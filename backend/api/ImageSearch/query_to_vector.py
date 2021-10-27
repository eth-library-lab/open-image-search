from pathlib import Path
import os
import json 
import numpy as np

from ImageSearch.models import Classification, MaterialTechnique, Relationship, Institution

def load_filter_lookup():
    """
    creates a nested dictionary that can be used to look ids for strings and create one-hot vectors 
    """
    print("making filter lookup")
    models = [Classification, MaterialTechnique, Relationship, Institution]
    keys = ["classification","materialtechnique","relationship", "institution"]

    # filter_dict = {
    #     "classification":{},
    #     "materialtechnique":{},
    #     "relationship":{},
    #     "institution"{}:
    # }

    filter_dict = {}

    for key, model in zip(keys,models):
        #get queryset as a list of name, id tuples and format as a dict
        qs = model.objects.all().values_list("name","pk")
        string_lookup = {name:pk for name, pk  in qs}
        #add to the overall dictionary
        filter_dict[key] = string_lookup

    return filter_dict


def make_filter_vec(filter_dict, fltr_type, qry_names):
    """
    uses the filter_dict to convert a list of names into a one hot encoded vector
    """
    qry_vec_len = len(filter_dict[fltr_type])
    
    if qry_names:
        qry_vec = np.zeros(qry_vec_len, dtype=int)
        # subtract 1 as vector is zero indexed but database index starts at 1
        indices = [filter_dict[fltr_type].get(qry_name) -1 for qry_name in qry_names]
        qry_vec[indices] = 1

    else:
        qry_vec = np.zeros(qry_vec_len, dtype=int)
    
    return qry_vec


def make_meta_vec(filter_dict, **kwargs):
    
    arg_names = kwargs.keys()

    # for each type of query parameter, create one hot encoded query vector
    param_names = ["classification", "materialTechnique", "relationship", "institution"]
    vec_list = []
    for param_name in param_names:

        if param_name in arg_names:
            qry_names = kwargs[param_name]
        else:        
            qry_names = []
        
        vec = make_filter_vec(filter_dict,
                                fltr_type=param_name.lower(),
                                qry_names=qry_names)
        vec_list.append(vec)

    # the dimension of this array should match the crorresponding input shape in the retrieval model    
    meta_vec = np.hstack(vec_list).astype(np.int)

    return meta_vec


def make_year_vec(**kwargs):
    
    arg_names = kwargs.keys()
    
    before_year = 0
    after_year = 0
   
    if "afterYear" in arg_names:
        after_year = int(kwargs["afterYear"][0])

        if "beforeYear" not in arg_names:
            before_year = 3000

    if "beforeYear" in arg_names:
        before_year = int(kwargs["beforeYear"][0])

    years_vec = np.array([after_year,before_year],dtype=int)

    return years_vec

