import pandas as pd

df = pd.read_csv(r"C:\Users\Meta Pc\PycharmProjects\DataSentry\data\dirty_sample.csv")
df_test = df.drop(columns="region")
required_columns = ["product", "units_sold", "unit_price", "region"]
required_columns_type = {
    "units_sold": "numeric",
    "unit_price": "numeric",
    "product": "string"
}


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

def check_value_range(df, column, main_value):
    unexpected = 0
    for value in df[column]:
        if isinstance(value, (int, float)):
            if value < main_value:
                unexpected += 1
    return unexpected

def generate_quality_report(df):
    report = {
    "missing_columns": [],
    "incorrect_types": [],
    "invalid_unit_price": 0,
    "invalid_units_sold": 0
    }
    report["missing_columns"] = check_required_columns(df, required_columns)
    report["incorrect_types"] = check_column_type(df, required_columns_type)
    report["invalid_unit_price"] = check_value_range(df, "unit_price", 0)
    report["invalid_units_sold"] = check_value_range(df, "units_sold", 0)
    return report

print(generate_quality_report(df))
print(generate_quality_report(df_test))