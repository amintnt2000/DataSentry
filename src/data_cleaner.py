import pandas as pd

df = pd.read_csv(r"C:\Users\Meta Pc\PycharmProjects\DataSentry\data\dirty_sample.csv")

def remove_duplicates(df):
    df_copy = df.copy()
    df_copy = df_copy.drop_duplicates()
    return df_copy

def handle_missing_values(df):
    df_copy = df.copy()
    group = df_copy.groupby("product")["unit_price"].transform("median")
    df_copy["unit_price"] =  df_copy["unit_price"].fillna(group)
    df_copy = df_copy.dropna(subset=["unit_price"])
    return df_copy

def handle_invalid_numeric(df):
    df_copy = df.copy()
    df_copy["units_sold"] = pd.to_numeric(df_copy["units_sold"], errors="coerce")
    df_copy = df_copy.dropna(subset=["units_sold"])
    return df_copy

def check_invalid_categories(df, column, allowed_values):
    return df.loc[~df[column].isin(allowed_values), column].value_counts()