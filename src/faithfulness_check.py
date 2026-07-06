from pathlib import Path
import logging
import pandas as pd

from evidence_extractor import EvidenceExtractor
from forecast_model import ForecastModel

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class FaithfulnessCheck:

    def __init__(self, prediction_csv: str, valid_news_csv: str):
        self.prediction_path = Path(prediction_csv)
        self.valid_news_path = Path(valid_news_csv)

        if not self.prediction_path.exists():
            raise FileNotFoundError(f"Không tìm thấy: {prediction_csv}")

        self.df = pd.read_csv(self.prediction_path)

        # Tái sử dụng tầng trích xuất và tầng mô hình dự báo xu hướng
        self.extractor = EvidenceExtractor(str(self.valid_news_path))
        self.model = ForecastModel(str(self.prediction_path))

    def run_experiments(
        self, output_file="outputs/faithfulness_check_results.csv"
    ):
        
        results = []

        for _, row in self.df.iterrows():
            original_news = row["news_text"]
            original_evidence = row["evidence_text"]
            original_conf = float(row["confidence"])
            original_pred = row["prediction"]

            # -------------------------------------------------------------
            # 1. Sufficiency Test: Chỉ dùng các từ khóa bằng chứng để dự báo
            # -------------------------------------------------------------
            suff_out = self.extractor.extract(original_evidence)
            suff_evidence = suff_out[0]
            suff_sentiment = suff_out[1]

            # Tạo mock row truyền vào predict_row
            suff_mock_row = {
                "evidence_text": original_evidence, 
                "sentiment": suff_sentiment
            }
            suff_res = self.model.predict_row(suff_mock_row)

            # SỬA LẠI INDEX THEO ĐÚNG SERIES TRẢ VỀ CỦA FORECAST_MODEL
            suff_conf = suff_res[5]  # Lấy đúng giá trị confidence (Index 5)
            suff_pred = suff_res[6]  # Lấy đúng nhãn "UP"/"DOWN"/"HOLD" (Index 6)

            # -------------------------------------------------------------
            # 2. Counterfactual Perturbation: Thay thế bằng một câu trung lập
            # -------------------------------------------------------------
            counterfactual_text = (
                "The company holds its annual investor meeting."
            )

            count_out = self.extractor.extract(counterfactual_text)
            count_evidence = count_out[0]
            count_sentiment = count_out[1]

            # Tạo mock row cho câu giả định
            count_mock_row = {
                "evidence_text": count_evidence, 
                "sentiment": count_sentiment
            }
            count_res = self.model.predict_row(count_mock_row)

            # SỬA LẠI INDEX ĐỂ ĐỒNG BỘ TUYỆT ĐỐI
            confidence_before = original_conf
            confidence_after = count_res[5]        # Lấy đúng confidence sau can thiệp (Index 5)
            counterfactual_pred = count_res[6]     # Lấy đúng prediction sau can thiệp (Index 6)

            # Tính toán mức độ sụt giảm độ tự tin (Confidence Drop)
            confidence_drop = confidence_before - confidence_after

            results.append({
                "news_text": original_news,
                "prediction": original_pred,
                "confidence_before": confidence_before,
                "sufficiency_pred": suff_pred,
                "sufficiency_conf": suff_conf,
                "counterfactual_news": counterfactual_text,
                "counterfactual_pred": counterfactual_pred,
                "confidence_after": confidence_after,
                "confidence_drop": confidence_drop,
            })

        df_results = pd.DataFrame(results)

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        df_results.to_csv(output_file, index=False)
        logging.info(f"Đã xuất kết quả faithfulness tại: {output_file}")

        return df_results


def main():
    checker = FaithfulnessCheck(
        prediction_csv="outputs/prediction_results.csv",
        valid_news_csv="outputs/valid_news.csv",
    )
    checker.run_experiments()


if __name__ == "__main__":
    main()