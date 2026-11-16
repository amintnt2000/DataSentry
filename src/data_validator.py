import pandas as pd
import numpy as np
import json
from .data_analyzer import check_duplicates
from .data_cleaner import check_invalid_categories

df = pd.read_csv(r"C:\Users\Meta Pc\PycharmProjects\DataSentry\data\dirty_sample.csv")
df_test = df.drop(columns=["region", "unit_price"])
empty_df = pd.DataFrame()

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

def calculate_quality_score(report):
    if isinstance(report["missing_values_percentage"], (int, float, np.number)):
        completeness =  100 - report["missing_values_percentage"]
    elif report["missing_values_percentage"] is None:
        completeness = None
    else:
        completeness = 0
    if isinstance(report["duplicate_percentage"], (int, float, np.number)):
        uniqueness = 100 - report["duplicate_percentage"]
    elif report["duplicate_percentage"] is None:
        uniqueness = None
    else:
        uniqueness = 0
    value = list(report["invalid_numeric_percentage"].values())
    num = 0
    for val in value:
        if val is None:
            num = None
            break
    if num is not None:
        if len(value) != 0:
            num = sum(value) / len(value)
        else:
            num = 0
    if num is not None:
        validity = 100 - num
    else:
        validity = None
    if completeness is not None and uniqueness is not None and validity is not None:
        grade = (completeness + uniqueness + validity) / 3
    else:
        grade = None
    return grade

def generate_quality_report(df, columns:list, rules: dict):
    report = {
    "missing_columns": [],
    "incorrect_types": [],
    "missing_values_percentage":0,
    "duplicate_percentage":0,
    "missing_values_count":0,
    "duplicate_count":0,
    "allowed_categories":{},
    "wrong_categories":{},
    "invalid_numeric_count": {},
    "invalid_numeric_percentage": {},
    "quality_score": 0
    }
    report["missing_columns"] = check_required_columns(df, rules["required_columns"])
    report["incorrect_types"] = check_column_type(df, rules["required_columns_type"])
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
    for column, expected_type in  rules["required_columns_type"].items():
        if expected_type == "numeric":
            if column in df.columns:
                report["invalid_numeric_count"][column] = count_invalid_numeric_values(df, column)
    for column, err in report["invalid_numeric_count"].items():
        report["invalid_numeric_percentage"][column] = calculate_error_percentage(err, len(df))
    score = calculate_quality_score(report)
    if score is None:
        report["quality_score"] = None
    elif score < 0:
        report["quality_score"] = 0
    elif score > 100:
        report["quality_score"] = 100
    else:
        report["quality_score"] = score
    return report
