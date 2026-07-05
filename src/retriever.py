from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


class TemporalRetriever:
    """
    Chức năng:
    - Đọc dữ liệu từ file CSV.
    - Kiểm tra dữ liệu đầu vào.
    - Lọc các tin tức hợp lệ theo thời gian.
    - Phát hiện Temporal Leakage.
    - Xuất kết quả thành hai file CSV.
    """

    REQUIRED_COLUMNS = {
        "ticker",
        "forecast_time",
        "news_time",
        "news_text",
        "label"
    }

    def __init__(self, csv_file: str):

        csv_path = Path(csv_file)

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {csv_file}"
            )

        self.df = pd.read_csv(csv_path)

        # Kiểm tra các cột bắt buộc
        missing_columns = self.REQUIRED_COLUMNS - set(self.df.columns)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        # Chuyển sang datetime
        self.df["forecast_time"] = pd.to_datetime(
            self.df["forecast_time"],
            errors="coerce"
        )

        self.df["news_time"] = pd.to_datetime(
            self.df["news_time"],
            errors="coerce"
        )

        # Loại bỏ record lỗi
        self.df.dropna(
            subset=["forecast_time", "news_time"],
            inplace=True
        )

        logging.info(
            f"Dataset loaded successfully "
            f"({len(self.df)} records)"
        )

    def retrieve(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Lọc tin tức theo thời gian.

        valid_news:
            Các tin có news_time <= forecast_time.

        invalid_future_news:
            Các tin có news_time > forecast_time.
        """

        valid_news = self.df[
            self.df["news_time"] <= self.df["forecast_time"]
        ].copy()

        invalid_future_news = self.df[
            self.df["news_time"] > self.df["forecast_time"]
        ].copy()

        return valid_news, invalid_future_news

    def export_results(
        self,
        valid_path: str = "outputs/valid_news.csv",
        invalid_path: str = "outputs/invalid_future_news.csv"
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
    
        # Xuất kết quả sau khi lọc

        # Tạo thư mục output nếu chưa tồn tại
        Path(valid_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        Path(invalid_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        valid_news, invalid_news = self.retrieve()

        valid_news.to_csv(valid_path, index=False)
        invalid_news.to_csv(invalid_path, index=False)

        total = len(self.df)
        leakage_ratio = (
            len(invalid_news) / total
            if total > 0 else 0
        )

        logging.info("=" * 50)
        logging.info("Temporal Retriever Summary")
        logging.info(f"Total Records       : {total}")
        logging.info(f"Valid News          : {len(valid_news)}")
        logging.info(f"Future News         : {len(invalid_news)}")
        logging.info(f"Leakage Ratio       : {leakage_ratio:.2%}")
        logging.info(f"Valid CSV           : {valid_path}")
        logging.info(f"Invalid CSV         : {invalid_path}")
        logging.info("=" * 50)

        return valid_news, invalid_news


def main():

    retriever = TemporalRetriever(
        "data/sample_news_price.csv"
    )

    valid_news, invalid_news = retriever.export_results()

    print("\n========== VALID NEWS ==========")
    print(valid_news.head())

    print("\n===== INVALID FUTURE NEWS =====")
    print(invalid_news.head())


if __name__ == "__main__":
    main()