import pytest
import os, sys
sys.path.append("../src")

import utils


snake_case_test_cases = [
    ("snake_case", True),
    ("snake", True),
    ("snake2", True),
    ("snake_", False), 
    ("SNAKE", False),
    ("snake__case", False),
    ("snake_case!", False)]
@pytest.mark.parametrize("test_input, expected",snake_case_test_cases)
def test_is_snake_case(test_input, expected):

    assert expected == utils.is_snake_case(test_input)