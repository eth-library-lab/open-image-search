# Generated by Django 3.1.2 on 2021-04-26 10:47

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImageMetadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_id', models.IntegerField()),
                ('created_date', models.DateTimeField(auto_now=True, verbose_name='db_created_date')),
                ('title', models.CharField(blank=True, max_length=300, null=True)),
                ('image_url', models.URLField(max_length=300)),
                ('record_url', models.URLField(max_length=300)),
                ('inventory_number', models.CharField(blank=True, max_length=50, null=True)),
                ('person', models.CharField(blank=True, max_length=1500, null=True, verbose_name='artist who produced work')),
                ('date', models.CharField(blank=True, max_length=200, null=True, verbose_name='date of the work')),
                ('classification', models.CharField(blank=True, max_length=200, null=True, verbose_name='type of work')),
                ('material_technique', models.CharField(blank=True, max_length=200, null=True, verbose_name='techniques used')),
                ('institution_isil', models.CharField(blank=True, max_length=50, null=True, verbose_name='credit line')),
                ('image_licence', models.CharField(blank=True, max_length=50, null=True, verbose_name='image licence')),
            ],
        ),
        migrations.CreateModel(
            name='SearchResult',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_date', models.DateTimeField(auto_now=True, verbose_name='db_created_date')),
                ('keep', models.BooleanField(default=False, verbose_name='user has requested to save this link')),
                ('results', models.JSONField(verbose_name='ids of images returned to the user')),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploaded_images', verbose_name='uploaded image')),
            ],
        ),
    ]
