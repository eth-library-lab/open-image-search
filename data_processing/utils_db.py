import os
from sqlalchemy import create_engine
import json
import numpy as np

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