# Generated by Django 5.1.3 on 2025-02-28 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_app', '0003_extractedtext'),
    ]

    operations = [
        migrations.AddField(
            model_name='extractedtext',
            name='qna_gcs_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='extractedtext',
            name='quiz_gcs_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
