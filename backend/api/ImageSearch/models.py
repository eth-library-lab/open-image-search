from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.contrib.postgres.fields import ArrayField


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
    name = models.CharField("credit line i.e.: long-form insitution name", max_length=100, unique=True)
    isil_id = models.CharField("isil identifier, e.g. CH-000511-9", max_length=12, unique=True)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    ref_name = models.CharField("short reference name", unique=True, blank=False, null=False, max_length=5)


class ImageMetadata(models.Model):
    """mainly unedited/extracted text based metadata for images"""
    institution_id = models.ForeignKey(Institution, db_column="institution_id", blank=True, null=True, on_delete=models.SET_NULL)
    record_name = models.CharField("provider's original object id", max_length=200, blank=False, null=False)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    title = models.CharField(blank=True, null=True, max_length=300)
    image_url = models.URLField(blank=False, null=False, max_length=300)
    record_url = models.URLField(blank=False, null=False, max_length=300)
    inventory_number = models.CharField(blank=True, null=True, max_length=50)
    image_licence = models.CharField("image licence", blank=True, null=True, max_length=50)
    person = models.CharField("artist who produced work", blank=True, null=True, max_length=1500)
    date = models.CharField("date of the work", blank=True, null=True, max_length=200)
    classification = models.CharField("type of work", blank=True, null=True, max_length=500)
    material_technique = models.CharField("techniques used", blank=True, null=True, max_length=500)
    relationship = models.CharField("relationships assosciated with this work", blank=True, null=True, max_length=500)
    
    class Meta:
        constraints = [models.UniqueConstraint(
                                fields=['institution_id', 'record_name'],
                                name='unique record'),]


class Image(models.Model):
    directory = models.CharField("local directory where image is saved", null=True, max_length=300)
    provider_filename = models.CharField("original filename", max_length=200)
    institution_id = models.ForeignKey(Institution, blank=True, null=True, on_delete=models.SET_NULL)
    image_metadata_id = models.ForeignKey(ImageMetadata, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta: 
        constraints = [models.UniqueConstraint(
                                fields=['provider_filename', 'institution_id'],
                                name='unique_original_filename'),]


class ImageMetadataFeatures(models.Model):
    
    image_metadata_id = models.ForeignKey(ImageMetadata, db_column="image_metadata_id", on_delete=models.CASCADE)
    created_date = models.DateTimeField("db_created_date", auto_now=True)
    year_min = models.IntegerField(blank=True, null=True, default=-1, validators=[MinValueValidator(-1), MaxValueValidator(9999)])
    year_max = models.IntegerField(blank=True, null=True, default=-1, validators=[MinValueValidator(-1), MaxValueValidator(9999)])
    classification_id = models.ManyToManyField(Classification)
    material_technique_tag = models.ManyToManyField(MaterialTechnique)
    relationship_id = models.ManyToManyField(Relationship)


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