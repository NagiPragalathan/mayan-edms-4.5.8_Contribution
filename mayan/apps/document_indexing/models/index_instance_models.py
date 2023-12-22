from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from mayan.apps.documents.models.document_models import Document

from ..managers import (
    DocumentIndexInstanceNodeManager, IndexInstanceManager
)

from .index_template_models import IndexTemplate, IndexTemplateNode
from .index_instance_model_mixins import (
    IndexInstanceBusinessLogicMixin, IndexInstanceNodeBusinessLogicMixin
)


class IndexInstance(IndexInstanceBusinessLogicMixin, IndexTemplate):
    """
    Model that represents an evaluated index. This is an index whose nodes
    have been evaluated against a series of documents. If is a proxy model
    at the moment.
    """
    objects = IndexInstanceManager()

    class Meta:
        proxy = True
        verbose_name = _('Index instance')
        verbose_name_plural = _('Index instances')

    def get_absolute_url(self):
        try:
            index_instance_root_node = self.index_instance_root_node
        except IndexInstanceNode.DoesNotExist:
            return '#'
        else:
            return reverse(
                viewname='indexing:index_instance_node_view', kwargs={
                    'index_instance_node_id': index_instance_root_node.pk
                }
            )


class IndexInstanceNode(IndexInstanceNodeBusinessLogicMixin, MPTTModel):
    """
    This model represent one instance node from a index template node. That is
    a node template that has been evaluated against a document and the result
    from that evaluation is this node's stored values. Instances of this
    model also point to the original node template.
    """
    parent = TreeForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        related_name='children', to='self'
    )
    index_template_node = models.ForeignKey(
        on_delete=models.CASCADE, related_name='index_instance_nodes',
        to=IndexTemplateNode, verbose_name=_('Index template node')
    )
    value = models.CharField(
        blank=True, db_index=True, max_length=255, verbose_name=_('Value')
    )
    documents = models.ManyToManyField(
        related_name='index_instance_nodes', to=Document,
        verbose_name=_('Documents')
    )

    class Meta:
        ordering = ('value',)
        unique_together = ('index_template_node', 'parent', 'value')
        verbose_name = _('Index instance node')
        verbose_name_plural = _('Indexes instances node')

    def __str__(self):
        return self.value

    def get_absolute_url(self):
        return reverse(
            viewname='indexing:index_instance_node_view', kwargs={
                'index_instance_node_id': self.pk
            }
        )


class DocumentIndexInstanceNode(IndexInstanceNode):
    """
    Proxy model of node instance. It is used to represent the node instance
    in which a document is currently located. It is used to aid in column
    registration. The inherited methods of this model should not be used.
    """
    objects = DocumentIndexInstanceNodeManager()

    class Meta:
        proxy = True
        verbose_name = _('Document index node instance')
        verbose_name_plural = _('Document indexes node instances')


class IndexInstanceNodeSearchResult(IndexInstanceNode):
    class Meta:
        proxy = True
        verbose_name = _('Index instance node')
        verbose_name_plural = _('Index instance nodes')
