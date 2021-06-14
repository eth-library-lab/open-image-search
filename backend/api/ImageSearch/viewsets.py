import json
from django.core.serializers.json import DjangoJSONEncoder
import numpy as np
import os

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view 
from rest_framework.permissions import IsAdminUser

from settings.settings import DEBUG, MEDIA_ROOT
from ImageSearch.models import ImageMetadata, SearchResult
from ImageSearch.serializers import ImageMetadataSerializer
from ImageSearch.serializers import ImageSearchSerializer, ImageSearchResultSerializer, SearchResultSerializer, SaveSearchResultSerializer
from ImageSearch.feature_extraction import get_nearest_object_ids


def getMetadataForListOfIds(object_ids):

    qry_set = ImageMetadata.objects.all()
    results_metadata = []

    for obj_id in object_ids:
        results_metadata.append(qry_set.filter(record_id=obj_id).values().first())

    return results_metadata


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
    
    permission_classes = [IsAdminUser, ]
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
    permission_classes = [IsAdminUser, ]
    
    queryset = SearchResult.objects.all()
    serializer_class = SearchResultSerializer

    def retrieve(self, request, *args, **kwargs):
        # do your customization here
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        resp = serializer.data
        #load metdata for list of ids        
        results = getMetadataForListOfIds(instance.results)        
        resp['results'] = results

        
        if DEBUG:
            print('serializer data: ', serializer.data)
            print('\napi response: ', resp, '\n\n')

        return Response(resp, status=200)




@api_view(['POST',])
def save_search_result(request):

        serializer = SaveSearchResultSerializer(data=request.data)

        if DEBUG: 
            print('in save_search_result')
            print('request.data: ', request.data)

        if serializer.is_valid():
            if DEBUG: 
                print("serializer.validated_data['keep']: ", serializer.validated_data['keep'])
            
            if serializer.validated_data['keep'] == True:
                
                print('serializer.validated_data: ', serializer.validated_data)

                pk = str(request.data['id'])

                print('pk: ', pk)
                try:
                    search_record = SearchResult.objects.get(pk=pk)
                    print('search_record: ', search_record)
                except SearchResult.DoesNotExist as e:
                    return Response("search record not found", status=status.HTTP_404_NOT_FOUND)
        
                search_record.keep = True
                
                try: 
                
                    orig_path = search_record.image.path
                    new_name = os.path.join('uploaded_images','saved', os.path.basename(search_record.image.name))
                    new_path = os.path.join(MEDIA_ROOT, new_name)
                    #move file to saved folder
                    saved_folder = os.path.dirname(new_path)

                    if not os.path.exists(saved_folder):
                        os.makedirs(saved_folder)

                    os.replace(orig_path, new_path)
                    search_record.image.name = new_name
                    search_record.save()                  

                except Exception as e:
                    print(e)

                # return updated data
                serializer = SearchResultSerializer(search_record)
                
                return Response(serializer.data)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

            uploaded_image = request.data['image']
            img_stream = uploaded_image.open()
            print('at img_stream: ', img_stream)
            object_ids = get_nearest_object_ids(img_stream) # [3,18,19,33,52,236, 308,312,313, 324]
            qry_set = ImageMetadata.objects.all()
            results_metadata = []

            for obj_id in object_ids:
                results_metadata.append(qry_set.filter(record_id=obj_id).values().first())

            # resp_serializer = ImageSearchResultSerializer(results_metadata, many=True)

            # save result to reproduce results if needed (e.g. for shareable link)
            # object_ids_json = json.dumps(object_ids, cls=DjangoJSONEncoder)

            search_result_list = np.array(object_ids,'int32').tolist()
            search_result = SearchResult.objects.create(
                keep=False, # set to false unless user requests a shareable link
                results=search_result_list,
                image=uploaded_image)

            if DEBUG:
                print('\nsearch_result: ', search_result, '\n\n')

            result = {
                'results':results_metadata,
                'result_id':search_result.id
                }

            if DEBUG:
                print('\napi response: ', result, '\n\n')

            return Response(result, status=200)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)