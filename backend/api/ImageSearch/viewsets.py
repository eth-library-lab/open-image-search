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
from ImageSearch.feature_extraction import calculate_image_features
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


@api_view(['POST',])
def image_search(request):
    """
    post an image and return a list of most similar images in the database
    """

    print(request)
    if request.method == 'POST':

        serializer = ImageSearchSerializer(data=request.data)
        serializer_is_valid = serializer.is_valid()

        if DEBUG:
            print("serializer.errors: ", serializer.errors)

        if serializer_is_valid:
            ### Calculate Features ###
            uploaded_image = request.data['image']
            img_stream = uploaded_image.open()
            image_features = calculate_image_features(img_stream) 
            # image_features = np.array([0.6872767, -0.49840045, 0.61399406, -0.49840045, 0.95047694, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.17474458, -0.49840045, -0.49840045, 1.1665395, -0.49840045, 1.402829, -0.49840045, -0.49840045, -0.49840045, -0.40339026, -0.49840045, -0.3345898, -0.49840045, -0.49840045, 1.4530649, 0.070052244, 0.59028745, -0.49840045, 0.24755163, -0.22891137, 0.30366623, 0.19757599, 0.35847113, -0.49840045, 0.1085733, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.59879994, -0.49840045, 0.053540573, 0.40487340000000005, 0.6992586999999999, -0.49840045, -0.49840045, 1.1900799, 0.40438979999999997, -0.11246126, 0.5662746, -0.49840045, -0.20479532, 1.9019622, 0.44386309999999995, 0.42961859999999996, 0.21663277, 0.6645059, -0.49840045, -0.49840045, -0.49840045, -0.36044872, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.28876397, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.6293297, 0.84790766, -0.3540868, -0.49840045, -0.49840045, -0.36397612, 1.1656666, -0.49840045, -0.49840045, -0.49840045, 1.038729, -0.49840045, -0.076539375, 1.542158, -0.49840045, -0.49840045, -0.13465598, -0.49840045, -0.49840045, 0.38510245, -0.49840045, -0.34741783, -0.49840045, 0.5053364, -0.33789125, 0.12158183, -0.29947314, 0.7122323, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.7047928000000001, 0.49657172, -0.34099236, -0.49840045, -0.3409478, 2.9849565, -0.49840045, -0.49840045, -0.49840045, 1.882575, 1.9773471000000002, 0.8745687, -0.49840045, -0.49840045, -0.49840045, 0.8110006999999999, 0.17683738, 0.30799437, -0.49840045, -0.49840045, -0.49840045, -0.25898993, -0.49840045, -0.49840045, -0.49840045, 0.050685953, -0.49840045, -0.49840045, 0.60790205, -0.49840045, 0.8192874, 3.4437417999999997, -0.49840045, -0.49840045, -0.49840045, 1.2166455, -0.49840045, -0.49840045, 0.24213186, -0.49840045, 1.1888173999999998, -0.16072837, 1.3163666, -0.49840045, 0.17368534, -0.49840045, -0.49840045, 14.117095, -0.2634261, 0.047061704, -0.49840045, 0.30538636, -0.49840045, -0.49840045, -0.49840045, -0.25054595, -0.49840045, -0.49840045, 0.7778799, -0.49840045, 0.29360765, -0.22128603, -0.25031117, -0.1597106, 0.82669353, 0.1214346, -0.28994313, 1.5306309999999999, -0.0038224056, -0.42002648, -0.49581670000000005, 0.107147194, -0.34934986, -0.49840045, -0.49840045, -0.49840045, 0.4093045, 0.32250500000000004, 3.069636, -0.050385997, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.17841446, -0.49840045, -0.045274086, -0.49840045, 0.49642079999999994, -0.49840045, -0.49840045, 0.09220914, -0.49840045, -0.49840045, -0.4839133, -0.49840045, -0.49840045, -0.49840045, -0.006071839, -0.24246503, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.29757893, -0.49840045, 0.8062416, -0.49840045, -0.37223622, -0.038166545, -0.49840045, -0.49840045, -0.49840045, -0.49645942, -0.09469575, -0.49840045, -0.08888416, 0.6898496000000001, 0.45627344, -0.49840045, 1.8745080000000003, -0.49840045, -0.39495555, 1.6924240000000002, -0.48426604, -0.38745582, -0.49840045, -0.49840045, 1.8955683999999997, -0.49840045, -0.49840045, -0.31196684, -0.37919673, -0.49840045, -0.49840045, 0.15384434, 1.4077903, -0.49673802, 0.89587414, 1.9627866999999999, 0.07323203, -0.14738907, -0.49840045, -0.49840045, -0.49840045, 1.5956333, 1.0662825, -0.02694709, -0.49840045, 0.32544506, 0.64544207, -0.49840045, 1.5608996000000002, -0.28660855, -0.49840045, -0.120414205, -0.49840045, -0.47778190000000004, -0.49840045, -0.49840045, 0.12080379, -0.49840045, -0.49840045, -0.042715337, -0.48482820000000004, -0.23157266, -0.49840045, 2.5297403, 0.7849495, -0.49840045, -0.10707865, -0.49840045, -0.49840045, -0.023777613, 0.23386733, -0.49840045, 0.22379468, -0.49840045, -0.49840045, -0.49840045, 0.62977004, 0.29801350000000004, 1.0138828000000002, 0.3370754, -0.43662024, 0.46774578, -0.49840045, 1.4202358, -0.49840045, 1.1711537, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.6637138000000001, -0.34126812, 1.4143956, -0.32729309999999995, -0.49840045, -0.49840045, -0.49840045, -0.36631897, 0.12826653, -0.49840045, 3.3451047, -0.064608485, 0.77502775, -0.34744936, 1.7420589, -0.056547057000000005, 0.30154547, -0.35329294, -0.49840045, -0.49840045, -0.49840045, 0.93002164, -0.49840045, 3.230025, -0.49840045, -0.49840045, -0.41696313, -0.49840045, -0.49840045, 0.12927394, 1.1237508, -0.49840045, -0.49840045, -0.13516416, -0.49840045, 0.2381013, 0.45513085, 0.520401, 1.3662579, -0.49840045, -0.49840045, 1.998256, 0.26588345, -0.49840045, -0.4409791, 0.08164225, -0.43750578, 3.0235426, -0.39291066, -0.49840045, -0.49840045, 0.68090206, -0.49840045, -0.49840045, 0.6477257, -0.49840045, -0.49840045, -0.49840045, -0.33964875, -0.49840045, 0.08746133, -0.49840045, -0.49840045, -0.49840045, 1.5620736000000002, -0.49840045, -0.4770316, 1.4514818, -0.49404734, -0.49840045, -0.031020755, -0.49840045, 0.5500710999999999, -0.49840045, -0.49840045, -0.49840045, 0.7183094, 0.6913097, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.62836975, -0.49840045, -0.49840045, 2.4937877999999998, -0.49840045, -0.32786018, -0.49840045, 0.07357337, -0.2762673, -0.3187103, -0.16678478, -0.49840045, -0.49840045, -0.49840045, -0.40621929999999995, -0.49840045, 0.18377525, -0.11551607400000001, 0.018740568, -0.49840045, -0.42300034, 0.5893215, -0.49840045, -0.49840045, -0.45010805, -0.49840045, -0.25902608, 0.39787802, -0.49840045, -0.21358775, 2.8035438, -0.49840045, -0.4341842000000001, -0.49840045, -0.49840045, -0.36352894, -0.49840045, -0.49840045, -0.45410436, -0.49840045, -0.49840045, -0.26024386, -0.49840045, -0.49840045, -0.49840045, -0.3045692, -0.49840045, -0.44297272, 0.41131666, -0.49840045, -0.49840045, 1.2943786, -0.08590003, 1.7887107, 5.5176305999999995, -0.4268651, -0.49840045, 1.629117, -0.49840045, -0.49840045, -0.49840045, -0.49840045, -0.14501663, -0.30508196, -0.3230676, -0.49840045, -0.26267284, 0.088384144, -0.49840045, -0.49840045, -0.49840045, -0.24325629, 0.23756222, -0.49840045, -0.49840045, -0.43873993, -0.40188086, 1.0163294, -0.49840045, -0.49840045, -0.04278825, -0.49840045, -0.16546774, -0.49840045, -0.49840045, -0.49840045, -0.49840045, 0.8650205, 0.048209794, -0.49840045, -0.34073532, -0.36715215, 0.40570554, -0.006226429, -0.49840045, 0.54376525, 0.7575754, -0.49840045, -0.49840045, 0.83421654, -0.49840045, -0.49840045, -0.49840045, -0.4816501, 0.8981043, 0.5286920999999999, -0.49840045, 2.3266287, -0.27062362, -0.08760956, -0.49840045, -0.49840045, 0.49544750000000004, 1.395209, -0.49840045, 2.8334036, 0.5662256, 1.1443543, -0.24290209, -0.49840045, 0.9623798000000001, -0.2687854, -0.49840045, 1.1661299999999999, -0.49840045])
            image_features = image_features.reshape(1, -1)

            ### Get Nearest Neighbours ###
            print("request.query_params: ",request.query_params)
            qry_params = request.query_params
            record_ids_to_exclude=None
            if len(qry_params)>0:
                record_ids_to_exclude = combine_filters(**qry_params)

            if record_ids_to_exclude:
                model_ids_to_exclude = record_to_model_ids(record_ids_to_exclude)
                model_ids_to_exclude = set(model_ids_to_exclude)
                model_ids = top_k_with_exclusions(image_features, ids_to_exclude=model_ids_to_exclude, k=10)
            else:
                model_ids = knearest_ids(image_features)

            record_ids = model_to_record_ids(model_ids)
            if DEBUG:
                print('record_ids: ',record_ids)
            ### Look Up Metadata ###
            qry_set = ImageMetadata.objects.all()
            if DEBUG:
                print("qry_set len: ",len(qry_set.values()))
            
            results_metadata = []
            
            for record_id in record_ids:
                results_metadata.append(qry_set.filter(record_id=record_id).values()[0])

            if DEBUG:
                print("results_metadata: ", results_metadata)

            ### Save Result to reproduce results if needed (e.g. for shareable link) ###
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

            result = {
                'results':results_metadata,
                'result_id':search_result_id
                }

            if DEBUG:
                print('\napi response: ', result, '\n\n')

            return Response(result, status=200)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)