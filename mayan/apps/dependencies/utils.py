from xmlrpc import client

import mayan

from .exceptions import DependenciesException
from .literals import (
    MAYAN_PYPI_NAME, MESSAGE_GREATER_THAN_SERVER, MESSAGE_NOT_LATEST,
    MESSAGE_UNKNOWN_VERSION, MESSAGE_UNEXPECTED_ERROR, MESSAGE_UP_TO_DATE,
    PYPI_URL
)
from .versions import Version


class PyPIClient:
    class ExceptionAheadOfUpstream(DependenciesException):
        """
        The installed version is more recent than the upstream version.
        """
        def __init__(self, version_local, version_server):
            self.version_local = version_local
            self.version_server = version_server
            self.message = MESSAGE_GREATER_THAN_SERVER % {
                'version_local': self.version_local,
                'version_server': self.version_server
            }

            super().__init__(self.message)

    class ExceptionNotLatestVersion(DependenciesException):
        """
        The installed version is not the latest available version.
        """
        def __init__(self, version_local, version_server):
            self.version_local = version_local
            self.version_server = version_server
            self.message = MESSAGE_NOT_LATEST % {
                'version_local': self.version_local,
                'version_server': self.version_server
            }

            super().__init__(self.message)

    class ExceptionUnknownLatestVersion(DependenciesException):
        """
        It is not possible to determine what is the latest upstream version.
        """
        def __init__(self):
            self.message = MESSAGE_UNKNOWN_VERSION

            super().__init__(self.message)

    def __init__(self):
        self.version_local = Version(version_string=mayan.__version__)

    def check_version(self):
        versions = self.get_server_versions()
        if not versions:
            raise PyPIClient.ExceptionUnknownLatestVersion
        else:
            version_local = Version(version_string=mayan.__version__)
            version_server = Version(version_string=versions[0])

            if version_local > version_server:
                raise PyPIClient.ExceptionAheadOfUpstream(
                    version_local=mayan.__version__,
                    version_server=versions[0]
                )
            elif version_local < version_server:
                raise PyPIClient.ExceptionNotLatestVersion(
                    version_local=mayan.__version__,
                    version_server=versions[0]
                )

    def check_version_verbose(self):
        try:
            self.check_version()
        except PyPIClient.ExceptionAheadOfUpstream as exception:
            message = str(exception)
        except PyPIClient.ExceptionNotLatestVersion as exception:
            message = str(exception)
        except PyPIClient.ExceptionUnknownLatestVersion as exception:
            message = str(exception)
        except Exception as exception:
            message = MESSAGE_UNEXPECTED_ERROR % {'exception': exception}
        else:
            message = MESSAGE_UP_TO_DATE % {
                'version_local': mayan.__version__
            }

        return message

    def get_server_proxy(self):
        return client.ServerProxy(uri=PYPI_URL)

    def get_server_versions(self):
        server_proxy = self.get_server_proxy()
        return server_proxy.package_releases(MAYAN_PYPI_NAME)
