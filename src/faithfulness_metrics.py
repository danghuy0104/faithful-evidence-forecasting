from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


class FaithfulnessEvaluator:
    """
    Metrics:
    1. Evidence Support
    2. Temporal Validity
    3. Confidence Drop
    """

    def __init__(self, prediction_csv: str, counterfactual_csv: str):

        pred_path = Path(prediction_csv)
        cf_path = Path(counterfactual_csv)

        if not pred_path.exists():
            raise FileNotFoundError(f"Không tìm thấy: {prediction_csv}")
        if not cf_path.exists():
            raise FileNotFoundError(f"Không tìm thấy: {counterfactual_csv}")

        self.df = pd.read_csv(pred_path)
        self.cf_df = pd.read_csv(cf_path)

        required = {
            "prediction",
            "expected_direction",
            "confidence",
            "forecast_time",
            "news_time",
            "evidence_text",
            "news_text"
        }

        missing = required - set(self.df.columns)

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        self.df["forecast_time"] = pd.to_datetime(
            self.df["forecast_time"]
        )

        self.df["news_time"] = pd.to_datetime(
            self.df["news_time"]
        )

        self.cf_mapping = self.cf_df.set_index("news_text").to_dict("index")


    def evidence_support(self, row):
        if row["prediction"] == row["expected_direction"]:
            return 1
        return 0


    def temporal_validity(self, row):
        if row["news_time"] <= row["forecast_time"]:
            return 1
        return 0


    def confidence_drop(self, row):
        news = str(row["news_text"])

        # Trích xuất dữ liệu confidence thực tế từ Counterfactual Evaluator
        if news in self.cf_mapping:
            cf_data = self.cf_mapping[news]
            confidence_before = cf_data["confidence_before"]
            confidence_after = cf_data["confidence_after"]
            drop = cf_data["confidence_drop"]
        else:
            confidence_before = float(row["confidence"])
            confidence_after = confidence_before
            drop = 0.0

        return pd.Series([
            confidence_before,
            confidence_after,
            drop
        ])


    def evaluate(self):

        self.df["evidence_support"] = self.df.apply(
            self.evidence_support,
            axis=1
        )

        self.df["temporal_validity"] = self.df.apply(
            self.temporal_validity,
            axis=1
        )

        self.df[
            [
                "confidence_before",
                "confidence_after",
                "confidence_drop"
            ]
        ] = self.df.apply(
            self.confidence_drop,
            axis=1
        )

        return self.df


    def summary(self):

        print("\n========== Faithfulness Summary ==========\n")

        print(
            f"Average Evidence Support : "
            f"{self.df['evidence_support'].mean():.2f}"
        )

        print(
            f"Average Temporal Validity : "
            f"{self.df['temporal_validity'].mean():.2f}"
        )

        print(
            f"Average Confidence Drop : "
            f"{self.df['confidence_drop'].mean():.2f}"
        )


    def export(
        self,
        output_file="outputs/faithfulness_results.csv"
    ):

        Path(output_file).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.df.to_csv(
            output_file,
            index=False
        )

        logging.info(
            f"Saved: {output_file}"
        )


def main():
    evaluator = FaithfulnessEvaluator(
        prediction_csv="outputs/prediction_results.csv",
        counterfactual_csv="outputs/faithfulness_check_results.csv"
    )

    df = evaluator.evaluate()

    evaluator.summary()

    evaluator.export()

    print()

    print(df[
        [
            "prediction",
            "expected_direction",
            "confidence_before",
            "confidence_after",
            "confidence_drop",
            "evidence_support",
            "temporal_validity"
        ]
    ].head())


if __name__ == "__main__":
    main()