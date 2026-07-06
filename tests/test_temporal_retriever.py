from pathlib import Path

import pandas as pd
import pytest

from src.retriever import TemporalRetriever

@pytest.fixture
def sample_csv(tmp_path):
    """
    Tạo dataset tạm thời để test.
    """

    data = pd.DataFrame({
        "ticker": ["AAPL", "AAPL", "TSLA"],
        "forecast_time": [
            "2025-03-12 09:00:00",
            "2025-03-12 09:00:00",
            "2025-03-12 10:00:00"
        ],
        "news_time": [
            "2025-03-11 20:00:00",   # valid
            "2025-03-12 15:00:00",   # future
            "2025-03-12 09:30:00"    # valid
        ],
        "news_text": [
            "Apple sales decline",
            "Future announcement",
            "Tesla launches model"
        ],
        "label": [
            "DOWN",
            "UP",
            "UP"
        ]
    })

    csv_file = tmp_path / "sample.csv"
    data.to_csv(csv_file, index=False)

    return csv_file


def test_dataset_loaded(sample_csv):
    """
    Kiểm tra dataset được đọc thành công.
    """

    retriever = TemporalRetriever(sample_csv)

    assert len(retriever.df) == 3


def test_split_news(sample_csv):
    """
    Kiểm tra Temporal Retriever phân loại đúng.
    """

    retriever = TemporalRetriever(sample_csv)

    valid, invalid = retriever.retrieve()

    assert len(valid) == 2
    assert len(invalid) == 1

    assert all(
        valid["news_time"] <= valid["forecast_time"]
    )

    assert all(
        invalid["news_time"] > invalid["forecast_time"]
    )


def test_export_results(sample_csv, tmp_path):
    """
    Kiểm tra export CSV.
    """

    retriever = TemporalRetriever(sample_csv)

    valid_path = tmp_path / "valid.csv"
    invalid_path = tmp_path / "future.csv"

    valid, invalid = retriever.export_results(
        valid_path=str(valid_path),
        invalid_path=str(invalid_path)
    )

    assert valid_path.exists()
    assert invalid_path.exists()

    valid_df = pd.read_csv(valid_path)
    invalid_df = pd.read_csv(invalid_path)

    assert len(valid_df) == len(valid)
    assert len(invalid_df) == len(invalid)


def test_missing_file():
    """
    Kiểm tra FileNotFoundError.
    """

    with pytest.raises(FileNotFoundError):
        TemporalRetriever("not_exist.csv")


def test_missing_required_columns(tmp_path):
    """
    Kiểm tra thiếu cột bắt buộc.
    """

    df = pd.DataFrame({
        "ticker": ["AAPL"]
    })

    csv_file = tmp_path / "invalid.csv"
    df.to_csv(csv_file, index=False)

    with pytest.raises(ValueError):
        TemporalRetriever(csv_file)


def test_invalid_datetime_removed(tmp_path):
    """
    Kiểm tra record datetime lỗi bị loại bỏ.
    """

    df = pd.DataFrame({
        "ticker": ["AAPL"],
        "forecast_time": ["INVALID"],
        "news_time": ["2025-03-10"],
        "news_text": ["Apple"],
        "label": ["UP"]
    })

    csv_file = tmp_path / "invalid_time.csv"
    df.to_csv(csv_file, index=False)

    retriever = TemporalRetriever(csv_file)

    assert len(retriever.df) == 0


def test_empty_dataset(tmp_path):
    """
    Kiểm tra dataset rỗng.
    """

    df = pd.DataFrame(columns=[
        "ticker",
        "forecast_time",
        "news_time",
        "news_text",
        "label"
    ])

    csv_file = tmp_path / "empty.csv"
    df.to_csv(csv_file, index=False)

    retriever = TemporalRetriever(csv_file)

    valid, invalid = retriever.retrieve()

    assert valid.empty
    assert invalid.empty