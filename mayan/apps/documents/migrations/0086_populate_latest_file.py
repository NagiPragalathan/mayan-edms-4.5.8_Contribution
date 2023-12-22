from django.db import migrations


def code_document_latest_file_populate(apps, schema_editor):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    for document in Document.objects.all():
        document.file_latest = document.files.order_by('timestamp').only('id').last()
        document.save(
            update_fields=('file_latest',)
        )


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0085_document_file_latest')
    ]

    operations = [
        migrations.RunPython(
            code=code_document_latest_file_populate,
            reverse_code=migrations.RunPython.noop
        )
    ]
