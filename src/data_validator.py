import pandas as pd
import json
from .data_analyzer import check_duplicates
from .data_cleaner import check_invalid_categories

df = pd.read_csv(r"C:\Users\Meta Pc\PycharmProjects\DataSentry\data\dirty_sample.csv")
df_test = df.drop(columns=["region", "unit_price"])


def check_required_columns(df, required_columns:list):
    missing = []
    for column in required_columns:
        if column not in df.columns:
            missing.append(column)
    return  missing

def check_column_type(df, required_columns_type:dict):
    incorrect = []
    for column, expected_type in required_columns_type.items():
        if column in df.columns:
            if expected_type == "numeric":
                if pd.api.types.is_numeric_dtype(df[column]):
                    pass
                else:
                    incorrect.append([column, expected_type])
            elif expected_type == "string":
                if not pd.api.types.is_numeric_dtype(df[column]):
                    pass
                else:
                    incorrect.append([column, expected_type])
    return incorrect

def count_invalid_numeric_values(df, column):
    counter = 0
    for number in df[column]:
        num = pd.to_numeric(number, errors="coerce")
        if pd.isna(num) is True and pd.isna(number) is not True:
            counter += 1
    return counter

def check_value_range(df, column, value_range):
    unexpected = 0
    for value in df[column]:
        if isinstance(value, (int, float)):
             if value < value_range["min"] :
                 unexpected += 1
             if value > value_range["max"] :
                 unexpected += 1
    return unexpected

def calculate_error_percentage(error_count, total_rows):
    if total_rows > 0:
        return (error_count / total_rows) * 100
    else:
        return None

def load_rules(path):
    with open(path, "r", encoding="utf-8") as f:
        rules = json.load(f)
    return rules

def generate_quality_report(df, columns:list, rules: dict):
    report = {
    "missing_columns": [],
    "incorrect_types": [],
    "invalid_unit_price": 0,
    "invalid_units_sold": 0,
    "unit_price_error_percentage":0,
    "units_sold_error_percentage":0,
    "missing_values_percentage":0,
    "duplicate_percentage":0,
    "missing_values_count":0,
    "duplicate_count":0,
    "allowed_categories":{},
    "wrong_categories":{},
    "invalid_numeric_count": {},
    "invalid_numeric_percentage": {}
    }
    report["missing_columns"] = check_required_columns(df, rules["required_columns"])
    report["incorrect_types"] = check_column_type(df, rules["required_columns_type"])
    if "unit_price" in df.columns:
        report["invalid_unit_price"] = check_value_range(df, "unit_price", rules["value_ranges"]["unit_price"])
    if "units_sold" in df.columns:
        report["invalid_units_sold"] = check_value_range(df, "units_sold", rules["value_ranges"]["units_sold"])
    if "unit_price" in df.columns:
        report["unit_price_error_percentage"] = calculate_error_percentage(report["invalid_unit_price"], len(df))
    if "units_sold" in df.columns:
        report["units_sold_error_percentage"] = calculate_error_percentage(report["invalid_units_sold"], len(df))
    report["missing_values_percentage"] = calculate_error_percentage(df.isnull().sum().sum(), df.size)
    duplicate, pre_duplicate, _ = check_duplicates(df)
    report["duplicate_percentage"] = pre_duplicate
    report["missing_values_count"] = df.isnull().sum().sum()
    report["duplicate_count"] = duplicate
    for column in columns:
        if column in df.columns:
            if column in rules["allowed_categories"]:
                report["allowed_categories"][column] = rules["allowed_categories"][column]
                report["wrong_categories"][column] = check_invalid_categories(df, column, rules["allowed_categories"][column])
    for column, type in  rules["required_columns_type"].items():
        if type == "numeric":
            if column in df.columns:
                report["invalid_numeric_count"][column] = count_invalid_numeric_values(df, column)
    for column, err in report["invalid_numeric_count"].items():
        report["invalid_numeric_percentage"][column] = calculate_error_percentage(err, len(df))
    return report

print(generate_quality_report(df, ["units_sold", "unit_price"], load_rules("../config/data_rules.json")))