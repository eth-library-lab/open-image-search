# creates a list/vocabulary of classification terms
# To be used later to tag text that contains these terms

import pandas as pd
import numpy as np
import re
import os, sys
import argparse
from collections import defaultdict

sys.path.append('..')
import export_metadata

DATA_DIR = "../data"

def load_df():
    # list of files to load classification terms from
    fpaths = [
        (DATA_DIR, "raw","ethz","metadata","imageSearch_relations.xlsx"),
    ]

    df_list = []
    for fpath in fpaths:
        fpath = os.path.join(*fpath)
        if fpath.endswith(".xlsx"):
            df = pd.read_excel(fpath)
        else:
            df = pd.read_csv(fpath)
        
        df_list.append(df)

    df = pd.concat(df_list)
    print(f"loaded metadata file with {df.shape[0]} rows")

    return df

def main():

    df = load_df()
    
    col_name="classification"
    #### classification types ####
    if col_name in df.columns:
        ser = df[col_name]
        ser = ser.str.strip().replace("",np.nan).dropna()
        ser = ser.drop_duplicates()
        ser = ser.str.lower()

        # write classification csv and fixture
        model_name = 'Classification'

        tdf = pd.DataFrame(ser)
        output_dir = os.path.join(DATA_DIR, "processed","lists")
        csv_path = os.path.join(output_dir, model_name+".csv")
        tdf.to_csv(csv_path, index=False)

        # write json fixture
        fixture_lst = export_metadata.df_to_fixture_list(tdf,
                    app_name='ImageSearch',
                    model_name=model_name,
                    use_df_index_as_pk=True,
                    create_datetimefield_name="created_date",
                    created_by_field_name=None,
                    )
        export_metadata.write_fixture_list_to_json(fixture_lst,
                                model_name,
                                output_dir,
                                file_name_modifier="")


if __name__ ==  '__main__':

    main()