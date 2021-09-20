
| input                 | |       operation     | |        output          | notes |
|---------------------  |-|---------------------|-|------------------------|----|
| raw/metadata.csv      |⇒| clean metadata     |⇒| interim/{dataset}/metadata.csv  | |
| interim/metadata.csv  |⇒| download images    |⇒| raw/{dataset}/images/ | |
| raw/{dataset}/images/ |⇒| preprocess images  |⇒| processed/{dataset}/images/  | |
| processed/{dataset}/images/ |⇒| calculate features |⇒| interim/{dataset}/features.csv  | |
| interim/{dataset}/features.csv <br/> processed/{dataset}/images/ |⇒| create_recommender |⇒| models/retrieval <br/> models/retrieval_exclusion  | images are for testing and tracing the model graph |
| interim/{dataset}/metadata.csv |⇒| process_metadata |⇒| processed/fixtures/*.json <br/> processed/metadata.csv  | |

-----------------------

_ tables will be eventually write to spark tables instead of csvs _
