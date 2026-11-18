import numpy as np
import pandas as pd
from src.data_validator import generate_quality_report, load_rules
from src import data_cleaner
from src.data_loader import load_csv

rules = load_rules("../config/data_rules.json")

def run_quality_pipeline(path, columns:list, rules):
    df = load_csv(path)
    cleaning_summary = {
        "original_rows": len(df)
    }
    initial_report = generate_quality_report(df, columns, rules)
    df_copy = df.copy()
    df_copy = data_cleaner.remove_duplicates(df_copy)
    cleaning_summary["after_duplicate_removal"] = len(df_copy)
    cleaning_summary["duplicates_removed"] = cleaning_summary["original_rows"] - len(df_copy)
    df_copy = data_cleaner.handle_missing_values(df_copy)
    cleaning_summary["after_handle_missing_value"] = len(df_copy)
    cleaning_summary["handle_missing_value"] = cleaning_summary["after_duplicate_removal"] - len(df_copy)
    df_copy = data_cleaner.handle_invalid_numeric(df_copy)
    cleaning_summary["after_invalid_numeric"] = len(df_copy)
    cleaning_summary["invalid_numeric"] = cleaning_summary["after_handle_missing_value"] - len(df_copy)
    final_report = generate_quality_report(df_copy, columns, rules)
    return (df, initial_report, df_copy, final_report, cleaning_summary)

def generate_cleaning_summary(cleaning_summary):
    return ("DataSentry Cleaning Report\n"
            "--------------------------\n"
            f"Original Rows: {cleaning_summary['original_rows']}\n"
            f"Duplicates Removed: {cleaning_summary['duplicates_removed']}\n"
            f"Rows After Duplicate Removal: {cleaning_summary['after_duplicate_removal']}\n"
            f"Rows Removed During Missing Value Handling: {cleaning_summary['handle_missing_value']}\n"
            f"Rows After Missing Value Handling: {cleaning_summary['after_handle_missing_value']}\n"
            f"Invalid Numeric Rows Removed: {cleaning_summary['invalid_numeric']}\n"
            f"Final Rows: {cleaning_summary['after_invalid_numeric']}\n"
            f"Total Rows Removed: {cleaning_summary['original_rows'] - cleaning_summary['after_invalid_numeric']}")

def generate_quality_summary(report):
    wrong_cat = 0
    for val in report['wrong_categories'].values():
        wrong_cat += val.sum()
    invalid_numeric = 0
    for val in report['invalid_numeric_count'].values():
        invalid_numeric +=  val
    score = 0
    if report['quality_score'] is not None:
        score = f"{report['quality_score']:.2f}"
    else:
        score = "N/A"
    return ("DataSentry Quality Report\n"
            "-------------------------\n"
            f"Quality Score: {score}\n"
            f"Missing Values: {report['missing_values_count']}\n"
            f"Duplicate Rows: {report['duplicate_count']}\n"
            f"Invalid Categories: {wrong_cat}\n"
            f"Invalid Numeric Values: {invalid_numeric}\n"
            f"Missing Columns: {len(report['missing_columns'])}\n"
            f"Incorrect Column Types: {len(report['incorrect_types'])}\n")

def generate_final_report(initial_report, final_report, cleaning_summary):
    initial_quality = generate_quality_summary(initial_report)
    final_quality = generate_quality_summary(final_report)
    cleaning_report = generate_cleaning_summary(cleaning_summary)
    return ("================================\n"
            "DATASENTRY REPORT\n"
            "================================\n"
            "[INITIAL DATA QUALITY]\n"
            f"{initial_quality}\n\n"
            "[CLEANING SUMMARY]\n"
            f"{cleaning_report}\n\n"
            "[FINAL DATA QUALITY]\n"
            f"{final_quality}\n\n"
            "================================")