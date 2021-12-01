import os,sys
import argparse

sys.path.append("../search-model/src" )
import utils

import shutil

from sqlalchemy import create_engine, insert, text, Table, Column,Integer, MetaData, ForeignKey


def create_connection_string():

    user=os.environ.get("DB_USER")
    password=os.environ.get("DB_PASSWORD")
    host=os.environ.get("DB_HOST")
    port=os.environ.get("DB_PORT")
    dbname=os.environ.get("DB_NAME")

    con_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

    return con_str


def connect_to_db():

    con_str = create_connection_string()
    engine = create_engine(con_str)
    
    return engine


def write_images_to_db(engine, values_dicts):

    # reflect the existing table properties
    metadata_obj = MetaData()
    image_table = Table("ImageSearch_image", metadata_obj, autoload_with=engine)

    # create the sql statement with sqlalchemy methods
    stmt = (image_table.insert()
                        .values(values_dicts)
                        .returning(
                          image_table.c.id, 
                          image_table.c.directory,
                          image_table.c.provider_filename)
    )

    # execute the statement
    with engine.connect() as conn:
        result = conn.execute(stmt)

    return result


def make_in_out_fpaths(input_directory,
                input_fname,
                output_directory, 
                new_file_id):

    input_fpath = os.path.join(input_directory, input_fname)

    f_extension = input_fname.rsplit(".", maxsplit=1)[-1]
    output_fname = f"{new_file_id}.{f_extension}"
    output_fpath = os.path.join(output_directory, output_fname)

    return input_fpath, output_fpath


def main(provider):

    input_directory = f"../data/interim/{provider}/images"
    output_directory = f"../data/processed/{provider}/images"

    # list images in folder
    flist = utils.list_files_in_dir(input_directory)
    flist = [f.replace(input_directory+"/","") for f in flist]
    # insert records into database
       
    values_dicts = [{"directory":output_directory, "provider_filename":f} for f in flist]

    engine = connect_to_db()
    result = write_images_to_db(engine, values_dicts)
    
    # copy files with newly assigned ids as file names
    utils.prep_dir(output_directory)

    for (new_id, output_directory, provider_filename) in result.fetchall():
    
        in_fpath, out_fpath = make_in_out_fpaths(
                                            input_directory,
                                            provider_filename,
                                            output_directory, 
                                            new_id)
        print(in_fpath, out_fpath)
        # shutil.copy2(in_fpath, out_fpath)
    # use returned id numbers to copy and rename images to processed folder with new file names

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='metadata_cleaning')
    parser.add_argument("--provider",  type=str,
                        help="name of data provider for this directory of images (forms part of directory path")
    args = parser.parse_args()

    main(provider=args.provider)