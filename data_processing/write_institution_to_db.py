"""
script to add directory of images to database 
and copy/rename files with db assigned ids 
"""

import os,sys
import argparse

from datetime import datetime as dt

from sqlalchemy import create_engine, insert, text, Table, Column, Integer, MetaData, ForeignKey, select

from utils_db import create_db_engine, institution_exists


def write_institution_to_db(engine, values_dict):

    # reflect the existing table properties
    metadata_obj = MetaData()
    table = Table("ImageSearch_institution", metadata_obj, autoload_with=engine)

    # create the sql statement with sqlalchemy methods
    stmt = (table.insert()
                    .values(values_dict)
                    .returning(table.c.id)
    )

    # execute the statement
    with engine.connect() as conn:
        result = conn.execute(stmt)

    return result



def main(args):

    name=args.name, 
    ref_name=args.ref_name
    isil_id = args.isil_id
    # prep values and insert into database
    engine = create_db_engine()
    exists = institution_exists(engine, inst_ref_name=ref_name)
    if exists==False:
        values_dict = {"name":name,
                       "isil_id":isil_id,
                       "ref_name":ref_name,
                       "created_date":dt.now()}
        write_institution_to_db(engine, values_dict)
    else:
        print(f"institution: '{ref_name}' already exists")

if __name__ == "__main__":

    description= """creates a database record for an institution"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--name",  type=str,
                    help="official name of institution/data provider")
    parser.add_argument("--ref_name",  type=str,
                        help="short reference name of the data provider (used to form the directory path)")
    parser.add_argument("--isil_id",  type=str,
                        help="official isil identifier for the institution")
    args = parser.parse_args()

    main(args)