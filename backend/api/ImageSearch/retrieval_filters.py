from ImageSearch.models import ImageMetadata
from django.db.models import Q

def records_to_exclude_by_year(after_year=None, before_year=None, include_unknown_year=False):
    """
    after_year: int, the user wants results from after this year
    before_year: int, the user wants results from before this year
    
    returns
    ids_to_exclude: set of ids that do not meet the filter criteria

    if before_year or after_year is within the range of the earliest estimated year and latest estimated year then
    the record will be included
    """
    
    if after_year and before_year:
        assert after_year <= before_year, "after_year can't be less than before_year. after_year gets records from after or in this year. before_year gets records from before or in this year"

    qs_nan = ImageMetadata.objects.none()
    qs_too_early = ImageMetadata.objects.none()
    qs_too_late = ImageMetadata.objects.none()

    if include_unknown_year == False:
        qs_nan = ImageMetadata.objects.all().filter(year_min=-1)

    if after_year:
        # get the records whose latest year comes before this year
        qs_too_early = ImageMetadata.objects.all().filter(year_max__lte=after_year)

    if before_year:
        # get the records whose earliest year comes after this year
        qs_too_late = ImageMetadata.objects.all().filter(year_min__gte=before_year)
    
    # these are all the indices to remove from the results
    qs_to_exclude = qs_nan.union(qs_too_early, qs_too_late)
    ids_to_exclude = set(qs_to_exclude.values_list(flat=True))
    
    return ids_to_exclude


def records_to_exclude_by_classification(classification_qry_names=[]):

    ids_to_exclude = set()
    
    if classification_qry_names:
        res = ImageMetadata.objects.exclude(classification_id__name__in=classification_qry_names)

    ids_to_exclude = res.values_list('id',flat=True)

    return set(ids_to_exclude)


def records_to_exclude_by_material_technique(mat_tec_qry_names=[]):

    ids_to_exclude = set()
    
    if mat_tec_qry_names:
        res = ImageMetadata.objects.exclude(material_technique_id__name__in=mat_tec_qry_names)

        ids_to_exclude = res.values_list('id',flat=True)
        set(ids_to_exclude)

    return ids_to_exclude


def records_to_exclude_by_relationship(relationship_qry_names=[]):
    """
    relationship_qry_names: the names of the relationships that the user *does* want to see
    """
    ids_to_exclude = set()
    
    if relationship_qry_names:
        res = ImageMetadata.objects.exclude(relationship_type_id__name__in=relationship_qry_names)

        ids_to_exclude = res.values_list('id',flat=True)
        set(ids_to_exclude)

    return ids_to_exclude


def records_to_exclude_by_institution(institution_qry_names=[]):
    """
    relationship_qry_names: the names of the institutions that the user *does* want to see
    """
    ids_to_exclude = set()
    
    if institution_qry_names:
        res = ImageMetadata.objects.exclude(institution_isil_id__name__in=institution_qry_names)

        ids_to_exclude = res.values_list('id',flat=True)
        set(ids_to_exclude)

    return ids_to_exclude


def combine_filters(**kwargs):
    
    # init an empty list of sets
    set_list = [set(),]
    for kw in kwargs:
        print(kw, '-', kwargs[kw])
    
    arg_names = kwargs.keys()

    if "classification" in arg_names:
       
        qry_names = kwargs["classification"]
        class_set = records_to_exclude_by_classification(classification_qry_names=qry_names)
        set_list.append(class_set)

    after_year = None
    if "afterYear" in arg_names:
        after_year = int(kwargs["afterYear"][0])

    before_year = None        
    if "beforeYear" in arg_names:
        before_year = int(kwargs["beforeYear"][0])
    
    include_unknown_year = None        
    if "includeUnknownYear" in arg_names:
        include_unknown_year = kwargs["includeUnknownYear"]  
    
    if any([after_year, before_year, include_unknown_year]):

        year_set = records_to_exclude_by_year(after_year=after_year, 
                                              before_year=before_year, 
                                              include_unknown_year=include_unknown_year)
        set_list.append(year_set)

    if "materialTechnique" in arg_names:
        
        qry_names = kwargs["materialTechnique"]
        mat_set = records_to_exclude_by_material_technique(mat_tec_qry_names=qry_names)
        set_list.append(mat_set)

    if "relationship" in arg_names:

        qry_names = kwargs["relationship"]
        rel_set = records_to_exclude_by_relationship(relationship_qry_names=qry_names)
        set_list.append(rel_set)

    # return the combination of all sets by unpacking the set_list
    
    return set.union(*set_list)
