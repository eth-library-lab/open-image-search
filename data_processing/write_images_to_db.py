"""
script to add directory of images to database 
and copy/rename files with db assigned ids 
"""

import os,sys
import argparse

sys.path.append("../search-model/src" )
import utils

import shutil

from sqlalchemy import create_engine, insert, text, Table, Column, Integer, MetaData, ForeignKey, select

from utils_db import create_db_engine


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



def rename_files_using_db_ids(input_directory, results):
    """
    input_directory: path to the existing files
    results: an iterable three part tuple of (new_id, output_directory, provider_filename)
    """
    total = len(results)

    for i, (new_id, output_directory, provider_filename) in enumerate(results):
    
        in_fpath, out_fpath = make_in_out_fpaths(
                                            input_directory,
                                            provider_filename,
                                            output_directory, 
                                            new_id)
        utils.prep_dir(out_fpath)
        shutil.copy2(in_fpath, out_fpath)

        utils.print_dyn_progress_bar(total, i)

    print("\nfinished adding images to db and renaming with new ids")
    # use returned id numbers to copy and rename images to processed folder with new file names
    return


def main(inst_ref):

    input_directory = f"../data/interim/{inst_ref}/images"
    output_directory = f"../data/processed/{inst_ref}/images"

    # list images in folder
    flist = utils.list_files_in_dir(input_directory)
    flist = [f.replace(input_directory+"/","") for f in flist]

    # prep values and insert into database
    engine = create_db_engine()
    inst_id = get_institution_id(engine, inst_ref_name=inst_ref)
    
    values_dicts = [{"directory":output_directory, 
                     "provider_filename":f,
                     "institution_id":inst_id} for f in flist]

    # result = write_images_to_db(engine, values_dicts)
    # results = result.fetchall()

    # # copy files with newly assigned ids as file names
    # utils.prep_dir(output_directory)
    # rename_files_using_db_ids(input_directory, results)


if __name__ == "__main__":

    description= """creates database records for a directory of images and makes copies of the images with the new id name"""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--inst_ref",  type=str,
                        help="short name of data provider for this directory of images (used to form the directory path)")
    args = parser.parse_args()

    main(inst_ref=args.inst_ref)