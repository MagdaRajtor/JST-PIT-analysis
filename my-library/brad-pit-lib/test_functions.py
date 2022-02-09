import pytest
import pandas as pd
from income import double_names

def test_double_names():
    df1 = pd.DataFrame(data={"nazwa": ["a", "b", "aa", "a", "c"], "ile": [2, 3, 1, 3, 2]})
    assert double_names(df1) == ["a"]
    df2 = pd.DataFrame(data={"name": ["a", "b", "aa", "a", "c"], "ile": [2, 3, 1, 3, 2]})
    with pytest.raises(NameError):
        double_names(df2)

