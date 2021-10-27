# Generated by Django 3.1.2 on 2021-08-31 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ImageSearch', '0005_auto_20210831_1753'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagemetadata',
            name='classification_id',
        ),
        migrations.AddField(
            model_name='imagemetadata',
            name='classification_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ImageSearch.classification'),
        ),
    ]
