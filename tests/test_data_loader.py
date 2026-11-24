import pandas as pd
import pytest
from src.data_loader import load_csv


def test_load_csv_success(tmp_path):
    file_path = tmp_path / "test.csv"

    df = pd.DataFrame({
        "product": ["Laptop", "Mouse"],
        "units_sold": [5, 10]
    })

    df.to_csv(file_path, index=False)

    result = load_csv(file_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == ["product", "units_sold"]

def test_load_csv_wrong(tmp_path):
    file_path = tmp_path / "random.csv"
    with pytest.raises(FileNotFoundError) as err:
        load_csv(file_path)
    assert "File not found" in str(err.value)


def test_load_csv_wrong_extension(tmp_path):
    file_path = tmp_path / "random.txt"
    file_path.write_text("some text")
    with pytest.raises(ValueError):
        load_csv(file_path)

def test_load_csv_empty_file(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.touch()
    with pytest.raises(ValueError):
        load_csv(file_path)
