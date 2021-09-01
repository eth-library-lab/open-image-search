from rest_framework import serializers

from ImageSearch.models import ImageMetadata, SearchResult, Classification, MaterialTechnique, Relationship, Institution

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

class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = '__all__'

class MaterialTechniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialTechnique
        fields = '__all__'

class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = '__all__'

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'
