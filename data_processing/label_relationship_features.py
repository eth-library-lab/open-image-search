# get create a feature vector based on the classification of each record

import pandas as pd
import label_utils as lu


if __name__ == '__main__':

    fpath="../data/interim/zbz/metadata/metadata.csv"
    class_dict = lu.load_fixture_to_dict("../data/processed/lists/Relationship.json")
     
    df = pd.read_csv(fpath, usecols=["relationship_type"])
    # join the classification and mat_tec columns the data is often overlapped between them
    input_ser = df['relationship_type'].astype(str)

    print("\n---input_ser----\n", input_ser.head(10), "\n")
    output_ser = lu.process_series(input_ser, class_dict)
    
    print("\n---output_ser----\n", output_ser.head(10), "\n")
    
    print(output_ser.apply(len).max())