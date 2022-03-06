#!/usr/bin/env python
# coding: utf-8

# # parse lido file and extract elements used in the open imageSearch project

# In[1]:


import bs4 #beautifulSoup
import os
import re
from pprint import pprint
import pandas as pd


# # Mapping Lido to imageSearch database fields

# Need to map lido to the fields in our database.  
# 
# our db metadata fields are:
# 
# ```
# id | record_id | created_date | title | image_url | record_url | inventory_number | person | date | classification | material_technique | institution_isil | image_licence | year_min | year_max | classification_id_id | institution_isil_id_id | relationship_id
# ```
# 
# These correspond to the following Lido elements

# 
# `record_id`
# 
# ```html
# <lido:recordID lido:type=http://terminology.lido-schema.org/lido00100 lido:source=https://culture.ld.admin.ch/isil/CH-000511-9>21566</lido:recordID>
# ```

# 
# `title`
# 
# ```html
# <lido:titleWrap>
#     <lido:titleSet>
#         <lido:appellationValue>Porträt von Albrecht Dürer dem Älteren</lido:appellationValue>
#     </lido:titleSet>
# </lido:titleWrap>
# ```

# `record_url`
# 
# ```html
# <lido:recordInfoLink>https://doi.org/10.16903/ethz-grs-D_008883</lido:recordInfoLink>
# ```

# `person`
# 
# ```html
# <lido:displayActorInRole>Hollar, Wenzel (1607 - 1677)</lido:displayActorInRole>
#  
# <lido:displayActorInRole>Dürer, Albrecht (1471 - 1528), nach</lido:displayActorInRole>
# ```
# 

# 
# `imageUrl`
# 
# ```html
# <lido:resourceRepresentation lido:type=http://terminology.lido-schema.org/lido00451>
# <lido:linkResource>https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&amp;module=collection&amp;objectId=21566&amp;resolution=mediumImageResolution</lido:linkResource>
# </lido:resourceRepresentation>
# ```

# `year_min`  `year_max`
# 
# 
# ```html
# <lido:eventDate>
#     <lido:displayDate>1498</lido:displayDate>
#     <lido:date>
#         <lido:earliestDate>1498</lido:earliestDate>
#         <lido:latestDate>1498</lido:latestDate>
#     </lido:date>
# </lido:eventDate>
# ```

# `classification`
# 
# ETH Zurich Graphische Sammlung
# 
# ```html
# <lido:classification lido:type="Objektklassifikation">
#     <lido:conceptID lido:type=http://terminology.lido-schema.org/lido00099 lido:source=http://vocab.getty.edu/aat>
#         http://vocab.getty.edu/aat/300041273
#     </lido:conceptID>
#     <lido:term>Druckgraphik</lido:term>
# </lido:classification>
# ```
# 
# Zentral Bibliothek Graphische Sammlung
# 
# ```html
# 
#     <lido:objectClassificationWrap>
#         <lido:objectWorkTypeWrap>
#             <lido:objectWorkType>
#                 <lido:term>Einblattdruck</lido:term>
#             </lido:objectWorkType>
#             <lido:objectWorkType>
#                 <lido:term>Bildliche Darstellung</lido:term>
#             </lido:objectWorkType>
#             <lido:objectWorkType>
#                 <lido:term>Holzschnitt</lido:term>
#             </lido:objectWorkType>
#         </lido:objectWorkTypeWrap>
#     </lido:objectClassificationWrap>
# ```
# 
# 

# `image_licence`
# 
# ```html
# <lido:rightsResource>
# <lido:rightsType>
# <lido:conceptID lido:type=http://terminology.lido-schema.org/lido00099>https://creativecommons.org/publicdomain/zero/1.0/</lido:conceptID>
# <lido:term>CC0 1.0 Universal (CC0 1.0)</lido:term>
# </lido:rightsType>
# ```

# `material_technique`
# 
# ```html
# <lido:displayMaterialsTech>Radierung</lido:displayMaterialsTech>
#  
# 
# <lido:termMaterialsTech lido:type=http://terminology.lido-schema.org/lido00132>
# <lido:conceptID lido:type=http://terminology.lido-schema.org/lido00099 lido:source=http://vocab.getty.edu/aat>http://vocab.getty.edu/aat/300053241</lido:conceptID>
# <lido:term>Radierung</lido:term>
# </lido:termMaterialsTech>
# ```

# `institution_isil`
# 
# ```html
# 
# ```

# `relationship_type`
# 
# ```xml
# <lido:objectRelationWrap>
#         <lido:subjectWrap>
#             <lido:subjectSet>
#                 <lido:subject>
#                     <lido:subjectPlace>
#                         <lido:place>
#                             <lido:placeID lido:type="http://terminology.lido-schema.org/identifier_type/uri">
#                                 http://d-nb.info/gnd/1090935323
#                             </lido:placeID>
#                             <lido:namePlaceSet>
#                                 <lido:appellationValue>Château de Bulle (Bulle, Schweiz)</lido:appellationValue>
#                             </lido:namePlaceSet>
#                         </lido:place>
#                     </lido:subjectPlace>
#                 </lido:subject>
#             </lido:subjectSet>
#         </lido:subjectWrap>
#     <lido:relatedWorksWrap>
#         <lido:relatedWorkSet>
#             <lido:relatedWork>
#                 <lido:displayObject>
#                     Hermann Spiess-Schaad: David Herrliberger Zürcher Kupferstecher und Verleger 1697-1777, Nr. 1.5.1, S. 141ff
#                 </lido:displayObject>
#             </lido:relatedWork>
#             <lido:relatedWorkRelType>
#                 <lido:term>dokumentiert in</lido:term>
#             </lido:relatedWorkRelType>
#         </lido:relatedWorkSet>
#     </lido:relatedWorksWrap>
# </lido:objectRelationWrap>
# ```

# 
# ## functions

# In[2]:


def get_titles(object_identification_wrap: bs4.element.Tag):
    """
    find list of titles for a given object
    """
    
    titles = []
    for title_set in object_identification_wrap.find_all("lido:titleSet"):
        print(title_set.attrs)
        title = title_set.find("lido:appellationValue")
        if title:
            titles.append(title.text)
            
    return titles


# In[3]:


def find_lido_element_text(lido: bs4.element.Tag, 
                            element_name:str) -> str:
    
    """
    generic function to a find an element from the given tag and return the innerText from the first found result
    """
    
    try:
        text = lido.find(element_name).text

    except Exception as E:
        print(E)
        text = None
    
    return text  
    


# In[4]:


def get_lido_id(lido: bs4.element.Tag):
    """
    <lido:lidoRecID lido:type="http://terminology.lido-schema.org/lido00100" lido:source="http://ld.zdb-services.de/resource/organisations/DE-MUS-079214">DE-MUS-079214/lido/05091715,T,001</lido:lidoRecID>
    """ 

    try:
        _id = lido.find("lido:lidoRecID").text
    except Exception as E:
        print(E)
        _id = None
    
    return _id


# In[5]:


def get_image_url(lido: bs4.element.Tag) -> str:
    """
    assume there is only one image and that we only use lido:type 'http://terminology.lido-schema.org/lido00451'
    
    return the url for the image or None if element is not found 
    """
    
    rep_types_to_use = [
        "http://terminology.lido-schema.org/lido00451",
        "http://terminology.lido-schema.org/resourceRepresentation_type/provided_image",
    ]
    
    resource_reps = lido.find_all("lido:resourceRepresentation")
    
    for resource_rep in resource_reps:
        rep_type = resource_rep.get("lido:type")
        if rep_type in rep_types_to_use:
            url = resource_rep.find("lido:linkResource")
            if url:
                return url.text

    return None


# In[6]:


def find_record_id(lido: bs4.element.Tag) -> str:
    
    res = lido.find("lido:lidoRecID", attrs = {"lido:type":"http://terminology.lido-schema.org/identifier_type/local_identifier"})
    if res:
        return res.text
    
    res = lido.find("lido:recordID", attrs={"lido:type":"http://terminology.lido-schema.org/lido00100"})
    if res:
        return res.text
    
    return None


# In[7]:


def find_record_url(lido: bs4.element.Tag) -> str:
    
    res = lido.find("lido:recordInfoLink")

    if res:
        return res.text            
    return None


# In[8]:


def find_inventory_number(lido: bs4.element.Tag) -> str:
    
    res = lido.find("lido:workID", attrs={"lido:type":"Inventarnummer"})

    if res:
        return res.text            
    return None


# In[9]:


def find_persons(lido) -> [str,]:
    
    res = lido.find_all("lido:displayActorInRole")
    
    if res:
        # return as list of comma seperated values
        return ",".join([r.text for r in res])

    return None


# In[10]:



def find_relevant_dates(lido) -> [str,]:
    
    # lido:term xml:lang="en">Publication event
    # http://terminology.lido-schema.org/identifier_type/uri">http://terminology.lido-schema.org/lido00485
    
    event_types_to_find= [
    "http://terminology.lido-schema.org/lido00485", # publication date
    "http://terminology.lido-schema.org/lido00486", # work conception
    "http://terminology.lido-schema.org/lido00484", # Expression creation
    "http://terminology.lido-schema.org/lido00487", # Carrier Production
    "http://terminology.lido-schema.org/lido00228", # publication
    "http://terminology.lido-schema.org/lido00528", # exact date
    "http://terminology.lido-schema.org/lido00529", # estimated date
    ]
    found_dates=[]

    events = lido.find_all("lido:event")
    for event in events:
        event_type = event.find("lido:eventType").find("lido:conceptID").text # attrs={"lido:type":"http://terminology.lido-schema.org/lido00099"}
        if event_type in event_types_to_find:
            event_dates = find_min_max_years_within_event(event)
            found_dates +=event_dates

    return found_dates


# In[11]:


def find_min_max_years_within_event(lido) -> (int, int):
    """
    find all listed dates and take min max
    
    """
    
    found_date_strings = []
    date_types = ["lido:displayDate", "lido:earliestDate", "lido:latestDate",]
    
    for date_type in date_types:
        dates = lido.find_all(date_type)
        for date in dates:
            date_text = date.text.strip()
            if date_text:
                found_date_strings.append(date_text)
                         
    return found_date_strings


# In[12]:


def find_years_in_string(s: str) -> list:
    """
    finds 4 digit numbers in strings
    e.g. for input "earliest year is 1591 - to (1700)"
    returns [1591, 1700]
    """

    ptrn = r"[0-9]{4}"
    res = re.findall(ptrn, s)
    return res


# In[13]:


def get_min_max_year_from_dates(date_strings:[str,]) -> (int, int):
    
    years = []
    for s in date_strings:
        years += find_years_in_string(s)

    if years:
        year_min = min(years)
        year_max = max(years)
    else:
        year_min = None
        year_max = None

    return year_min, year_max


# In[14]:


def find_title(lido: bs4.element.Tag) -> str:
    """
    can be multiple titles. this function just finds the first
    """
    try:
        title_element = lido.find("lido:titleSet").find("lido:appellationValue")
    except Exception as e:
        return None
    
    return title_element.text


# In[15]:


def find_classification(lido: bs4.element.Tag) -> str:

    cls = lido.find("lido:classification")
    
    if cls:
        return cls.find("lido:term").text
    
    return None


# In[16]:


def find_classification_2(lido: bs4.element.Tag) -> str:
    """   `
        <lido:objectClassificationWrap>
            <lido:objectWorkTypeWrap>
                <lido:objectWorkType>
                    <lido:term>Einblattdruck</lido:term>
                </lido:objectWorkType>
                <lido:objectWorkType>
                    <lido:term>Bildliche Darstellung</lido:term>
                </lido:objectWorkType>
                <lido:objectWorkType>
                    <lido:term>Holzschnitt</lido:term>
                </lido:objectWorkType>
            </lido:objectWorkTypeWrap>
        </lido:objectClassificationWrap>
    `
    """
    class_el =  lido.find("lido:objectClassificationWrap")
    if class_el:
        
        classes = class_el.find_all("lido:objectWorkType")
        cls_list = [cls.findChildren()[0].text for cls in classes]
        # return string as comma seperated values
        return ",".join(cls_list)
    
    return None


# In[17]:


def find_insitution_isil(lido)->str:

    isil = lido.find("lido:legalBodyID", attrs={"lido:type":"http://terminology.lido-schema.org/lido00099"})

    isil_text = ""
    if isil:
        isil_text = isil.text
    
    if isil_text=="":
        isil = lido.find("lido:legalBodyID", attrs={"lido:type":"http://terminology.lido-schema.org/identifier_type/uri"})
        if isil:
            isil_text = isil.text
    
    isil_text = re.sub("^info:isil/","", isil_text)

    return isil_text


def find_insitution_name(lido)->str:

    el = lido.find("lido:legalBodyName")
    
    if el:
        return el.find("lido:appellationValue").text

    return None


# In[18]:


def find_image_licence(lido) -> str:
    
    el = lido.find("lido:rightsResource")
    if el:
        el = el.find("lido:term")

    if el:
        return el.text
    
    return None


# In[19]:


def find_credit_line(lido) -> str:
    
    el = lido.find("lido:creditLine")
    
    if el:
        return el.text
    
    return None


# In[20]:


def find_material_techniques(lido) -> str:
    
    mat_tecs = lido.find_all("lido:displayMaterialsTech")
    
    if mat_tecs:
        mat_tec_list = [mat_tec.text for mat_tec in mat_tecs]
        # return string as comma seperated values
        return ",".join(mat_tec_list)

    return None


# In[21]:


def find_relationship_types(lido: bs4.element.Tag) -> [str,]:
    """
    find all the `lido:relatedWorkRelType` elements and return the inner text from the lido:relatedWorkRelType
    """

    results=[]
    rel_types = lido.find_all("lido:relatedWorkRelType")
    
    for rel_type in rel_types:
        if rel_type:
            for child in rel_type.findChildren(recursive=False):
                txt = child.text
                if txt not in results:
                    results.append(txt)
    return results


def clean_relationship_types(relationships:list)->str:
    
    # rename uris to string descirptions based on dict of relationship types 
    # from http://terminology-view.lido-schema.org/vocnet/?startNode=lido00409&lang=en&uriVocItem=http://terminology.lido-schema.org/lido00138)
    lido_rel_dict ={
        "http://terminology.lido-schema.org/lido00622":"is duplicate of",
        "http://terminology.lido-schema.org/lido00625":"contains reproduction of",
        "http://terminology.lido-schema.org/lido00255":"is physical part of",
        "http://terminology.lido-schema.org/lido00256":"has physical part"
    }
    for i, rel in enumerate(relationships):
        if rel in lido_rel_dict:
            relationships[i] = lido_rel_dict[rel]

    # string listing unique elements
    output = ""
    if relationships:
        output += ",".join(list(set(relationships)))

    return output


# In[22]:


def clean_terms(terms:str):
    """
    """ 
    return re.sub("druckgrafik","druckgraphik",terms)
    

# In[23]:


def find_all_lido_mappings(lido) -> dict:
    
    lido_dict = {}
    # find record_id
    lido_dict['record_name'] = find_record_id(lido)
    
    # find publisher_id
    lido_dict['object_published_id'] = find_lido_element_text(lido,"lido:objectPublishedID")
    
    # find lido_id
    lido_dict['lido_id'] = get_lido_id(lido)
    
    # find image_url
    lido_dict['image_url'] = get_image_url(lido)
    
    # find record_url
    lido_dict['record_url'] = find_record_url(lido)
    
    # find inventory_number
    lido_dict['inventory_number'] = find_inventory_number(lido)
    
    # find host_isil
    lido_dict['institution_isil'] = find_insitution_isil(lido)
    lido_dict['institution_name'] = find_insitution_name(lido)
    
    # find image_licence
    lido_dict['image_licence'] = find_image_licence(lido)
    
    # find creditline
    lido_dict['credit_line'] = find_credit_line(lido)
    
    # find title
    lido_dict['title'] = find_title(lido)
    
    # find person(s)
    lido_dict['person'] = find_persons(lido)    
    
    # find material_technique
    lido_dict['material_technique'] = find_material_techniques(lido)
    lido_dict['material_technique'] = clean_terms(lido_dict['material_technique'])
    
    # find min max years
    found_date_strings = find_relevant_dates(lido)
    year_min, year_max = get_min_max_year_from_dates(found_date_strings)
    lido_dict['year_min'] = year_min
    lido_dict['year_max'] = year_max
    lido_dict["date"] = ",".join(found_date_strings)

    # find classification
    lido_dict['classification'] = find_classification(lido)
    if lido_dict['classification']==None:
        lido_dict['classification'] = find_classification_2(lido)
    lido_dict['classification'] =  clean_terms(lido_dict['classification'])
    
    # find relationships to other works
    relationships = find_relationship_types(lido)
    lido_dict['relationship'] = clean_relationship_types(relationships)
    
    return lido_dict


# In[24]:


def parse_xml_and_output_csv(content, output_fpath):
    """parse xml text data and output to csv"""

    # parse xml file
    print("parsing with BeautifulSoup ...")
    bs_content = bs4.BeautifulSoup(content, "xml")
    
    # find all the individual lido records, as the main element that contains all the metadata for an object
    lidos = bs_content.find_all('lido:lido')
    del bs_content

    num_records = len(lidos)
    print(f"found lido elements: {num_records}")

    chunksize=100
    lido_dict_list = []
    include_header = True
    for i, lido in enumerate(lidos):

        lido_dict = find_all_lido_mappings(lido)
        lido_dict_list.append(lido_dict)

        # add record to list / write to db
        # save at each chunk interval or on last record
        if (len(lido_dict_list) >= chunksize) or (i+1==num_records):

            tdf = pd.DataFrame(lido_dict_list)
            tdf.to_csv(output_fpath, mode="a", index=False, header=include_header)
            #only write header the first time
            include_header=False
            # clear list
            lido_dict_list = []
            print(f"\rprocessed {i+1} of {num_records}", end="")
            include_header=False
    print(":  done processing lido file")
    print(f"saved to: {output_fpath}")


# In[25]:


def main(institution:str, fname: str):
    
    DATA_DIR = "../data/"
    dir_path = f"raw/{institution}/"

    # prepare output directory to save to
    output_dir_path = DATA_DIR + f"interim/{institution}/metadata/"
    if os.path.exists(output_dir_path)==False:
        os.makedirs(output_dir_path)
    output_fpath = output_dir_path + "metadata.csv"
    
    if os.path.exists(output_fpath):
        print(f"error found existing output file: {output_fpath}")
        return 1
    
    fpath = os.path.join(DATA_DIR, dir_path, fname)
    print(f"opening file: {fpath}")

    # load lido file
    with open(fpath, 'r') as f:
        content = f.read()
    
    parse_xml_and_output_csv(content, output_fpath)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="parse lido xml file into a tabular csv format")
    parser.add_argument("--institution",
                        required=True,
                        default=None,
                        type=str,
                        help="short reference name for the institution whose lido data you want to process e.g. ethz")
    parser.add_argument("--fname",
                        required=True,
                        default=None,
                        type=str,
                        help="filename of the lido xml file to parse")
    args = parser.parse_args()

    institution = args.institution
    fname = args.fname

    # institution="zbz"
    # fname = "DL-ZB-20201209-20210219.LIDO.xml"

    # institution= "mahg"
    # fname="Export_MAH_20171025.LIDO.xml"

    main(institution, fname)

