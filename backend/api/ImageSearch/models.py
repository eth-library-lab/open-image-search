from django.db import models
import uuid

# Create your models here.

class ImageMetadata(models.Model):
    
    record_id = models.IntegerField(blank=False, null=False)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    title = models.CharField(blank=True, null=True, max_length=300)
    image_url = models.URLField(blank=False, null=False, max_length=300)
    record_url = models.URLField(blank=False, null=False, max_length=300)
    inventory_number = models.CharField(blank=True, null=True, max_length=50)
    person = models.CharField("artist who produced work",blank=True, null=True, max_length=1500)
    date = models.CharField("date of the work", blank=True, null=True, max_length=200)
    classification =  models.CharField("type of work", blank=True, null=True, max_length=200)
    material_technique = models.CharField("techniques used", blank=True, null=True, max_length=200)
    institution_isil = models.CharField("credit line", blank=True, null=True, max_length=50)
    image_licence = models.CharField("image licence", blank=True, null=True, max_length=50)


class SearchResult(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    keep = models.BooleanField("user has requested to save this link", default=False)
    data = models.JSONField()
    image = models.ImageField('uploaded image', upload_to='uploaded_images',blank=True, null=True)

    def __str__(self):
        return f"{self.created_date}: {self.id} (keep:{self.keep})"