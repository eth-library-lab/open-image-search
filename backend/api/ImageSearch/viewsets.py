from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view 

from settings.settings import DEBUG
from ImageSearch.models import ImageMetadata, SearchResult
from ImageSearch.serializers import ImageMetadataSerializer
from ImageSearch.serializers import ImageSearchSerializer, ImageSearchResultSerializer, SearchResultSerializer
from ImageSearch.feature_extraction import get_nearest_object_ids

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

class SearchResultViewset(viewsets.ModelViewSet):

    """
    list:
    Returns a list of all search results
    
    retrieve:
    Return results for a specific search.

    create: 
    save a new record for a search
    (this will be done server side)

    update:
    (n/a)
    change some of the fields for a specific search
    """    

    queryset = SearchResult.objects.all()
    serializer_class = SearchResultSerializer


@api_view(['POST',])
def image_search(request):
    """
    post an image and return a list of most similar images in the database
    """

    if request.method == 'POST':

        serializer = ImageSearchSerializer(data=request.data)

        if serializer.is_valid():
            # TO DO
            # function to get object_ids of most similar images

            img_stream = request.data['image'].open()
            print('at img_stream: ', img_stream)
            object_ids = get_nearest_object_ids(img_stream) # [3,18,19,33,52,236, 308,312,313, 324]
            qry_set = ImageMetadata.objects.all()
            results_metadata = []

            for obj_id in object_ids:
                results_metadata.append(qry_set.filter(record_id=obj_id).values()[0])

            # resp_serializer = ImageSearchResultSerializer(results_metadata, many=True)
            
            if DEBUG:
                print('\napi response: ', results_metadata, '\n\n')

            return Response(results_metadata, status=200)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)