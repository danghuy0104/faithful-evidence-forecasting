from pathlib import Path
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

class EvidenceExtractor:
    
    POSITIVE_KEYWORDS = [
        "profit", "grow", "beat", "increase", "record", "strong", "surge", "gain", "expand", "upgrade", "exceed", "win"
    ]
    NEGATIVE_KEYWORDS = [
        "loss", "weak", "decline", "drop", "miss", "lawsuit", "bankruptcy", 
        "fall", "downgrade", "decrease", "strike", "delay", "disrupt", "fine", "investigat", "recall", "face"
    ]

    def __init__(self, csv_file: str):
        csv_path = Path(csv_file)
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found: {csv_file}")
        self.df = pd.read_csv(csv_path)
        if "news_text" not in self.df.columns:
            raise ValueError("Missing required column: news_text")
        logging.info("=" * 50)
        logging.info(f"Loaded {len(self.df)} news articles.")

    def _get_evidence_lists(self, text_lower):
        """Trích xuất từ khóa, loại bỏ trùng lặp ngữ nghĩa."""
        pro = [w for w in self.POSITIVE_KEYWORDS if w in text_lower]
        con = [w for w in self.NEGATIVE_KEYWORDS if w in text_lower]
        return list(set(pro)), list(set(con))

    def extract(self, text: str):
        text_lower = str(text).lower()
        pro, con = self._get_evidence_lists(text_lower)
        
        positive, negative = len(pro), len(con)
        
        if positive > negative:
            sentiment, direction = "positive", "UP"
        elif negative > positive:
            sentiment, direction = "negative", "DOWN"
        else:
            sentiment, direction = "neutral", "HOLD"

        # Tổng hợp toàn bộ từ khóa tìm được
        evidence_all = ", ".join(pro + con)
        return evidence_all, sentiment, direction, pro, con

    def process(self):
        evidences, sentiments, directions = [], [], []
        pro_evidences_cols, counter_evidences_cols = [], []

        for news in self.df["news_text"]:
            ev, sen, dr, pro_list, con_list = self.extract(news)
            evidences.append(ev)
            sentiments.append(sen)
            directions.append(dr)
            
            pro_col = ""
            count_col = ""
            
            if dr == "UP":
                pro_col = ", ".join(pro_list)
                count_col = ", ".join(con_list)
            elif dr == "DOWN":
                pro_col = ", ".join(con_list)  # Ủng hộ DOWN là các từ tiêu cực
                count_col = ", ".join(pro_list) # Phản bác DOWN là các từ tích cực
            elif dr == "HOLD":
                # Đối với nhãn HOLD, phân loại rõ ràng: không có pro_evidence thúc đẩy xu hướng
                # Toàn bộ từ khóa tìm được sẽ đẩy vào counter_evidence hoặc giữ sạch dữ liệu
                pro_col = ""
                count_col = ", ".join(pro_list + con_list)
                
            # Append giá trị đã được xử lý/xóa rỗng an toàn vào list
            pro_evidences_cols.append(pro_col)
            counter_evidences_cols.append(count_col)

        self.df["evidence_text"] = evidences
        self.df["sentiment"] = sentiments
        self.df["expected_direction"] = directions
        self.df["pro_evidence"] = pro_evidences_cols
        self.df["counter_evidence"] = counter_evidences_cols
        return self.df

    def export(self, output_file="outputs/evidence_results.csv"):
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        df = self.process()
        df.to_csv(output_file, index=False)
        logging.info(f"Evidence extracted: {len(df)}")
        logging.info(f"Evidence CSV      : {output_file}")
        logging.info("=" * 50)
        return df

def main():
    extractor = EvidenceExtractor("outputs/valid_news.csv")
    df = extractor.export()
    print(df[["news_text", "expected_direction", "pro_evidence", "counter_evidence"]].head(5))

if __name__ == "__main__":
    main()