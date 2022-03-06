from sqlalchemy import Table, MetaData
import pandas as pd
from typing import List
from utils import chunk_df
from utils_db import create_db_engine, get_institution_id, create_django_datetimestamp


def write_images_to_db(engine, values_dicts):

    # reflect the existing table properties
    metadata_obj = MetaData()
    image_table = Table("ImageSearch_imagemetadata", metadata_obj, autoload_with=engine)

    # create the sql statement with sqlalchemy methods
    stmt = (image_table.insert()
                        .values(values_dicts)
            )

    # execute the statement
    with engine.connect() as conn:
        result = conn.execute(stmt)

    return result


def metadata_df_to_values_dicts(df:pd.DataFrame) -> List[dict,]:
    df = df.copy()
    df["created_date"] = create_django_datetimestamp()
    cols = ["institution_id", #
            "record_name", #
            "created_date", #
            "title", #
            "image_url", #
            "record_url", #
            "inventory_number", #
            "person", #
            "date", #
            "classification", #
            "material_technique", #
            "image_licence", #
            ]
    
    df = df.loc[:,cols]
    values_dicts = [row.dropna().to_dict() for _, row in df.iterrows()]
    return values_dicts

 
def main(inst_ref_name:str):

    # connect to db
    engine = create_db_engine()
    inst_id = get_institution_id(engine, inst_ref_name=inst_ref_name)
    if inst_id == None:
        print("institution not found in DB. please check reference name and/or add institution to database before adding metadata")
        return

    # load all values
    fpath = f"../data/interim/{inst_ref_name}/metadata/metadata.csv"
    df = pd.read_csv(fpath, index_col=False).head(100)
    df['institution_id'] = inst_id

    total_rows = df.shape[0]
    chunksize = 10
    values_dicts = []
    ctr = 0
    for tdf in chunk_df(df, chunksize=chunksize):

        ctr += tdf.shape[0]
        # loop over dataframe to write in chunks to db
        values_dicts = metadata_df_to_values_dicts(tdf)
        write_images_to_db(engine, values_dicts)
        print(f"\rwrote {ctr} of {total_rows}", end="")

    print(f":  done")
    return 


if __name__ == "__main__":

    from argparse import ArgumentParser
    parser = ArgumentParser(description="write prcoessed metadata to imagemetadata table")
    parser.add_argument("--institution",type=str,
                        required=True,
                        help="short reference name for the institution whose metadata you want to write to DB e.g. 'ethz'")
    args = parser.parse_args()

    inst_ref_name = args.institution
    main(inst_ref_name)