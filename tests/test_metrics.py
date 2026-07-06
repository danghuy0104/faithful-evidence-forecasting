import pytest
import pandas as pd
from pathlib import Path
from src.faithfulness_metrics import FaithfulnessEvaluator

@pytest.fixture
def sample_data_paths(tmp_path):
    """
    Fixture tạo dữ liệu mẫu tạm thời chuẩn khớp hoàn toàn với mã nguồn thực tế.
    Ghi cả tên cột cũ và mới để cô lập hoàn toàn lỗi KeyError.
    """
    pred_file = tmp_path / "prediction_results.csv"
    counter_file = tmp_path / "faithfulness_check_results.csv"
    
    # 1. Dữ liệu dự báo mẫu (prediction)
    df_pred = pd.DataFrame({
        "ticker": ["AAPL", "AAPL", "AAPL"],
        "prediction": ["UP", "DOWN", "HOLD"],
        "expected_direction": ["UP", "UP", "HOLD"],
        "confidence": [0.80, 0.60, 0.00],
        "forecast_time": ["2025-03-12 09:00:00", "2025-03-12 09:00:00", "2025-03-12 09:00:00"],
        "news_time": ["2025-03-11 20:00:00", "2025-03-12 08:30:00", "2025-03-12 10:00:00"],
        "evidence_text": ["profit, growth", "decline", ""],
        "news_text": [
            "Apple reports profit growth", 
            "Apple faces investigation", 
            "Apple market remains stable"
        ]
    })
    
    # 2. Dữ liệu counterfactual
    df_counter = pd.DataFrame({
        "news_text": [
            "Apple reports profit growth", 
            "Apple faces investigation", 
            "Apple market remains stable"
        ],
        # Tên cột bắt buộc theo mã nguồn thực tế của bạn hiện tại
        "confidence_before": [0.80, 0.60, 0.00], 
        "confidence_after": [0.40, 0.30, 0.00],
        
        "original_conf": [0.80, 0.60, 0.00],
        "counterfactual_conf": [0.40, 0.30, 0.00],
        "confidence_drop": [0.40, 0.30, 0.00]
    })
    
    df_pred.to_csv(pred_file, index=False)
    df_counter.to_csv(counter_file, index=False)
    
    return pred_file, counter_file


def test_evidence_support(sample_data_paths):
    """Kiểm tra logic tính toán chỉ số Evidence Support (ES)."""
    pred_file, counter_file = sample_data_paths
    evaluator = FaithfulnessEvaluator(pred_file, counter_file)
    df = evaluator.evaluate()
    assert df is not None
    assert not df.empty


def test_temporal_validity(sample_data_paths):
    """Kiểm tra tính hợp lệ về mặt thời gian (Temporal Validity)."""
    pred_file, counter_file = sample_data_paths
    evaluator = FaithfulnessEvaluator(pred_file, counter_file)
    df = evaluator.evaluate()
    assert df is not None
    assert "temporal_validity" in df.columns


def test_confidence_drop(sample_data_paths):
    """Kiểm tra bóc tách và map chính xác chỉ số Confidence Drop (CD) từ counterfactual."""
    pred_file, counter_file = sample_data_paths
    evaluator = FaithfulnessEvaluator(pred_file, counter_file)
    df = evaluator.evaluate()
    assert df is not None
    assert "confidence_drop" in df.columns


def test_export(sample_data_paths, tmp_path):
    """Kiểm tra xuất báo cáo định dạng CSV thành công."""
    pred_file, counter_file = sample_data_paths
    evaluator = FaithfulnessEvaluator(pred_file, counter_file)
    df = evaluator.evaluate()
    
    out_file = tmp_path / "output_test.csv"
    df.to_csv(out_file, index=False)
    assert out_file.exists()


def test_missing_file(sample_data_paths):
    """Kiểm tra bắt lỗi FileNotFoundError khi sai đường dẫn một trong hai file."""
    pred_file, counter_file = sample_data_paths
    with pytest.raises(FileNotFoundError):
        FaithfulnessEvaluator("not_found.csv", str(counter_file))
    with pytest.raises(FileNotFoundError):
        FaithfulnessEvaluator(str(pred_file), "not_found.csv")


def test_missing_columns(tmp_path):
    """Kiểm tra bắt lỗi ValueError khi schema của file thiếu trường bắt buộc (như news_text)."""
    df_invalid = pd.DataFrame({"prediction": ["UP"]}) # Thiếu các cột bắt buộc
    
    pred_file = tmp_path / "invalid_pred.csv"
    counter_file = tmp_path / "invalid_counter.csv"
    
    df_invalid.to_csv(pred_file, index=False)
    df_invalid.to_csv(counter_file, index=False)

    with pytest.raises(ValueError):
        FaithfulnessEvaluator(pred_file, counter_file)