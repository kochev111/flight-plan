# Generated by Django 4.2.4 on 2023-08-25 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='landing_dir',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='plan',
            name='pattern',
            field=models.ImageField(upload_to='plans'),
        ),
    ]
