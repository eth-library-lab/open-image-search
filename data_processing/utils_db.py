import os
from sqlalchemy import create_engine, Table, MetaData, text
import json
import numpy as np
import pandas as pd
from typing import List
from datetime import datetime as dt


def create_connection_string():

    user=os.environ.get("DB_USER")
    password=os.environ.get("DB_PASSWORD")
    host=os.environ.get("DB_HOST")
    port=os.environ.get("DB_PORT")
    dbname=os.environ.get("DB_NAME")

    con_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

    return con_str

def create_db_engine():

    con_str = create_connection_string()
    engine = create_engine(con_str)
    
    return engine


def create_django_datetimestamp(dt_object=None):
    
    if dt_object==None:
        created_time = dt.now()
    else:
        created_time = dt_object
    # for django, timefield must be in format YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
    # e.g. "2020-05-26T11:40:56+01:00"
    created_time = created_time.strftime('%Y-%m-%dT%H:%M:%S+01:00')
    
    return created_time


def institution_exists(engine, inst_ref_name:str):
    
    stmt = """
    SELECT id, ref_name
    FROM "ImageSearch_institution"
    WHERE ref_name = :inst_ref_name
    """
    stmt = text(stmt)
    
    with engine.connect() as conn:
        result = conn.execute(stmt, {"inst_ref_name":inst_ref_name})

    exists=False
    for row in result:
        print("found existing institution: ", row)
        exists=True

    return exists


def series_to_values_dicts(ser:pd.Series, field_name:str)-> List[dict,]:

    tstamp = create_django_datetimestamp()
    val_dicts = [{field_name:v, "created_date":tstamp} for v in ser]
    return val_dicts


def write_values_dict_to_db(engine, values_dict:dict, table_name:str) -> List:
    """
    example:
    table_name="ImageSearch_classification"
    """
    # reflect the existing table properties
    metadata_obj = MetaData()
    table = Table(table_name, metadata_obj, autoload_with=engine)

    # create the sql statement with sqlalchemy methods
    stmt = (table.insert()
                    .values(values_dict)
                    .returning(table.c.id)
    )

    # execute the statement
    with engine.connect() as conn:
        try:
            result = conn.execute(stmt)
        except Exception as e:
            print(e)
            return []
    return result


def get_institution_id(engine, inst_ref_name="ethz"):
    
    stmt = """
    SELECT id
    FROM "ImageSearch_institution"
    WHERE ref_name = :inst_ref_name
    LIMIT 1;
    """
    stmt = text(stmt)
    
    with engine.connect() as conn:
        result = conn.execute(stmt, {"inst_ref_name":inst_ref_name})
    
    for row in result:
        return row[0]


class NumpyEncoder(json.JSONEncoder):
    """ Custom encoder for numpy data types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):

            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)): 
            return None

        return json.JSONEncoder.default(self, obj)