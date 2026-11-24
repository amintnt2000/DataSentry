import pandas as pd
import numpy as np
from src.data_analyzer import check_missing_values, check_duplicates, check_unique_values, analyze_dtype

def test_missing_values():
    df = pd.DataFrame({"product":[float("nan"), "Mouse"],
                   "units_sold": [5, 10]
                   })

    result = check_missing_values(df)
    null, per_null, row_null = result

    assert null["product"] == 1
    assert null["units_sold"] == 0
    assert per_null["product"] == 50
    assert len(row_null) == 1

def test_missing_values_no_nulls():
    df = pd.DataFrame({"product":["Laptop", "Mouse", "Keyboard"],
                   "units_sold": [5, 10, 15]
                   })
    result = check_missing_values(df)
    null, per_null, row_null = result

    assert null["product"] == 0
    assert null["units_sold"] == 0
    assert per_null["product"] == 0
    assert per_null["units_sold"] == 0
    assert row_null.empty is True

def test_check_duplicates():
    df = pd.DataFrame({"product":["Laptop", "Mouse", "Keyboard", "Mouse"],
                   "units_sold": [5, 10, 15, 10]
                   })
    result = check_duplicates(df)
    duplicate, pre_duplicate, row_duplicate = result

    assert duplicate == 1
    assert pre_duplicate == 25
    assert isinstance(row_duplicate, pd.DataFrame)
    assert len(row_duplicate) == 1

def test_unique_values():
    df = pd.DataFrame({"product": ["Laptop","Mouse","Laptop","Keyboard","Mouse"],
                       "region": ["London","Berlin","London","Paris","Berlin"]})
    result = check_unique_values(df)
    assert isinstance(result, dict)
    assert len(result["product"]["unique"]) == 3
    assert len(result["region"]["unique"]) == 3
    assert result["product"]["counts"]["Laptop"] == 2
    assert result["region"]["counts"]["London"] == 2

def test_analyze_dtype():
    df = pd.DataFrame({"product":["Laptop", "Mouse", "Keyboard"],
                    "units_sold": [5, 10, 15],
                    "region": ["London", "Berlin", "Paris"],
                    "unit_price": [1000, 100, 150]
                   })
    result = analyze_dtype(df)
    assert result["dtypes"]["product"] == "str"
    assert np.issubdtype(result["dtypes"]["units_sold"], np.number) is True
    assert result["dtypes"]["region"] == "str"
    assert np.issubdtype(result["dtypes"]["unit_price"], np.number) is True
    assert result["numeric_columns"].tolist() == ['units_sold', 'unit_price']
    assert result["non_numeric_columns"].tolist() == ['product', 'region']
