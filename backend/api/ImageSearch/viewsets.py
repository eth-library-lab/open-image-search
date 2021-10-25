import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Max, Min
import numpy as np
import os
import logging

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
from ImageSearch.retrieval import retrieve_top_ids
from ImageSearch.model_filters import combine_filters


def get_ids_from_model_response(model_response):
    

    model_response_dict = json.loads(model_response.text)

    if DEBUG:
        scores = model_response_dict["predictions"][0]["output_1"]

    _ids = model_response_dict["predictions"][0]["output_2"]

    return _ids


# for loop could be replaced with qry_set.filter(record_id__in=object_ids)
def get_metadata_for_list_of_ids(_ids):

    qry_set = ImageMetadata.objects.all()
    results_metadata = []

    for obj_id in _ids:
        metadata = qry_set.filter(id=obj_id).values().first()
        results_metadata.append(metadata)

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
def get_num_ids_remaining(request):
    """
    get a count of how many records are left after applying filters
    """
    
    qry_params = request.query_params

    total_num_records = ImageMetadata.objects.all().count()    

    ids_to_exclude = combine_filters(**qry_params)
    num_to_exclude = len(ids_to_exclude)

    num_remaining = total_num_records - num_to_exclude

    resp_data = {"idsToExclude": ids_to_exclude,
                "num_records":num_remaining,
                }
    
    return Response(resp_data)


@api_view(['GET',])
def get_ids_to_exclude(request):
    """
    
    """
    qry_params = request.query_params
    
    total_num_records = ImageMetadata.objects.all().count()
    ids_to_exclude = combine_filters(**qry_params)
    num_to_exclude = len(ids_to_exclude)
    num_remaining = total_num_records - num_to_exclude
    resp_data = {
                "idsToExclude": ids_to_exclude,
                "num_records":num_remaining,
                }
    
    return Response(resp_data)


@api_view(['POST',])
def save_search_result(request):

        serializer = SaveSearchResultSerializer(data=request.data)

        if serializer.is_valid():
            
            if serializer.validated_data['keep'] == True:
                
                pk = str(request.data['id'])
                try:
                    search_record = SearchResult.objects.get(pk=pk)

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


def lookup_metadata_from_ids(_ids):


    metadata = []
    qry_set = ImageMetadata.objects.all()
    
    for _id in _ids:
        record_metadata = qry_set.filter(id=_id).values()
        if len(record_metadata)>0:        
            metadata.append(record_metadata[0])

    return metadata


def create_search_result_record(record_ids, uploaded_image, request):

    search_result_list = np.array(record_ids,'int32').tolist()
    search_result_id=None
    try:
        search_result = SearchResult.objects.create(
            keep=False, # set to false unless user requests a shareable link
            results=search_result_list,
            image=uploaded_image,
            query_parameters=request.query_params)
        search_result_id = search_result.id

    except PermissionError as pe:
        print("could not write file: ", pe)
        
    return search_result.id


@api_view(['POST',])
def image_search(request):
    """
    post an image and return a list of most similar images in the database
    """

    if DEBUG:
        txt = f"request received: {str(request)}"
        logging.info(txt)
        print(txt)

    if request.method == 'POST':

        serializer = ImageSearchSerializer(data=request.data)
        serializer_is_valid = serializer.is_valid()

        if DEBUG:
            print("serializer.errors: ", serializer.errors)

        if serializer_is_valid:
            ### read image ###
            img_stream = request.data['image'].open()
            
            if DEBUG:
                print("request.query_params: ", request.query_params)
            ### send image and query params to model ###
            model_response = retrieve_top_ids(img_stream,
                                              request.query_params)
            ### handle model response ###
            if model_response.status_code != 200:
                return Response(model_response.text, status=status.HTTP_400_BAD_REQUEST)           

            _ids = get_ids_from_model_response(model_response)
            results_metadata = get_metadata_for_list_of_ids(_ids)           

            ### Save Result ### to reproduce results if needed (e.g. for shareable link)
            search_result_id = create_search_result_record(_ids, img_stream, request)

            ### Format & Return Response ###
            total_num_records = ImageMetadata.objects.all().count()
            result = {
                'results':results_metadata,
                'resultId':search_result_id,
                'numPossibleResults':total_num_records,
                }

            return Response(result, status=200)

        else:
            print("error with serializer")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)