from django.utils.safestring import mark_safe


def document_link(document):
    return mark_safe(
        s='<a href="{}">{}</a>'.format(
            document.get_absolute_url(), document
        )
    )
