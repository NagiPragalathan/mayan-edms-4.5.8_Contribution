from mayan.apps.sources.tests.source_backend_actions import (
    SourceBackendActionDocumentUploadBasic
)

from ..source_backend_actions.mixins import SourceBackendActionMixinCompressedInteractive


class SourceBackendActionDocumentUploadBasicCompressed(
    SourceBackendActionMixinCompressedInteractive,
    SourceBackendActionDocumentUploadBasic
):
    """
    Minimal action for the test source.
    """
