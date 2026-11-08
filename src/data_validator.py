import pandas as pd

df = pd.read_csv(r"C:\Users\Meta Pc\PycharmProjects\DataSentry\data\dirty_sample.csv")
df_test = df.drop(columns="region")

def check_required_columns(df, required_columns:list):
    missing = []
    for column in required_columns:
        if column not in df.columns:
            missing.append(column)
    return  missing

def check_column_type(df, required_columns_type:dict):
    incorrect = []
    for column, type in required_columns_type.items():
        for d_column, d_type in df.dtypes:
            if column == d_column:
                if type != d_type:
                    incorrect.append([column, type])
    return incorrect

print(check_column_type(df_test, {"product": "str"}))



