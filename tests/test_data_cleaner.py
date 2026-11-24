import pandas as pd
import numpy as np
from src.data_cleaner import remove_duplicates, handle_missing_values, handle_invalid_numeric,check_invalid_categories, normalize_categories

def test_remove_duplicates():
    df = pd.DataFrame({"product": ["Laptop", "Mouse", "Keyboard", "Keyboard"],
                        "units_sold": [5, 10, 15, 15],
                        "region": ["London", "Berlin", "Paris", "Paris"],
                        "unit_price": [1000, 100, 150, 150]
                        })
    result = remove_duplicates(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert result.duplicated().any() == False

def test_handle_missing_values():
    df = pd.DataFrame({"product": ["Laptop", "Mouse", "Keyboard", "Laptop"],
                        "units_sold": [5, 10, 15, 5],
                        "region": ["London", "Berlin", "Paris", "London"],
                        "unit_price": [float("nan"), 100, 150, 1000]
                        })
    result = handle_missing_values(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 4
    assert result["unit_price"].isnull().any() == False
    assert result["unit_price"].iloc[0] == 1000

def test_handle_invalid_numeric():
    df = pd.DataFrame({"product": ["Laptop", "Mouse", "Keyboard", "Laptop"],
                        "units_sold": [5, "unknown", 15, 5],
                        "region": ["London", "Berlin", "Paris", "London"],
                        "unit_price": [1000, 100, 150, 1000]
                        })
    result = handle_invalid_numeric(df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert np.issubdtype(result["units_sold"].dtype, np.number)
    assert result["units_sold"].isnull().sum() == 0

def test_check_invalid_categories():
    df = pd.DataFrame({"region": ["London" ,"Berlin" ,"Paris" ,"Atlantis"]})
    result = check_invalid_categories(df, "region", ["London" ,"Berlin" ,"Paris"])
    assert isinstance(result, pd.Series)
    assert result["Atlantis"] == 1
    assert len(result) == 1

def test_normalize_categories():
    df = pd.DataFrame({"product":["laptop", " LAPTOP ", "mouse", "KEYBOARD"]})
    result = normalize_categories(df, {"allowed_categories":{"product":["Laptop", "Mouse", "Keyboard"]}})
    assert isinstance(result, pd.DataFrame)
    assert result["product"].iloc[0] == "Laptop"
    assert result["product"].iloc[1] == "Laptop"
    assert result["product"].iloc[2] == "Mouse"
    assert result["product"].iloc[3] == "Keyboard"