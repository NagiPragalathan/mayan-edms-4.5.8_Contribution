import yaml

from django.template import Library
from django.utils.html import mark_safe

import mayan
from mayan.apps.dependencies.versions import Version

register = Library()


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


def yaml_dump(data, indent):
    result = yaml.dump(
        Dumper=Dumper, data=data, width=1000
    )

    result = result.replace('\'\'\'', '\'')

    output = []

    for line in result.split('\n'):
        if line:
            output.append(
                '{}{}'.format(
                    ' ' * indent, line
                )
            )

    return mark_safe(
        '\n'.join(output)
    )


@register.simple_tag
def platform_gitlab_ci_cache_before_script(indent, apk=False, apt=False):
    data = []

    if apk:
        data.extend(
            [
                'mkdir --parents ${APK_CACHE_DIR}',
                'apk update'
            ]
        )

    if apt:
        data.extend(
            [
                'export APT_STATE_LISTS=${APT_CACHE_DIR}/lists && export APT_CACHE_ARCHIVES=${APT_CACHE_DIR}/archives',
                'mkdir --parents "${APT_STATE_LISTS}/partial" && mkdir --parents "${APT_CACHE_ARCHIVES}/partial"',
                'printf "dir::state::lists    ${APT_STATE_LISTS};\\ndir::cache::archives    ${APT_CACHE_ARCHIVES};\\n" > /etc/apt/apt.conf.d/99gitlab-ci-cache',
                'if [ "${APT_PROXY}" ]; then echo "Acquire::http { Proxy \\"http://${APT_PROXY}\\"; };" > /etc/apt/apt.conf.d/01proxy; fi',
                'apt-get update'
            ]
        )

    return yaml_dump(data=data, indent=indent)


@register.simple_tag
def platform_gitlab_ci_cache_paths(indent, apk=False, apt=False, pip=False):
    cache_list = []

    version = Version(version_string=mayan.__version__)

    if apk:
        cache_list.append(
            {
                'key': 'apk-cache-{}'.format(
                    version.as_minor()
                ),
                'paths': ['${APK_CACHE_DIR}']
            }
        )

    if apt:
        cache_list.append(
            {
                'key': 'apt-cache-{}'.format(
                    version.as_minor()
                ),
                'paths': ['${APT_CACHE_DIR}']
            }
        )

    if pip:
        cache_list.append(
            {
                'key': 'pip-cache-{}'.format(
                    version.as_minor()
                ),
                'paths': ['${PIP_CACHE_DIR}']
            }
        )

    return yaml_dump(data=cache_list, indent=indent)


@register.simple_tag
def platform_gitlab_ci_cache_variables(
    indent, apk=False, apt=False, pip=False
):
    variables = {}

    if apk:
        variables['APK_CACHE_DIR'] = '${CI_PROJECT_DIR}/.cache/apk'

    if apt:
        variables['APT_CACHE_DIR'] = '${CI_PROJECT_DIR}/.cache/apt'

    if pip:
        variables['PIP_CACHE_DIR'] = '${CI_PROJECT_DIR}/.cache/pip'

    return yaml_dump(data=variables, indent=indent)


@register.simple_tag
def platform_gitlab_ci_config_env_before_script(indent):
    data = ['set -a && . ./config.env && set +a']

    return yaml_dump(data=data, indent=indent)


@register.simple_tag
def platform_gitlab_ci_ssh_before_script(indent, hostname, private_key):
    data = [
        'mkdir --parents ~/.ssh',
        'chmod 700 ~/.ssh',
        'echo "{}" > ~/.ssh/known_hosts'.format(hostname),
        'chmod 644 ~/.ssh/known_hosts',
        '\'which ssh-agent || ( apt-get update --yes && apt-get install --yes --no-install-recommends openssh-client rsync )\'',
        'eval $(ssh-agent -s)',
        'echo "{}" | tr -d \'\\r\' | ssh-add - > /dev/null'.format(private_key)
    ]

    return yaml_dump(data=data, indent=indent)
