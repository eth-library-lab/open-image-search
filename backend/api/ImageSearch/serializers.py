from rest_framework import serializers

from ImageSearch.models import ImageMetadata

class ImageMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = '__all__'


class ImageSearchSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    image = serializers.ImageField()


class ImageSearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = ['id', 
                  'object_id',
                  'title',
                  'image_url',
                  'detail_url',
                  'description']

