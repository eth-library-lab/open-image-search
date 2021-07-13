import os, sys
sys.path.append("../src")

import settings

# def test_always_fail():
#     print(settings.BASE_DIR)
#     assert 1 == 2, "this is supposed to fail"


def test_type():
    assert list == type(settings.metadata_csvs)


def test_num_neighbours():
    assert int == type(settings.num_neighbours)


def test_batch_size():
    assert int == type(settings.batch_size)
