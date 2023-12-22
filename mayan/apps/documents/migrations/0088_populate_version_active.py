from django.db import migrations


def code_document_version_active_populate(apps, schema_editor):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    for document in Document.objects.all():
        document.version_active = document.versions.filter(active=True).only('id').first()
        document.save(
            update_fields=('version_active',)
        )


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0087_document_version_active')
    ]

    operations = [
        migrations.RunPython(
            code=code_document_version_active_populate,
            reverse_code=migrations.RunPython.noop
        )
    ]
