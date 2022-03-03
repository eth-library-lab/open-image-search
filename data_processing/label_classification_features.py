# get create a feature vector based on the classification of each record

import pandas as pd

import label_utils as lu


def label_series(input_ser:pd.Series) -> pd.Series:

    class_dict = lu.load_fixture_to_dict("../data/processed/lists/Classification.json", 
                                         synonyms = {"druckgraphik":"druckgrafik",})

    input_ser = input_ser.astype(str)
    output_ser = lu.process_series(input_ser, class_dict)

    return output_ser


if __name__ == '__main__':

    fpath="../data/interim/zbz/metadata/metadata.csv"

    df = pd.read_csv(fpath, usecols=["classification","material_technique"])
    # join the classification and mat_tec columns the data is often overlapped between them
    input_ser = df['classification'].astype(str) + ", " + df['material_technique'].astype(str)
    output_ser = label_series(input_ser)

    print("\n---output_ser----\n", output_ser.head(10), "\n")
    
    print(output_ser.apply(len).max())