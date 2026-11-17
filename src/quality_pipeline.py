from src.data_validator import generate_quality_report, load_rules
from src import data_cleaner
from src.data_loader import load_csv


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

rules = load_rules("../config/data_rules.json")

df, initial_report, cleaned_df, final_report, cleaning_summary = run_quality_pipeline(
    "../data/dirty_sample.csv",
    ["region", "product"],
    rules
)

print(cleaning_summary)