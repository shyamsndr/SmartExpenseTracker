# Generated by Django 5.1.6 on 2025-03-01 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_sourceofincome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sourceofincome',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name='sourceofincome',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_user_source'),
        ),
    ]
