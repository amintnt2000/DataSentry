import pandas as pd

def check_missing_values(df):
    null = df.isnull().sum()
    rows = len(df)
    if rows > 0:
        per_null = (null / rows) * 100
    else:
        per_null = None

    return  null, per_null, df[df.isnull().any(axis=1)]

def check_duplicates(df):
    duplicate = df.duplicated().sum()
    rows = len(df)
    if rows > 0:
        pre_duplicate = (duplicate / rows) * 100
    else:
        pre_duplicate = None
    return duplicate , pre_duplicate, df[df.duplicated()]

def check_unique_values(df):
    result = {}
    for col in df.columns:
        result[col] = ({"unique" :df[col].unique(),
                        "counts" :df[col].value_counts()})
    return result

def analyze_dtype(df):
    str_columns = df.select_dtypes(include=["object", "str"])
    numeric = df.select_dtypes(include=["number"])

    result = {
        "dtypes": df.dtypes,
        "numeric_columns" : numeric.columns,
        "non_numeric_columns":  str_columns.columns
    }
    return result

