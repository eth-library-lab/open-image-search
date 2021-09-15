import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Max, Min
import numpy as np
import os

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view 
from rest_framework.permissions import IsAdminUser

from settings.settings import DEBUG, MEDIA_ROOT
from settings.custom_permissions import IsAdminUserOrReadOnly
from ImageSearch.models import ImageMetadata, SearchResult, Classification, MaterialTechnique, Relationship, Institution
from ImageSearch.serializers import ImageMetadataSerializer
from ImageSearch.serializers import ImageSearchSerializer, ImageSearchResultSerializer, SearchResultSerializer, SaveSearchResultSerializer
from ImageSearch.serializers import ClassificationSerializer, MaterialTechniqueSerializer, RelationshipSerializer, InstitutionSerializer
from ImageSearch.feature_extraction import request_top_ids
from ImageSearch.retrieval import knearest_ids, model_to_record_ids,record_to_model_ids, top_k_with_exclusions
from ImageSearch.retrieval_filters import combine_filters

# for loop could be replaced with qry_set.filter(record_id__in=object_ids)
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
    permission_classes = [IsAdminUserOrReadOnly, ]
    
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


@api_view(['GET',])
def get_filter_options(request):
    """return all the possible filter fields in one get request"""
    class_serializer = ClassificationSerializer(Classification.objects.all(), many=True)
    mat_serializer = MaterialTechniqueSerializer(MaterialTechnique.objects.all(), many=True)
    rel_serializer = RelationshipSerializer(Relationship.objects.all(), many=True)
    inst_serializer = InstitutionSerializer(Institution.objects.all(), many=True)

    year_qs = ImageMetadata.objects.exclude(year_min=-1).only('year_min','year_max')

    years_min = year_qs.aggregate(Min('year_min'))
    years_max = year_qs.aggregate(Max('year_max'))

    resp_data = {
    "classifications" : class_serializer.data,
    "materialTechniques" : mat_serializer.data,
    "relationships" : rel_serializer.data,
    "institutions" : inst_serializer.data,
    "yearMin": years_min["year_min__min"],
    "yearMax": years_max["year_max__max"]

    }

    return Response(resp_data)


@api_view(['GET',])
def get_ids_to_exclude(request):
    """
    
    """
    
    print("request.query_params: ", request.query_params)
    qry_params = request.query_params

    ids_to_exclude = combine_filters(**qry_params)
    resp_data = {"idsToExclude": ids_to_exclude
                }
    
    return Response(resp_data)


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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def lookup_metadata_from_records_ids(record_ids):

    qry_set = ImageMetadata.objects.all()
    if DEBUG:
        print("qry_set len: ", len(qry_set.values()))
    
    metadata = []
    
    for record_id in record_ids:
        metadata.append(qry_set.filter(record_id=record_id).values()[0])

    if DEBUG:
        print("results_metadata: ", metadata)

    return metadata


def save_search_result(record_ids, uploaded_image, request):

    search_result_list = np.array(record_ids,'int32').tolist()
    search_result_id=None
    try:
        search_result = SearchResult.objects.create(
            keep=False, # set to false unless user requests a shareable link
            results=search_result_list,
            image=uploaded_image,
            query_parameters=request.query_params)
        search_result_id = search_result.id

        if DEBUG:
            print('\nsearch_result: ', search_result, '\n\n')

    except PermissionError as pe:
        print("could not write file: ", pe)
        
    return search_result.id


@api_view(['POST',])
def image_search(request):
    """
    post an image and return a list of most similar images in the database
    """

    if request.method == 'POST':

        serializer = ImageSearchSerializer(data=request.data)
        serializer_is_valid = serializer.is_valid()

        if DEBUG:
            print("serializer.errors: ", serializer.errors)

        if serializer_is_valid:
            ### read image ###
            img_stream = request.data['image'].open()

            ### get query params ###
            if DEBUG:
                print("request.query_params: ",request.query_params)
            
            qry_params = request.query_params
            records_to_exclude=None

            if len(qry_params)>0:
                records_to_exclude = combine_filters(**qry_params)

            ### Get Nearest Neighbour Ids ###

            if records_to_exclude:
                # post to retrieval_exclusion                
                model_response = request_top_ids(img_stream, ids_to_exclude=records_to_exclude, k=10)

            else:
                # post to retrieval
                model_response = request_top_ids(img_stream)

            ### handle model response ###
            if DEBUG:
                print('model_response: ', model_response.status_code)

            if model_response.status_code != 200:
                return Response(model_response.content, model_response.status_code)

            model_response_dict = json.loads(model_response.text)

            if DEBUG:
                print('model_response_dict', model_response_dict)

            model_values = model_response_dict['predictions'][0]
            top_records = np.array(model_values).reshape(1, -1) # reshape for a single record        
            top_records = top_records.reshape(1, -1)

            ### lookup Metadata ###
            results_metadata = lookup_metadata_from_records_ids(top_records)

            ### Save Result to reproduce results if needed (e.g. for shareable link) ###
            search_result_id = save_search_result(record_ids, uploaded_image, request)

            ### format response ###
            result = {
                'results':results_metadata,
                'result_id':search_result_id
                }

            if DEBUG:
                print('\napi response: ', result, '\n\n')

            return Response(result, status=200)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)