# Generated by Django 3.2.23 on 2024-01-03 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0090_alter_documentversion_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('summary', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
