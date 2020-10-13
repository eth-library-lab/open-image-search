from rest_framework import viewsets

from ImageSearch.models import ImageMetadata
from ImageSearch.serializers import ImageMetadataSerializer

class ImageMetadataViewset(viewsets.ModelViewSet):

    """
    list:
    Returns a list of all image metadata in the database
    
    retrieve:
    Return metadata for a specific image.

    create:
    add metadata for a new image database.
    Images uploaded for image searches are not saved with this endpoint.

    update:
    change some of the fields for a specific image
    """    
    
    # permission_classes = [custom_permissions.IsAdminUserOrReadOnly]

    queryset = ImageMetadata.objects.all()
    serializer_class = ImageMetadataSerializer