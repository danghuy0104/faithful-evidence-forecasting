import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

class MarketEvaluator:
    def __init__(self, data_csv):
        # Đọc file kết quả dự báo (chứa cột prediction, price_5d_return, volume_change)
        self.df = pd.read_csv(data_csv)
        self.df.columns = self.df.columns.str.strip()

    def evaluate_consistency(self):
        """
        Đánh giá tính nhất quán giữa DỰ BÁO CỦA MÔ HÌNH (prediction) 
        với BIẾN ĐỘNG THỰC TẾ của thị trường (return & volume change).
        """
        def check_consistency(row):
            ret = row["price_5d_return"]
            pred = str(row["prediction"]).upper() # Sử dụng prediction thay vì label gốc!
            vol = row["volume_change"]
            
            # Khởi tạo trạng thái nhất quán
            is_directional_consistent = False
            
            if pred == "UP" and ret > 0:
                is_directional_consistent = True
            elif pred == "DOWN" and ret < 0:
                is_directional_consistent = True
            elif pred == "HOLD" and abs(ret) <= 0.5:
                is_directional_consistent = True
                
            # Nếu dự báo tăng/giảm đúng xu hướng VÀ khối lượng giao dịch tăng (thị trường đồng thuận mạnh)
            if is_directional_consistent and pred in ["UP", "DOWN"] and vol > 10.0:
                return 1.2  # Tăng trọng số cho các case bùng nổ volume chuẩn xác
            
            return 1 if is_directional_consistent else 0

        self.df["consistency_score"] = self.df.apply(check_consistency, axis=1)
        
        # Tính điểm nhất quán trung bình (chuẩn hóa về khoảng 100%)
        final_score = self.df["consistency_score"].mean()
        if final_score > 1.0: 
            final_score = 1.0 # Cap lại ở mức 100%
            
        return final_score

    def regime_analysis(self):
        """
        Phân tích trạng thái thị trường (Regime Analysis) dựa trên phân phối xu hướng
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
        
        return regime

if __name__ == "__main__":

    evaluator = MarketEvaluator("outputs/counterevidence_coverage.csv")
    
    score = evaluator.evaluate_consistency()
    regime = evaluator.regime_analysis()
    
    print(f"\n=== B3. MARKET CONSISTENCY & REGIME ANALYSIS ===")
    print(f"Market Consistency Score : {score:.2%}")
    print(f"Current Market Regime    : {regime}")
    print("-" * 50)
    print("Mẫu dữ liệu kiểm định (Chỉ số Nhất quán dựa trên Prediction):")
    print(evaluator.df[["news_text", "prediction", "price_5d_return", "volume_change", "consistency_score"]].head())