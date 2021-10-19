from pathlib import Path
import os
import json 
import numpy as np

def load_filter_lookup():
    
    print("making filter lookup")

    #replace this later with a query from the database
    types = ["MaterialTechnique", "Classification","Relationship", "Institution"]
    filter_dict = {}

    base_dir = Path(__file__).resolve().parent.parent

    for t in types:
        fpath = os.path.join(base_dir, f"fixtures/{t}.json")

        with open(fpath, 'r') as f:
            fixture = json.load(f) 

        string_lookup = {d['fields']['name']:d['pk'] for d in fixture}
        key = t.lower()
        filter_dict[key] = string_lookup

    return filter_dict


def make_filter_vec(filter_dict, fltr_type, qry_names):
    """
    
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

    for kw in kwargs:
        print(kw, '-', kwargs[kw])
    
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

