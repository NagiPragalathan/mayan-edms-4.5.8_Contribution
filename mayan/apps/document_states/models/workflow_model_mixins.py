import hashlib
import logging

from furl import furl
from graphviz import Digraph

from django.apps import apps
from django.core import serializers
from django.db import IntegrityError
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from mayan.apps.file_caching.models import CachePartitionFile

from ..events import event_workflow_template_edited
from ..literals import (
    STORAGE_NAME_WORKFLOW_CACHE, SYMBOL_GRAPHVIZ_CONDITIONAL,
    WORKFLOW_ACTION_ON_ENTRY
)

logger = logging.getLogger(name=__name__)


class WorkflowBusinessLogicMixin:
    @cached_property
    def cache(self):
        Cache = apps.get_model(app_label='file_caching', model_name='Cache')

        return Cache.objects.get(
            defined_storage_name=STORAGE_NAME_WORKFLOW_CACHE
        )

    @cached_property
    def cache_partition(self):
        partition, created = self.cache.partitions.get_or_create(
            name='{}'.format(self.pk)
        )
        return partition

    def document_types_add(self, queryset, user):
        for model_instance in queryset.all():
            self.document_types.add(model_instance)
            event_workflow_template_edited.commit(
                action_object=model_instance, actor=user, target=self
            )

    def document_types_remove(self, queryset, user):
        for model_instance in queryset.all():
            self.document_types.remove(model_instance)
            event_workflow_template_edited.commit(
                action_object=model_instance, actor=user, target=self
            )
            self.instances.filter(
                document__document_type_id=model_instance.pk
            ).delete()

    def generate_image(
        self, maximum_layer_order=None, transformation_instance_list=None,
        user=None
    ):
        # `user` argument added for compatibility.
        cache_filename = '{}'.format(
            self.get_hash()
        )

        try:
            self.cache_partition.get_file(filename=cache_filename)
        except CachePartitionFile.DoesNotExist:
            logger.debug(
                'workflow cache file "%s" not found', cache_filename
            )

            image = self.render()
            with self.cache_partition.create_file(filename=cache_filename) as file_object:
                file_object.write(image)
        else:
            logger.debug(
                'workflow cache file "%s" found', cache_filename
            )

        return cache_filename

    def get_api_image_url(self, *args, **kwargs):
        final_url = furl()
        final_url.args = kwargs
        final_url.path = reverse(
            viewname='rest_api:workflow-template-image',
            kwargs={'workflow_template_id': self.pk}
        )
        final_url.args['_hash'] = self.get_hash()

        return final_url.tostr()

    def get_document_types_not_in_workflow(self):
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )

        return DocumentType.objects.exclude(
            pk__in=self.document_types.all()
        )

    def get_hash(self):
        result = hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        )
        for state in self.states.all():
            result.update(
                state.get_hash().encode()
            )

        for transition in self.transitions.all():
            result.update(
                transition.get_hash().encode()
            )

        return result.hexdigest()

    def get_initial_state(self):
        try:
            return self.states.get(initial=True)
        except self.states.model.DoesNotExist:
            return None
    get_initial_state.short_description = _('Initial state')

    def launch_for(self, document, user=None):
        if document.document_type in self.document_types.all():
            try:
                logger.info(
                    'Launching workflow %s for document %s', self, document
                )
                WorkflowInstance = apps.get_model(
                    app_label='document_states',
                    model_name='WorkflowInstance'
                )
                workflow_instance = WorkflowInstance(
                    document=document, workflow=self
                )
                workflow_instance._event_actor = user
                workflow_instance.save()

                initial_state = self.get_initial_state()
                if initial_state:
                    for action in initial_state.entry_actions.filter(enabled=True):
                        context = workflow_instance.get_context()
                        context.update(
                            {
                                'action': action
                            }
                        )
                        action.execute(
                            context=context,
                            workflow_instance=workflow_instance
                        )
            except IntegrityError:
                logger.info(
                    'Workflow %s already launched for document %s',
                    self, document
                )
            else:
                logger.info(
                    'Workflow %s launched for document %s', self, document
                )
                return workflow_instance
        else:
            logger.error(
                'This workflow is not valid for the document type of the '
                'document.'
            )

    def render(self):
        diagram = Digraph(
            name='finite_state_machine', graph_attr={
                'rankdir': 'LR', 'splines': 'polyline'
            }, format='png'
        )

        action_cache = {}
        escalation_cache = {}
        state_cache = {}
        transition_cache = []

        for state in self.states.all():
            state_cache[
                's{}'.format(state.pk)
            ] = {
                'connections': {'origin': 0, 'destination': 0},
                'initial': state.initial,
                'label': state.label,
                'name': 's{}'.format(state.pk)
            }

            for action in state.actions.all():
                if action.enabled:
                    if action.has_condition():
                        action_label = '{} {}'.format(
                            SYMBOL_GRAPHVIZ_CONDITIONAL, action.label
                        )
                    else:
                        action_label = action.label

                    action_cache[
                        'a{}'.format(action.pk)
                    ] = {
                        'label': action_label,
                        'name': 'a{}'.format(action.pk),
                        'state': 's{}'.format(state.pk),
                        'when': action.when
                    }

            for escalation in state.escalations.all():
                if escalation.enabled:
                    label = 'After {}'.format(
                        escalation.get_time_display()
                    )

                    if escalation.has_condition():
                        label = '{} {}'.format(
                            SYMBOL_GRAPHVIZ_CONDITIONAL, label
                        )

                    escalation_cache[
                        'e{}'.format(escalation.pk)
                    ] = {
                        'label': label,
                        'destination': 's{}'.format(escalation.transition.destination_state.pk),
                        'state': 's{}'.format(state.pk),
                    }

        for transition in self.transitions.all():
            if transition.has_condition():
                transition_label = '{} {}'.format(
                    SYMBOL_GRAPHVIZ_CONDITIONAL, transition.label
                )
            else:
                transition_label = transition.label

            transition_cache.append(
                {
                    'label': transition_label,
                    'head_name': 's{}'.format(
                        transition.destination_state.pk
                    ),
                    'tail_name': 's{}'.format(transition.origin_state.pk)
                }
            )

            state_cache[
                's{}'.format(transition.origin_state.pk)
            ]['connections']['origin'] = state_cache[
                's{}'.format(transition.origin_state.pk)
            ]['connections']['origin'] + 1

            state_cache[
                's{}'.format(transition.destination_state.pk)
            ]['connections']['destination'] += 1

        for key, value in state_cache.items():
            kwargs = {
                'fillcolor': '#eeeeee',
                'label': value['label'],
                'name': value['name'],
                'shape': 'doublecircle' if value['connections']['origin'] == 0 or value['connections']['destination'] == 0 or value['initial'] else 'circle',
                'style': 'filled' if value['initial'] else ''
            }
            diagram.node(**kwargs)

        for transition in transition_cache:
            diagram.edge(**transition)

        for key, value in action_cache.items():
            kwargs = {
                'label': value['label'],
                'name': value['name'],
                'shape': 'box'
            }
            diagram.node(**kwargs)
            diagram.edge(
                **{
                    'arrowhead': 'dot',
                    'arrowtail': 'dot',
                    'dir': 'both',
                    'label': 'On entry' if value['when'] == WORKFLOW_ACTION_ON_ENTRY else 'On exit',
                    'head_name': '{}'.format(
                        value['name']
                    ),
                    'style': 'dashed',
                    'tail_name': '{}'.format(
                        value['state']
                    )
                }
            )

        for key, value in escalation_cache.items():
            diagram.edge(
                **{
                    'label': value['label'],
                    'head_name': '{}'.format(
                        value['destination']
                    ),
                    'style': 'dashed',
                    'tail_name': '{}'.format(
                        value['state']
                    ),
                }
            )

        return diagram.pipe()
