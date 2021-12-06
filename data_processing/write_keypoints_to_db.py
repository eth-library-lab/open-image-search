"""
write keypoints & descriptores calculated by SIFT
to the database 
"""

import os,sys
import argparse
import shutil
from sqlalchemy import create_engine, insert, text, Table, Column, Integer, MetaData, ForeignKey, select
from sift.sift import compute_sift, format_sift_features_as_list, format_sift_features_as_dict
import cv2
import json

from utils_db import create_db_engine, NumpyEncoder

sys.path.append("../search-model/src" )
import utils


def write_keypoints_to_db(engine, values_dicts):

    # reflect the existing table properties
    metadata_obj = MetaData()
    kp_table = Table("ImageSearch_imagekeypointdescriptor", metadata_obj, autoload_with=engine)

    # create the sql statement with sqlalchemy methods
    stmt = (kp_table.insert()
                    .values(values_dicts)
                    .returning(kp_table.c.id)
    )

    # execute the statement
    with engine.connect() as conn:
        result = conn.execute(stmt)

    return result


def get_images_with_no_keypoints(engine, limit:int=100) -> list:
    """
    query the database to get a batch of images that
    have not had keypoints & descriptors added for them yet
    limit: max number of records to return
    """
    stmt = """
    SELECT i.id,
           i.directory,
           k.keyp_des
    FROM "ImageSearch_image" AS i
    LEFT JOIN "ImageSearch_imagekeypointdescriptor" as k
    ON i.id = k.image_id_id
    WHERE k.keyp_des IS NULL
    LIMIT :limit;
    """
    stmt = text(stmt)
    
    with engine.connect() as conn:
        result = conn.execute(stmt, {"limit":limit})
            
    return [row for row in result]


def main():

    # prep values and insert into database
    engine = create_db_engine()

    # list of images to write keypoints for
    img_list = get_images_with_no_keypoints(engine, limit=100)
    num_imgs = len(img_list)
    print(f"num images to calculate keypoints, descriptors for: {num_imgs}")
    
    if num_imgs>0:
        # calculate keypoint, descriptors for the list of images
        values_dicts = []
        total = num_imgs

        for i, (img_id, img_dir, _ )  in enumerate(img_list):
            fname = str(img_id) + ".jpeg"
            fpath = os.path.join(img_dir, fname)
            img = cv2.imread(fpath)
            #calculate keypoints and descriptors
            [points,descps] = compute_sift(img, rootsift=True)
            kp_des = format_sift_features_as_dict(points, descps)
            #format as json
            kp_des = json.dumps(kp_des, cls=NumpyEncoder)
            temp_dict = {"keyp_des":kp_des,
                        "image_id_id":img_id,
                        "model_id_id":1}
            values_dicts.append(temp_dict)
            utils.print_dyn_progress_bar(total, i)

        print("\nfinished calculating keypoints, descriptors")

        print("writing to database")
        #write kp,des to database

        result = write_keypoints_to_db(engine, values_dicts)
        results = result.fetchall()
    
    print("done")


if __name__ == "__main__":

    description= """creates database records for a directory of images and makes copies of the images with the new id name"""
    parser = argparse.ArgumentParser(description=description)
    args = parser.parse_args()

    main()