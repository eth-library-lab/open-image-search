import pytest
import numpy as np
import pandas as pd
import re
import os, sys
sys.path.append("../src")

from process_metadata import clean_df, process_eth_metadata
from utils import is_snake_case

@pytest.fixture()
def df_raw_sample():
    "return a sample dataframe"
    
    np.random.seed(1)
    ages = [0, 1, 1, 2, 3, np.nan]
    rows = len(ages)
    classes = ["a","b","b","c","d", np.nan]
    data = {"age":ages, "class": classes}
    return pd.DataFrame(data)


@pytest.fixture()
def df_clean_sample():
    "return a sample dataframe"
    ages = [0, 1, 7, 1, 2, np.nan, 3]
    rows = len(ages)
    classes = ["a","b", "d","e","f","g"]
    data = {"age":ages, "class": classes}
    return pd.DataFrame(data)

@pytest.fixture()
def df_eth_raw():

    data = {
        'recordID': {
            0: 14943, 
            1: 17626, 
            2: 12789, 
            3: 10098
            },
        'imageURL': {
            0: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=14943&resolution=mediumImageResolution',
            1: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=17626&resolution=mediumImageResolution',
            2: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=12789&resolution=mediumImageResolution',
            3: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=10098&resolution=mediumImageResolution',
            },
        'invNr': {
            0: '1916.0047.1',
            1: '1916.0047.1-6',
            2: '1916.0047.2',
            3: '1916.0047.3'
            },
        'person': {
            0: 'Vallotton, Félix (1865 - 1925), Künstler',
            1: 'Vallotton, Félix (1865 - 1925), Künstler, Herausgeber',
            2: 'Vallotton, Félix (1865 - 1925), Künstler',
            3: 'Vallotton, Félix (1865 - 1925), Künstler',
            },
        'date': {
            0: 'Enstehung des Druckträgers: 1915',
            1: 'Enstehung des Druckträgers: 1915 - 1916',
            2: 'Enstehung des Druckträgers: 1915',
            3: 'Enstehung des Druckträgers: 1916',
            },
        'title': {
            0: 'La tranchée, Blatt Nr. 1 aus "C\'est la guerre"',
            1: "C'est la guerre",
            2: 'L\'orgie, Blatt Nr. 2 aus "C\'est la guerre"',
            3: 'Les fils de fer, Blatt Nr. 3 aus "C\'est la guerre"',
            },
        'classification': {
            0: 'Druckgraphik',
            1: 'Druckgraphik',
            2: 'Druckgraphik',
            3: 'Druckgraphik',
            },
        'matTec': {
            0: 'Holzschnitt',
            1: 'Holzschnitt',
            2: 'Holzschnitt',
            3: 'Holzschnitt',
            },
        'institutionIsil': {
            0: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            1: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            2: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            3: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            },
        'recordURL': {
            0: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=14943&viewType=detailView',
            1: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=17626&viewType=detailView',
            2: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=12789&viewType=detailView',
            3: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=10098&viewType=detailView',
            },
        'imageLicence': {
            0: 'Public Domain Mark 1.0',
            1: 'Public Domain Mark 1.0',
            2: 'Public Domain Mark 1.0',
            3: 'Public Domain Mark 1.0',
            },
        'timestamp': {
            0: '2020-06-25T20:22:59.957Z',
            1: '2020-06-25T20:45:41.43Z',
            2: '2020-06-25T20:11:40.1Z',
            3: '2020-06-25T19:57:32.323Z',
            },
        }

    return pd.DataFrame(data)


@pytest.fixture()
def df_eth_raw():

    data = {
        'recordID': {
            0: 14943,
            0: 14943, 
            1: 17626, 
            2: 12789, 
            3: 10098,
            4: np.nan
            },
        'image_url': {
            0: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=14943&resolution=mediumImageResolution',
            0: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=14943&resolution=mediumImageResolution',
            1: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=17626&resolution=mediumImageResolution',
            2: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=12789&resolution=mediumImageResolution',
            3: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ImageAsset&module=collection&objectId=10098&resolution=mediumImageResolution',
            4: np.nan,
            },
        'inventory_number': {
            0: '1916.0047.1',
            0: '1916.0047.1',
            1: '1916.0047.1-6',
            2: '1916.0047.2',
            3: '1916.0047.3',
            4: np.nan
            },
        'person': {
            0: 'Vallotton, Félix (1865 - 1925), Künstler',
            0: 'Vallotton, Félix (1865 - 1925), Künstler',
            1: 'Vallotton, Félix (1865 - 1925), Künstler, Herausgeber',
            2: 'Vallotton, Félix (1865 - 1925), Künstler',
            3: 'Vallotton, Félix (1865 - 1925), Künstler',
            4: np.nan,
            },
        'date': {
            0: 'Enstehung des Druckträgers: 1915',
            0: 'Enstehung des Druckträgers: 1915',
            1: 'Enstehung des Druckträgers: 1915 - 1916',
            2: 'Enstehung des Druckträgers: 1915',
            3: 'Enstehung des Druckträgers: 1916',
            4: np.nan,
            },
        'title': {
            0: 'La tranchée, Blatt Nr. 1 aus "C\'est la guerre"',
            0: 'La tranchée, Blatt Nr. 1 aus "C\'est la guerre"',
            1: "C'est la guerre",
            2: 'L\'orgie, Blatt Nr. 2 aus "C\'est la guerre"',
            3: 'Les fils de fer, Blatt Nr. 3 aus "C\'est la guerre"',
            4: np.nan,
            },
        'classification': {
            0: 'Druckgraphik',
            0: 'Druckgraphik',
            1: 'Druckgraphik',
            2: 'Druckgraphik',
            3: 'Druckgraphik',
            4: np.nan,
            },
        'material_technique': {
            0: 'Holzschnitt',
            0: 'Holzschnitt',
            1: 'Holzschnitt',
            2: 'Holzschnitt',
            3: 'Holzschnitt',
            4: np.nan,
            },
        'institution_isil': {
            0: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            0: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            1: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            2: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            3: 'Graphische Sammlung ETH Zürich (CH-000511-9)',
            4: np.nan,
            },
        'record_url': { 
            0: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=14943&viewType=detailView',
            0: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=14943&viewType=detailView',
            1: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=17626&viewType=detailView',
            2: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=12789&viewType=detailView',
            3: 'https://e-gs.ethz.ch/eMP/eMuseumPlus?service=ExternalInterface&module=collection&objectId=10098&viewType=detailView',
            4: np.nan,
            },
        'image_licence': {
            0: 'Public Domain Mark 1.0',
            0: 'Public Domain Mark 1.0',
            1: 'Public Domain Mark 1.0',
            2: 'Public Domain Mark 1.0',
            3: 'Public Domain Mark 1.0',
            4: np.nan,
            },
        'timestamp': {
            0: '2020-06-25T20:22:59.957Z',
            0: '2020-06-25T20:22:59.957Z',
            1: '2020-06-25T20:45:41.43Z',
            2: '2020-06-25T20:11:40.1Z',
            3: '2020-06-25T19:57:32.323Z',
            },
    }

    return pd.DataFrame(data)

class TestCleanDf():

    def test_no_nan_rows(self, df_raw_sample):

        res = clean_df(df_raw_sample)
        assert 0 == res.isna().sum().sum()


    def test_output(self, df_raw_sample):
        data = {"age" : [0.0, 1.0, 2.0, 3.0],
                "class" : ["a","b","c","d"]
            }
        ans = pd.DataFrame(data, index=[0,1,3,4], )
        res = clean_df(df_raw_sample)
        pd.testing.assert_frame_equal(ans, res, check_like=True, check_frame_type=False)


class TestProcessEthMetadata():

    def test_columns_are_snake_case(self, df_eth_raw):
        """
        check that all cleaned column names are in snake_case
        """

        df = process_eth_metadata(df_eth_raw)
        cols = df.columns
        for col in cols:
            assert True == is_snake_case(col), "failed column: {}".format(col)


    def test_check_field_names_match_django(self, df_eth_raw):
        """
        test that columns are the same as the Django model class
         in backend/api/ImageSearch/models
        """

        image_metadata_cols = ["record_id",
            "created_date",
            "title",
            "image_url",
            "record_url",
            "inventory_number",
            "person",
            "date",
            "classification",
            "material_technique",
            "institution_isil",
            "image_licence"]

        df = process_eth_metadata(df_eth_raw)
        cols = df.columns

        for col in cols:
            assert col in image_metadata_cols, "failed column: {}".format(col)

