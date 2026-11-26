import pandas as pd
import numpy as np
from src.data_validator import check_required_columns, check_column_type, count_invalid_numeric_values, check_value_range
from src.data_validator import calculate_error_percentage, calculate_category_validity, calculate_quality_score, generate_quality_report
from src.data_validator import load_rules
from src.quality_pipeline import RULES_PATH


def test_check_required_columns():
    df = pd.DataFrame({"product":[],
                       "region":[]})
    result = check_required_columns(df, ["product", "region", "unit_price"])

    assert isinstance(result, list)
    assert result == ["unit_price"]

def test_check_required_columns_all_exist():
    df = pd.DataFrame({"product":[],
                       "region":[],
                       "unit_price":[]})
    result = check_required_columns(df, ["product", "region", "unit_price"])

    assert isinstance(result, list)
    assert result == []

def test_check_column_type():
    df = pd.DataFrame({"product":["Mouse", "Keyboard"],
                       "region":["London", "Paris"],
                       "unit_price":[100, 200]})
    result = check_column_type(df, {"product":"string", "region":"string", "unit_price":"numeric"})

    assert isinstance(result, list)
    assert result == []

def test_check_column_type_incorrect_num():
    df = pd.DataFrame({"product":["Mouse", "Keyboard"],
                       "region":["London", "Paris"],
                       "unit_price":["100", "200"]})
    result = check_column_type(df, {"product":"string", "region":"string", "unit_price":"numeric"})

    assert isinstance(result, list)
    assert result == []

def test_check_column_type_invalid_num():
    df = pd.DataFrame({"product": ["Mouse", "Keyboard"],
                       "region": ["London", "Paris"],
                       "unit_price": ["unknown", "invalid"]})
    result = check_column_type(df, {"product": "string", "region": "string", "unit_price": "numeric"})

    assert isinstance(result, list)
    assert result == [["unit_price", "numeric"]]

def test_check_column_type_invalid_str():
    df = pd.DataFrame({"product":[1, 2],
                       "region":["London", "Paris"],
                       "unit_price":[100, 200]})
    result = check_column_type(df, {"product":"string", "region":"string", "unit_price":"numeric"})

    assert isinstance(result, list)
    assert result == [["product", "string"]]

def test_check_column_type_mixed_str():
    df = pd.DataFrame({"product": ["Laptop", 20],
                       "region":["London", "Paris"],
                       "unit_price":[100, 200]})
    result = check_column_type(df, {"product":"string", "region":"string", "unit_price":"numeric"})

    assert isinstance(result, list)
    assert result == []

def test_count_invalid_numeric_values():
    df = pd.DataFrame({"units_sold":[10, 20, "unknown", 30, "invalid"]})
    result = count_invalid_numeric_values(df, "units_sold")

    assert result == 2

def test_count_invalid_numeric_values_no_invalid():
    df = pd.DataFrame({"units_sold":[10, 20, 15, 30, 2]})
    result = count_invalid_numeric_values(df, "units_sold")

    assert result == 0

def test_count_invalid_numeric_values_with_nan():
    df = pd.DataFrame({"units_sold": [10, np.nan, "unknown", 20]})
    result = count_invalid_numeric_values(df, "units_sold")

    assert result == 1

def test_check_value_range():
    df = pd.DataFrame({"unit_price":[100, 500, 1200, -10, 800]})
    result = check_value_range(df,"unit_price", {"min": 0, "max": 1000})

    assert result == 2

def test_check_value_range_no_invalid():
    df = pd.DataFrame({"unit_price":[100, 500, 1000, 0, 800]})
    result = check_value_range(df,"unit_price", {"min": 0, "max": 1000})

    assert result == 0

def test_check_value_range_nan():
    df = pd.DataFrame({"unit_price":[100, np.nan, "unknown", 1200]})
    result = check_value_range(df,"unit_price", {"min": 0, "max": 1000})

    assert result == 1

def test_calculate_error_percentage():
    result = calculate_error_percentage(5, 100)

    assert result == 5.0

def test_calculate_error_percentage_zero_rows():
    result = calculate_error_percentage(5, 0)

    assert result is None

def test_calculate_error_percentage_no_errors():
    result = calculate_error_percentage(0, 100)

    assert result == 0.0

def test_calculate_category_validity():
    df = pd.DataFrame({"product":["Laptop", "Mouse", "Atlantis", "Keyboard"],
                       "region":["Berlin", "Paris", "London", "Atlantis"]})
    result = calculate_category_validity(df, {"allowed_categories":{"product":["Laptop", "Mouse", "Keyboard"],
                                                                            "region":["Berlin", "Paris", "London"]}})

    assert result["product"] == 75.0
    assert result["region"] == 75.0

def test_calculate_category_validity_no_invalid():
    df = pd.DataFrame({"product":["Laptop", "Mouse", "Keyboard"],
                       "region":["Berlin", "Paris", "London"]})
    result = calculate_category_validity(df, {"allowed_categories":{"product":["Laptop", "Mouse", "Keyboard"],
                                                                            "region":["Berlin", "Paris", "London"]}})

    assert result["product"] == 100.0
    assert result["region"] == 100.0

def test_calculate_category_validity_empty():
    df = pd.DataFrame({"product":[],
                       "region":[]})
    result = calculate_category_validity(df, {"allowed_categories":{"product":["Laptop", "Mouse", "Keyboard"],
                                                                            "region":["Berlin", "Paris", "London"]}})

    assert result["product"] is None
    assert result["region"] is None


def test_calculate_quality_score_perfect():
    report = {
        "missing_values_percentage": 0,
        "duplicate_percentage": 0,
        "invalid_numeric_percentage": {
            "units_sold": 0,
            "unit_price": 0
        },
        "out_of_range_percentage": {
            "units_sold": 0,
            "unit_price": 0
        }
    }
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard"],
        "region": ["Berlin", "Paris", "London"],
        "units_sold": [10, 20, 15],
        "unit_price": [100, 200, 75]
    })
    rules = {
        "allowed_categories": {
            "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
            "region": ["Berlin", "Paris", "London"]
        }
    }
    result = calculate_quality_score(report, df, rules)

    assert result == 100

def test_calculate_quality_score_with_errors():
    report = {
        "missing_values_percentage": 10,
        "duplicate_percentage": 20,
        "invalid_numeric_percentage": {
            "units_sold": 30,
            "unit_price": 30
        },
        "out_of_range_percentage": {
            "units_sold": 50,
            "unit_price": 50
        }
    }
    df = pd.DataFrame({
    "product": ["Laptop", "Mouse", "Keyboard", "Atlantis", "Unknown"],
    "region": ["Berlin", "Paris", "London", "Atlantis", "Unknown"],
    "units_sold": [10, 20, 15, 30, 40],
    "unit_price": [100, 200, 75, 300, 400]
})
    rules = {
        "allowed_categories": {
            "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
            "region": ["Berlin", "Paris", "London"]
        }
    }
    result = calculate_quality_score(report, df, rules)

    assert result == 70

def test_calculate_quality_score_with_none():
    report = {
        "missing_values_percentage": None,
        "duplicate_percentage": None,
        "invalid_numeric_percentage": {
            "units_sold": None
        },
        "out_of_range_percentage": {
            "unit_price": None
        }
    }
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard"],
        "region": ["Berlin", "Paris", "London"],
        "units_sold": [10, 20, 15],
        "unit_price": [100, 200, 75]
    })
    rules = {
        "allowed_categories": {
            "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
            "region": ["Berlin", "Paris", "London"]
        }
    }
    result = calculate_quality_score(report, df, rules)

    assert  result == 100

def test_calculate_quality_score_all_none():
    report = {
        "missing_values_percentage": None,
        "duplicate_percentage": None,
        "invalid_numeric_percentage": {
            "units_sold": None,
            "unit_price": None
        },
        "out_of_range_percentage": {
            "units_sold": None,
            "unit_price": None
        }
    }
    df = pd.DataFrame({
        "product": [],
        "region": [],
        "units_sold": [],
        "unit_price": []
    })
    rules = {
        "allowed_categories": {
            "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
            "region": ["Berlin", "Paris", "London"]
        }
    }
    result = calculate_quality_score(report, df, rules)

    assert result is None

def test_generate_quality_report_perfect():
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard"],
        "units_sold": [10, 20, 15],
        "unit_price": [100, 200, 75],
        "region": ["Berlin", "Paris", "London"]
    })
    columns = ["product", "region"]
    rules = load_rules(RULES_PATH)
    result = generate_quality_report(df, columns, rules)

    assert isinstance(result, dict)

    assert result["missing_columns"] == []
    assert result["incorrect_types"] == []

    assert result["missing_values_count"] == 0
    assert result["duplicate_count"] == 0

    assert result["wrong_categories"]["product"].empty
    assert result["wrong_categories"]["region"].empty

    assert result["invalid_numeric_count"]["units_sold"] == 0
    assert result["invalid_numeric_count"]["unit_price"] == 0

    assert result["quality_score"] == 100

def test_generate_quality_report_with_errors():
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Atlantis", "Keyboard"],
        "units_sold": [10, 20, 30, 40],
        "unit_price": [100, 200, 1200, 75],
        "region": ["Berlin", "Paris", "Atlantis", "London"]
    })
    columns = ["product", "region"]
    rules = load_rules(RULES_PATH)
    result = generate_quality_report(df, columns, rules)

    assert isinstance(result, dict)

    assert result["missing_columns"] == []
    assert result["incorrect_types"] == []

    assert result["wrong_categories"]["product"].sum() == 1
    assert result["wrong_categories"]["region"].sum() == 1

    assert result["out_of_range_count"]["unit_price"] == 1

    assert result["invalid_numeric_count"]["units_sold"] == 0
    assert result["invalid_numeric_count"]["unit_price"] == 0

    assert result["out_of_range_percentage"]["unit_price"] == 25
    assert result["invalid_numeric_percentage"]["units_sold"] == 0

    assert result["quality_score"] < 100

def test_generate_quality_report_missing_columns():
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard"],
        "region": ["Berlin", "Paris", "London"]
    })
    columns = ["product", "region"]
    rules = load_rules(RULES_PATH)
    result = generate_quality_report(df, columns, rules)

    assert isinstance(result, dict)

    assert result["missing_columns"] == ["units_sold", "unit_price"]
    assert result["incorrect_types"] == []

    assert result["wrong_categories"]["product"].empty
    assert result["wrong_categories"]["region"].empty

    assert result["invalid_numeric_count"] == {}
    assert result["quality_score"] is not None

def test_generate_quality_report_empty_df():
    df = pd.DataFrame({
        "product": pd.Series(dtype="str"),
        "units_sold": pd.Series(dtype="float64"),
        "unit_price": pd.Series(dtype="float64"),
        "region": pd.Series(dtype="str")
    })
    columns = ["product", "region"]
    rules = load_rules(RULES_PATH)

    result = generate_quality_report(df, columns, rules)
    assert isinstance(result, dict)

    assert result["missing_columns"] == []
    assert result["incorrect_types"] == []

    assert result["missing_values_count"] == 0
    assert result["duplicate_count"] == 0

    assert result["quality_score"] is None

def test_generate_quality_report_invalid_numeric():
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
        "units_sold": [10, "unknown", 15, "invalid"],
        "unit_price": [100, 200, 75, 300],
        "region": ["Berlin", "Paris", "London", "Berlin"]
    })
    columns = ["product", "region"]
    rules = load_rules(RULES_PATH)
    result = generate_quality_report(df, columns, rules)

    assert isinstance(result, dict)

    assert result["invalid_numeric_count"]["units_sold"] == 2
    assert result["invalid_numeric_count"]["unit_price"] == 0

    assert result["invalid_numeric_percentage"]["units_sold"] == 50
    assert result["invalid_numeric_percentage"]["unit_price"] == 0

    assert result["quality_score"] < 100

    assert result["wrong_categories"]["product"].empty
    assert result["wrong_categories"]["region"].empty

def test_generate_quality_report_out_of_range():
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
        "units_sold": [10, 20, 1500, 40],
        "unit_price": [100, 1200, 75, -10],
        "region": ["Berlin", "Paris", "London", "Berlin"]
    })
    columns = ["product", "region"]
    rules = load_rules(RULES_PATH)
    result = generate_quality_report(df, columns, rules)

    assert isinstance(result, dict)

    assert result["invalid_numeric_count"]["units_sold"] == 0
    assert result["invalid_numeric_count"]["unit_price"] == 0

    assert result["out_of_range_count"]["units_sold"] == 1
    assert result["out_of_range_count"]["unit_price"] == 2

    assert result["out_of_range_percentage"]["units_sold"] == 25
    assert result["out_of_range_percentage"]["unit_price"] == 50

    assert result["quality_score"] < 100

def test_generate_quality_report_combined_errors():
    df = pd.DataFrame({
        "product": ["Laptop", "Atlantis", "Mouse", "Keyboard"],
        "units_sold": [10, "unknown", 1500, 20],
        "unit_price": [100, 1200, 200, -10],
        "region": ["Berlin", "Atlantis", "Paris", "London"]
    })
    columns = ["product", "region"]
    rules = load_rules(RULES_PATH)
    result = generate_quality_report(df, columns, rules)

    assert isinstance(result, dict)

    assert result["missing_columns"] == []
    assert result["incorrect_types"] == []

    assert result["invalid_numeric_count"]["units_sold"] == 1
    assert result["invalid_numeric_count"]["unit_price"] == 0

    assert result["invalid_numeric_percentage"]["units_sold"] == 25
    assert result["invalid_numeric_percentage"]["unit_price"] == 0

    assert result["out_of_range_count"]["units_sold"] == 1
    assert result["out_of_range_count"]["unit_price"] == 2

    assert result["out_of_range_percentage"]["units_sold"] == 25
    assert result["out_of_range_percentage"]["unit_price"] == 50

    assert result["wrong_categories"]["product"].sum() == 1
    assert result["wrong_categories"]["region"].sum() == 1

    assert result["quality_score"] < 100