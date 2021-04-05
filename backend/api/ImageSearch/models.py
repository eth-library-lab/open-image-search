from django.db import models

# Create your models here.

class ImageMetadata(models.Model):
    
    record_id = models.IntegerField(blank=False, null=False)
    created_date = models.DateTimeField("db_created_date",auto_now=True)
    title = models.CharField(blank=True, null=True, max_length=200)
    image_url = models.URLField(blank=False, null=False, max_length=200)
    record_url = models.URLField(blank=False, null=False, max_length=200)
    inventory_number = models.CharField(blank=True, null=True, max_length=50)
    person = models.CharField("artist who produced work",blank=True, null=True, max_length=200)
    date = models.CharField("data of the work", blank=True, null=True, max_length=200)
    classification =  models.CharField("type of work", blank=True, null=True, max_length=200)
    material_technique = models.CharField("techniques used", blank=True, null=True, max_length=200)
    institution_isil = models.CharField("credit line", blank=True, null=True, max_length=50)
    image_licence = models.CharField("image licence", blank=True, null=True, max_length=50)