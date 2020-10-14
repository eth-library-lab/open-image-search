from django.db import models

# Create your models here.

class ImageMetadata(models.Model):
    
    object_id = models.IntegerField(blank=False, null=False)
    created_date = models.DateTimeField(auto_now=True)
    title = models.CharField(blank=True, null=True, max_length=200)
    image_url = models.URLField(blank=False, null=False, max_length=200)
    detail_url = models.URLField(blank=False, null=False, max_length=200)
    detail_description = models.CharField(blank=True, null=True, max_length=200)