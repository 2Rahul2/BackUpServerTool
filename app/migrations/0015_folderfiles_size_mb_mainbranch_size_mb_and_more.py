# Generated by Django 4.2.7 on 2023-12-08 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_alter_mainbranch_dateinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='folderfiles',
            name='size_mb',
            field=models.DecimalField(decimal_places=6, max_digits=100, null=True),
        ),
        migrations.AddField(
            model_name='mainbranch',
            name='size_mb',
            field=models.DecimalField(decimal_places=6, max_digits=100, null=True),
        ),
        migrations.AddField(
            model_name='subfolder',
            name='size_mb',
            field=models.DecimalField(decimal_places=6, max_digits=100, null=True),
        ),
    ]
