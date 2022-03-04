from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.contrib.postgres.fields import ArrayField

class Person(models.Model):
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField("db_created_date", auto_now=True)

    def __str__(self):
        return self.name


class Classification(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    
    def __str__(self):
        return self.name


class MaterialTechnique(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_date = models.DateTimeField("db_created_date", auto_now=True)

    def __str__(self):
        return self.name


class Relationship(models.Model):
    name = models.CharField("name relationship type", max_length=100, unique=True)
    created_date = models.DateTimeField("db_created_date", auto_now=True)

    def __str__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField("credit line", max_length=100)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    ref_name = models.CharField("short reference name", unique=True, blank=False, null=False, max_length=5)

class ImageMetadata(models.Model):
    
    record_id = models.IntegerField("provider's original object id", blank=False, null=False)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    title = models.CharField(blank=True, null=True, max_length=300)
    image_url = models.URLField(blank=False, null=False, max_length=300)
    record_url = models.URLField(blank=False, null=False, max_length=300)
    inventory_number = models.CharField(blank=True, null=True, max_length=50)
    person = models.CharField("artist who produced work",blank=True, null=True, max_length=1500)
    person_id = models.ManyToManyField(Person)
    date = models.CharField("date of the work", blank=True, null=True, max_length=200)
    classification =  models.CharField("type of work", blank=True, null=True, max_length=200)
    classification_id = models.ForeignKey(Classification, blank=True,null=True, on_delete=models.SET_NULL)
    material_technique = models.CharField("techniques used", blank=True, null=True, max_length=200)
    material_technique_id = models.ManyToManyField(MaterialTechnique)
    institution_isil = models.CharField("credit line", blank=True, null=True, max_length=50)
    institution_isil_id = models.ForeignKey(Institution, blank=True, null=True, on_delete=models.SET_NULL) 
    image_licence = models.CharField("image licence", blank=True, null=True, max_length=50)
    year_min = models.IntegerField(blank=True, null=True, default=-1, validators=[MinValueValidator(-1), MaxValueValidator(9999)])
    year_max = models.IntegerField(blank=True, null=True, default=-1, validators=[MinValueValidator(-1), MaxValueValidator(9999)])
    relationship_type_id = models.ManyToManyField(Relationship)

class Image(models.Model):
    directory = models.CharField("local directory where image is saved", null=True, max_length=300)
    provider_filename = models.CharField("original filename", max_length=200)
    image_metadata_id = models.ForeignKey(ImageMetadata, null=True, blank=True, on_delete=models.SET_NULL)
    institution = models.ForeignKey(Institution, null=True, on_delete=models.SET_NULL)

    class Meta: 
        constraints = [models.UniqueConstraint(
                                fields=['provider_filename', 'institution'], 
                                name='unique_original_filename'),
                      ]


class SearchResult(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    keep = models.BooleanField("user has requested to save this link", default=False)
    results = models.JSONField("ids of images returned to the user")
    image = models.ImageField('uploaded image', upload_to='uploaded_images/tmp',blank=True, null=True)
    query_parameters = models.JSONField("a json representation of the query filter parameters",blank=True, null=True)

    def __str__(self):
        return f"{self.created_date}: {self.id} (keep:{self.keep})"


class FeatureModel(models.Model):
    name = models.CharField(max_length=200)
    created_date = models.DateTimeField("when the model was trained", auto_now=True)
    description = models.CharField(max_length=500)

class ImageFeature(models.Model):
    feature = ArrayField(base_field=models.FloatField()) # a flat array
    image_id = models.ForeignKey(Image,verbose_name="image that the features are from", on_delete=models.CASCADE, null=True, blank=True)
    model_id = models.ForeignKey(FeatureModel, verbose_name="model that created the vector", on_delete=models.CASCADE)

class ImageKeyPointDescriptor(models.Model):
    """
    similar to imageFeature table but used for keypoint-descriptor features created
    by algorithms like SIFT
    """
    keyp_des = models.JSONField("dict of keypoints and descriptors in the image")
    image_id = models.ForeignKey(Image,verbose_name="image that the features are from", on_delete=models.CASCADE, null=True, blank=True)
    model_id = models.ForeignKey(FeatureModel, verbose_name="model that created the vector", on_delete=models.CASCADE)