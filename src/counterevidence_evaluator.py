from pathlib import Path
import logging
import pandas as pd
from evidence_extractor import EvidenceExtractor

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


class CounterevidenceEvaluator:

    def __init__(self, prediction_csv: str, valid_news_csv: str):
        pred_path = Path(prediction_csv)
        if not pred_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy file kết quả dự báo: {prediction_csv}"
            )

        # Đọc file kết quả dự báo của mô hình
        self.df = pd.read_csv(pred_path)

        # Khởi tạo EvidenceExtractor từ file valid_news.csv theo đúng cấu trúc của bạn
        self.extractor = EvidenceExtractor(valid_news_csv)

    def calculate_coverage(self):
        logging.info(
            "--- Đang tiến hành phân tích Counterevidence ---"
        )

        results_pro = []
        results_counter = []
        results_has_counter = []

        # Duyệt qua từng dòng dữ liệu bằng iterrows
        for _, row in self.df.iterrows():
            pred = str(row["prediction"]).upper()
            text = row["news_text"]

            # Gọi hàm extract có sẵn từ file evidence_extractor.py của bạn
            # Bỏ qua 3 tham số đầu, chỉ lấy pro_list và con_list
            _, _, _, pro_list, con_list = (
                self.extractor.extract(text)
            )

            # Logic xác định bằng chứng thuận (pro) và bằng chứng ngược (counter)
            # dựa trên nhãn 'prediction' thực tế của mô hình
            if pred == "UP":
                pro = pro_list
                # Đối với dự báo tăng (UP), từ khóa tiêu cực chính là bằng chứng ngược
                counter = con_list
                has_counter = len(counter) > 0
            elif pred == "DOWN":
                pro = con_list
                # Đối với dự báo giảm (DOWN), từ khóa tích cực chính là bằng chứng ngược
                counter = pro_list
                has_counter = len(counter) > 0
            else:
                # Đối với nhãn HOLD (trung lập), không tính toán tỷ lệ bao phủ phản bác xu hướng hướng cụ thể
                pro = []
                counter = pro_list + con_list
                has_counter = False

            results_pro.append(", ".join(pro))
            results_counter.append(", ".join(counter))
            results_has_counter.append(has_counter)

        # Gán trực tiếp kết quả vào bản sao của DataFrame gốc để giữ nguyên toàn bộ các cột (ticker, label,...)
        df_res = self.df.copy()
        df_res["pro_evidence"] = results_pro
        df_res["counter_evidence"] = results_counter
        df_res["has_counter"] = results_has_counter

        # Lọc riêng các mẫu dự báo có hướng rõ ràng (UP/DOWN) để tính toán tỷ lệ bao phủ chính xác
        df_directional = df_res[
            df_res["prediction"].isin(["UP", "DOWN"])
        ]

        print(
            f"\n=== Counterevidence Coverage Result ==="
        )
        if not df_directional.empty:
            coverage = df_directional["has_counter"].mean()
            print(
                f"Tỷ lệ bao phủ counter-evidence (cho dự báo UP/DOWN): {coverage:.2%}"
            )
        else:
            print(
                "Không có mẫu dự báo hướng UP/DOWN nào để tính toán tỷ lệ bao phủ."
            )

        return df_res


if __name__ == "__main__":
    
    evaluator = CounterevidenceEvaluator(
        "outputs/prediction_results.csv",
        "outputs/valid_news.csv"
    )

    df_result = evaluator.calculate_coverage()

    df_result.to_csv(
        "outputs/counterevidence_coverage.csv",
        index=False
    )
    print(
        "Đã lưu kết quả phân tích thành công vào: outputs/counterevidence_coverage.csv"
    )