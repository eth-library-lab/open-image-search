from rest_framework import serializers

from ImageSearch.models import ImageMetadata, SearchResult

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


class SearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchResult
        fields = '__all__'

class SaveSearchResultSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    keep = serializers.BooleanField()
