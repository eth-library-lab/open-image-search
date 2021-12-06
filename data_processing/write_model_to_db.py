"""
script to add a features/keypoint extraction model and description 
to the database to track which features were created by which model
"""

import os,sys
import argparse

from datetime import datetime as dt

from sqlalchemy import create_engine, insert, text, Table, Column, Integer, MetaData, ForeignKey, select


from utils_db import create_db_engine, NumpyEncoder


def write_model_to_db(engine, values_dict):

    # reflect the existing table properties
    metadata_obj = MetaData()
    table = Table("ImageSearch_featuremodel", metadata_obj, autoload_with=engine)

    # create the sql statement with sqlalchemy methods
    stmt = (table.insert()
                    .values(values_dict)
                    .returning(table.c.id)
    )

    # execute the statement
    with engine.connect() as conn:
        result = conn.execute(stmt)

    return result



def main(model_name, description):

    # prep values and insert into database
    engine = create_db_engine()

    values_dict = {"name":model_name,
                    "description":description,
                    "created_date":dt.now()}
    write_model_to_db(engine, values_dict)


if __name__ == "__main__":

    description= """creates a database record for a model"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--model_name",  type=str,
                    help="name of the feature extraction model")
    parser.add_argument("--description",  type=str,
                        help="description of the model, key parameters etc.")
    args = parser.parse_args()

    main(model_name=args.model_name, 
        description=args.description)