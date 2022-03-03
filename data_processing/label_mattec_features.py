import pandas as pd

import label_utils as lu


def label_series(input_ser:pd.Series) -> pd.Series:

    class_dict = lu.load_fixture_to_dict("../data/processed/lists/MaterialTechnique.json")

    input_ser = input_ser.astype(str)
    output_ser = lu.process_series(input_ser, class_dict)

    return output_ser


if __name__ == '__main__':


    df = pd.read_csv("../data/interim/zbz/metadata/metadata.csv", usecols=["classification","material_technique"])
    # join the classification and mat_tec columns the data is often overlapped between them
    input_ser = df['classification'].astype(str) + ", " + df['material_technique'].astype(str)
    output_ser = label_series(input_ser)

    print(output_ser.apply(len).max())