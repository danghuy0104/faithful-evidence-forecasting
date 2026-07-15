from pathlib import Path
import logging

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

from signals import POSITIVE_SET, NEGATIVE_SET

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


class ForecastModel:
    """
    score = positive_count - negative_count

    score > 0  -> UP
    score < 0  -> DOWN
    score = 0  -> HOLD
    """

    def __init__(self, csv_file: str):
        csv_path = Path(csv_file)

        if not csv_path.exists():
            raise FileNotFoundError(csv_file)

        self.df = pd.read_csv(csv_path)

        required = {
            "evidence_text",
            "sentiment",
            "label"
        }

        missing = required - set(self.df.columns)
        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

    def predict_row(self, row):
        evidence_str = str(row.get("evidence_text", "")).strip()
        sentiment = str(row.get("sentiment", "")).lower()

        pro_ev_list = []
        counter_ev_list = []

        # 1. Phân loại cụm tín hiệu (đã trích ở evidence_text) vào nhóm ủng hộ /
        #    chống lại, dùng chung từ điển signals.py để không lệch với extractor.
        if evidence_str and evidence_str.lower() != "nan" and evidence_str != "":
            keywords = [k.strip().lower() for k in evidence_str.split(",")]
            for kw in keywords:
                if kw in POSITIVE_SET:
                    pro_ev_list.append(kw)
                elif kw in NEGATIVE_SET:
                    counter_ev_list.append(kw)
        
        # 2. Lấy số lượng đếm chính xác dựa trên danh sách từ khóa đã phân loại
        positive = len(pro_ev_list)
        negative = len(counter_ev_list)

        # Nếu không bắt được từ khóa nào cụ thể, sử dụng nhãn sentiment tổng thể
        if positive == 0 and negative == 0:
            if sentiment == "positive":
                positive = 1
                pro_ev_list.append("positive")
            elif sentiment == "negative":
                negative = 1
                counter_ev_list.append("negative")

        # Chuyển mảng từ khóa thành chuỗi phân tách bằng dấu phẩy để ghi vào CSV
        pro_evidence = ", ".join(pro_ev_list) if pro_ev_list else ""
        counter_evidence = ", ".join(counter_ev_list) if counter_ev_list else ""

        # 3. Tính toán các chỉ số dự báo và độ tin cậy theo tài liệu báo cáo
        score = positive - negative

        if score > 0:
            prediction = "UP"
        elif score < 0:
            prediction = "DOWN"
        else:
            prediction = "HOLD"

        total = positive + negative
        
        confidence = (
            abs(score) / total
            if total > 0
            else 0.0
        )
        confidence = round(confidence, 2)

        return pd.Series(
            [
                pro_evidence,
                counter_evidence,
                positive,
                negative,
                score,
                confidence,
                prediction
            ]
        )

    def run(self):
        self.df[
            [
                "pro_evidence",
                "counter_evidence",
                "positive_count",
                "negative_count",
                "score",
                "confidence",
                "prediction"
            ]
        ] = self.df.apply(
            self.predict_row,
            axis=1
        )

        return self.df

    def evaluate(self):
        labels = ["UP", "DOWN", "HOLD"]

        accuracy = accuracy_score(
            self.df["label"],
            self.df["prediction"]
        )

        cm = confusion_matrix(
            self.df["label"],
            self.df["prediction"],
            labels=labels
        )

        # Chuyển Confusion Matrix thành DataFrame có tiêu đề Hàng/Cột rõ ràng
        cm_df = pd.DataFrame(
            cm,
            index=[f"Actual_{l}" for l in labels],
            columns=[f"Pred_{l}" for l in labels]
        )

        report = classification_report(
            self.df["label"],
            self.df["prediction"],
            labels=labels,
            zero_division=0
        )

        logging.info("=" * 50)
        logging.info(f"Accuracy : {accuracy:.2%}")
        logging.info("\nConfusion Matrix:\n%s", cm_df)
        logging.info("\nClassification Report:\n%s", report)

        return accuracy, cm

    def export(self, output_file="outputs/prediction_results.csv"):
        Path(output_file).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.df.to_csv(
            output_file,
            index=False
        )

        logging.info(
            f"Prediction saved to {output_file}"
        )


def main():
    model = ForecastModel(
        "outputs/evidence_results.csv"
    )

    df = model.run()
    model.evaluate()
    model.export()

    print(df[
        [
            "news_text",
            "pro_evidence",
            "counter_evidence",
            "confidence",
            "prediction",
            "label"
        ]
    ].head())


if __name__ == "__main__":
    main()