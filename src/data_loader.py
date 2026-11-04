import pandas as pd
from pathlib import Path


def load_csv(file_path):
    """
    Load a CSV dataset and validate it.
    """

    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    # Check file extension
    if path.suffix.lower() != ".csv":
        raise ValueError(
            "Only CSV files are supported."
        )

    # Read CSV file
    try:
        df = pd.read_csv(path)

    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty.")

    except pd.errors.ParserError:
        raise ValueError("Invalid CSV format.")

    # Check empty dataset
    if df.empty:
        raise ValueError("Dataset contains no rows.")

    return df