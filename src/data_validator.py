import pandas as pd
import numpy as np
import json
from src.data_analyzer import check_duplicates
from src.data_cleaner import check_invalid_categories

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
            if df[column].empty:
                if expected_type == "numeric":
                    if pd.api.types.is_numeric_dtype(df[column]) is not True:
                        incorrect.append([column, expected_type])
                elif expected_type == "string":
                    if pd.api.types.is_string_dtype(df[column]) is not True:
                        incorrect.append([column, expected_type])
            else:
                if expected_type == "numeric":
                    if pd.to_numeric(df[column], errors="coerce").notna().sum() > 0:
                        pass
                    else:
                        incorrect.append([column, expected_type])
                elif expected_type == "string":
                    if df[column].apply(lambda val: isinstance(val, str)).sum() > 0:
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
        if pd.isna(value):
            continue
        try:
            numeric = pd.to_numeric(value)
            if numeric < value_range["min"] :
                 unexpected += 1
            if numeric > value_range["max"] :
                 unexpected += 1
        except(ValueError, TypeError):
            continue
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

def calculate_quality_score(report, df, rules):
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

    cat_val = 0
    counter = 0
    category_dict = calculate_category_validity(df, rules)
    if not category_dict:
        category_validity = None
    else:
        for val in category_dict.values():
            if val is None:
                category_validity = None
                break
            elif isinstance(val, (int, float, np.number)):
                cat_val += val
                counter += 1
                category_validity = cat_val / counter
            else:
                category_validity = 0

    sum_range = 0
    counter = 0
    for val in report["out_of_range_percentage"].values():
        if val is not None:
            sum_range += val
            counter += 1
    if counter != 0:
        out_of_range = sum_range / counter
    else:
        out_of_range = None
    if out_of_range is not None:
        range_validity = 100 - out_of_range
    else:
        range_validity = None
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

    if len(rules["required_columns"]) != 0:
        schema_validity = 100 - (len(report["missing_columns"]) / len(rules["required_columns"])) * 100
    else:
        schema_validity = None

    metrics = [
        completeness,
        uniqueness,
        validity,
        category_validity,
        range_validity,
        schema_validity
    ]

    valid_metrics = [value for value in metrics if value is not None]
    if len(valid_metrics) != 0:
        grade = (sum(valid_metrics)) / len(valid_metrics)
    else:
        grade = None
    return grade

def calculate_category_validity(df, rules):
    not_allowed = {}
    error = {}
    category_validity = {}
    for column in df.columns:
        if column in rules["allowed_categories"]:
            not_allowed[column] = (sum(~df[column].isin(rules["allowed_categories"][column])))
    for key, val in not_allowed.items():
        if len(df) == 0 :
            error[key] = None
        else:
            error[key] = val /len(df) * 100
    for key, val in error.items():
        if val is None:
            category_validity[key] = None
        else:
            category_validity[key] = 100 - val
    return category_validity

def generate_quality_report(df, columns:list, rules: dict):
    report = {
        "out_of_range_percentage": {},
        "out_of_range_count": {},
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
    for column, value_range in rules["value_ranges"].items():
        if column in df.columns:
            report["out_of_range_count"][column] = check_value_range(df, column, value_range)
    for key, value in report["out_of_range_count"].items():
        report["out_of_range_percentage"][key] = calculate_error_percentage(value, len(df))
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
    score = calculate_quality_score(report, df, rules)
    if score is None:
        report["quality_score"] = None
    elif score < 0:
        report["quality_score"] = 0
    elif score > 100:
        report["quality_score"] = 100
    else:
        report["quality_score"] = score
    return report

