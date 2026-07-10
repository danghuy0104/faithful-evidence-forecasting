import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

class MarketEvaluator:
    def __init__(self, data_csv):
        # Đọc file kết quả dự báo
        self.df = pd.read_csv(data_csv)
        self.df.columns = self.df.columns.str.strip()

    def evaluate_consistency(self):
        """
        Đánh giá tính nhất quán giữa DỰ BÁO CỦA MÔ HÌNH (prediction) 
        với BIẾN ĐỘNG THỰC TẾ của thị trường (return & volume change).
        
        Trả về:
        - directional_accuracy: Tỷ lệ dự báo đúng hướng thuần túy (0.0 - 1.0).
        - weighted_consistency_index: Chỉ số nhất quán có tính thêm trọng số volume.
        """
        def compute_row_metrics(row):
            ret = row["price_5d_return"]
            pred = str(row["prediction"]).upper()
            vol = row["volume_change"]
            
            # 1. Kiểm tra tính đúng hướng thuần túy (0 hoặc 1)
            is_directional_consistent = 0
            if pred == "UP" and ret > 0:
                is_directional_consistent = 1
            elif pred == "DOWN" and ret < 0:
                is_directional_consistent = 1
            elif pred == "HOLD" and abs(ret) <= 0.5:
                is_directional_consistent = 1
                
            # 2. Tính điểm nhất quán kèm phần thưởng Volume
            consistency_score = float(is_directional_consistent)
            if is_directional_consistent == 1 and pred in ["UP", "DOWN"] and vol > 10.0:
                consistency_score = 1.2  # Thưởng thêm 0.2 vào chỉ số nếu thanh khoản bùng nổ đồng thuận
            
            return pd.Series([is_directional_consistent, consistency_score])

        # Áp dụng hàm tính toán cho từng dòng và tạo 2 cột mới
        self.df[["is_directional_correct", "consistency_score"]] = self.df.apply(compute_row_metrics, axis=1)
        
        # Tính toán giá trị trung bình tổng thể cho toàn tập dữ liệu
        directional_accuracy = self.df["is_directional_correct"].mean()
        weighted_consistency_index = self.df["consistency_score"].mean()
        
        return directional_accuracy, weighted_consistency_index

    def regime_analysis(self):
        """
        Phân tích trạng thái thị trường (Regime Analysis) dựa trên phân phối xu hướng.
        Trả về bộ 3 giá trị phục vụ trực tiếp cho báo cáo và trực quan hóa.
        """
        avg_return = self.df["price_5d_return"].mean()
        avg_volume = self.df["volume_change"].mean()
        
        # Thống kê phân phối dự báo để hiểu hành vi mô hình trong từng Regime
        pred_counts = self.df["prediction"].value_counts(normalize=True)
        up_ratio = pred_counts.get("UP", 0)
        down_ratio = pred_counts.get("DOWN", 0)
        
        # Xác định trạng thái dựa trên biến động giá trung bình
        if avg_return > 0.5:
            regime = "Bullish (Thị trường giá lên)"
        elif avg_return < -0.5:
            regime = "Bearish (Thị trường giá xuống)"
        else:
            regime = "Sideway (Thị trường đi ngang)"
            
        logging.info(f"Thống kê Regime: Avg Return: {avg_return:.2f}%, Avg Vol Change: {avg_volume:.2f}%")
        logging.info(f"Tỷ lệ dự báo của mô hình: UP: {up_ratio:.1%}, DOWN: {down_ratio:.1%}")
        
        
        return regime, avg_return, avg_volume

if __name__ == "__main__":
    # Khởi tạo bộ đánh giá với tệp đầu ra tương ứng
    evaluator = MarketEvaluator("outputs/counterevidence_coverage.csv")
    
    # Nhận về các chỉ số từ hệ thống
    dir_accuracy, consistency_index = evaluator.evaluate_consistency()
    market_regime, avg_ret, avg_vol = evaluator.regime_analysis()
    
    print(f"\n=== MARKET CONSISTENCY & REGIME ANALYSIS ===")
    print(f"Directional Accuracy        : {dir_accuracy:.2%}")
    print(f"Weighted Consistency Index  : {consistency_index:.2f} (baseline = 1.00)") 
    print(f"Current Market Regime       : {market_regime}")
    print(f"Average Market Return (5d)  : {avg_ret:.2f}%")
    print(f"Average Volume Change       : {avg_vol:.2f}%")
    print("-" * 65)
    print("Mẫu dữ liệu kiểm định chi tiết:")
    print(evaluator.df[[
        "news_text", 
        "prediction", 
        "price_5d_return", 
        "volume_change", 
        "is_directional_correct",
        "consistency_score"
    ]].head())