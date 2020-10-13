from rest_framework import serializers

from ImageSearch.models import ImageMetadata

class ImageMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = '__all__'