"""
add encoded feature labels/tags to the text based metadata
e.g. classification, materials
"""


import os
import string
import pandas as pd
import argparse

import utils
import label_utils as lu


def load_df(fpath:string)->pd.DataFrame:

    df = pd.read_csv(fpath)

    return df


def label_df(df:pd.DataFrame) -> pd.DataFrame:

    # join the classification and mat_tec columns the data is often overlapped between them
    input_ser = df['classification'].astype(str) + ", " + df['material_technique'].astype(str)
    input_ser = input_ser.astype(str)

    # label classification
    col_name = "classification"
    label_table = "ImageSearch_classification"
    class_dict = lu.load_feature_labels(label_table)
    output_ser = lu.label_series(input_ser, class_dict)
    df[col_name+"_id"] = output_ser

    # label material technique
    col_name = "material_technique"
    label_table = "ImageSearch_materialtechnique"
    class_dict = lu.load_feature_labels(label_table)
    output_ser = lu.label_series(input_ser, class_dict)
    df[col_name+"_id"] = output_ser

    
    # label relationship
    col_name = "relationship_type"
    label_table="ImageSearch_relationship"
    input_ser = df[col_name]
    class_dict = lu.load_feature_labels(label_table)
    output_ser = lu.label_series(input_ser, class_dict)
    df[col_name+"_id"] = output_ser

    return df


def save_df(df:pd.DataFrame, institution:string)->None:

    output_fpath = f"../data/processed/{institution}/metadata/metadata.csv"
    utils.prep_dir(output_fpath)
    df.to_csv(output_fpath)

    return


def main(institution:string)->None:

    fpath = f"../data/interim/{institution}/metadata/metadata.csv"
    df = load_df(fpath)
    df = label_df(df)
    save_df(df, institution)

    print("\n", df.head())
    print("\n", df.info())

    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="metadata labelling")
    parser.add_argument("--institution",
                        required=True,
                        default=None,
                        type=str,
                        help="short reference name for the institution whose data you want to process e.g. ethz")
    args = parser.parse_args()

    institution = args.institution
    fpath = f"../data/interim/{institution}/metadata/metadata.csv"
    output_fpath = f"../data/processed/{institution}/metadata/metadata.csv"

    # when running in the command line, check interactively if the user
    # wants to overwrite an existing file
    if utils.overwrite_if_exists(output_fpath):
        main(institution)
    else:
        print("process skipped")