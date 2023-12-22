import shlex

from django.apps import apps

from mayan.apps.templating.classes import Template

from .classes import MetadataLookup


class DocumentMetadataBusinessLogicMixin:
    @property
    def is_required(self):
        """
        Return a boolean value of True of this metadata instance's parent
        type is required for the stored document type.
        """
        return self.metadata_type.get_required_for(
            document_type=self.document.document_type
        )


class MetadataTypeBusinessLogicMixin:
    @staticmethod
    def comma_splitter(string):
        splitter = shlex.shlex(string, posix=True)
        splitter.whitespace = ','
        splitter.whitespace_split = True
        splitter.commenters = ''
        return [
            str(e) for e in splitter
        ]

    def get_default_value(self):
        template = Template(template_string=self.default)
        return template.render()

    def get_lookup_values(self):
        MetadataType = apps.get_model(
            app_label='metadata', model_name='MetadataType'
        )

        template = Template(template_string=self.lookup)
        return MetadataType.comma_splitter(
            template.render(
                context=MetadataLookup.get_as_context()
            )
        )

    def get_required_for(self, document_type):
        """
        Determine if the metadata type is required for the
        specified document type.
        """
        return document_type.metadata.filter(
            required=True, metadata_type=self
        ).exists()
