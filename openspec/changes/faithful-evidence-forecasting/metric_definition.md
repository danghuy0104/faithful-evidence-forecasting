# Định nghĩa Metric: Faithful Evidence-Centric Financial News Forecasting
 
## Mục đích
 
Tài liệu này định nghĩa công thức tính toán cụ thể, khoảng giá trị, và cách diễn giải cho từng metric dùng để kiểm chứng tính faithful của evidence trong đồ án. Phần 1 là 3 metric bắt buộc thuộc Phần A (yêu cầu A6). Phần 2 là các metric thuộc Phần B (nâng cao), chỉ cần định nghĩa nếu nhóm quyết định làm thêm.
 
## Phần 1: Metric cơ bản (bắt buộc — A6)
 
### 1.1. Temporal Validity (Tính hợp lệ về thời gian)
 
- Mục đích: kiểm tra evidence được dùng để giải thích prediction có vi phạm temporal leakage không, tức có dùng tin xuất hiện sau `forecast_time` hay không.
- Công thức: `temporal_validity = số evidence có news_time hợp lệ / tổng số evidence được cite`
- Khoảng giá trị: từ 0 đến 1. Giá trị 1.0 nghĩa là toàn bộ evidence hợp lệ về thời gian.
- Ví dụ minh họa: `forecast_time` là 2025-03-12 09:00, một evidence có `news_time` là 2025-03-12 15:30 (sau thời điểm dự báo) → evidence này không hợp lệ, làm giảm điểm `temporal_validity` của mẫu đó.
- Diễn giải: bất kỳ mẫu nào có `temporal_validity` nhỏ hơn 1.0 đều phải được gắn cờ cảnh báo trên dashboard, vì đây là lỗi nghiêm trọng làm toàn bộ kết quả thí nghiệm không đáng tin.
### 1.2. Evidence Support (Mức độ ủng hộ của evidence)
 
- Mục đích: kiểm tra evidence được cite có đúng hướng (polarity) với prediction cuối cùng hay không.
- Công thức: `evidence_support = số evidence có expected_direction khớp với prediction / tổng số evidence được cite`
- Khoảng giá trị: từ 0 đến 1. Giá trị 1.0 nghĩa là toàn bộ evidence được cite đều cùng hướng với prediction.
- Ví dụ minh họa: prediction là DOWN, evidence được cite có `expected_direction` là DOWN → support_score = 1.0 cho evidence đó. Nếu một mẫu có nhiều evidence được cite nhưng chỉ một nửa khớp hướng DOWN, evidence_support của mẫu đó là 0.5.
- Diễn giải: evidence_support thấp cho thấy mô hình cite cả những evidence không liên quan đến hướng dự báo, một dấu hiệu của explanation không nhất quán.
### 1.3. Confidence Drop (Mức giảm confidence khi bỏ cited evidence)
 
- Mục đích: đây là metric quan trọng nhất, dùng để trả lời trực tiếp câu hỏi nghiên cứu trung tâm của đồ án —  evidence có thật sự quyết định prediction hay chỉ là lời giải thích trang trí.
- Cách thực hiện: chạy Forecast Model hai lần trên cùng một mẫu — một lần với input đầy đủ (có cited evidence), một lần với input đã loại bỏ cited evidence — rồi so sánh confidence của hai lần chạy.
- Công thức: `confidence_drop = confidence_goc - confidence_sau_khi_bo_evidence`
- Khoảng giá trị: từ -1 đến 1 về lý thuyết, nhưng trong thực tế thường nằm trong khoảng 0 đến 1 (confidence giảm khi bỏ evidence quan trọng). Giá trị âm (confidence tăng lên khi bỏ evidence) là trường hợp bất thường, cần được ghi chú riêng khi phân tích.
- Ví dụ minh họa (evidence có khả năng faithful — theo ví dụ TSLA trong đề bài): confidence gốc là 0.81, sau khi  bỏ cited evidence còn 0.55 → confidence_drop = 0.26. Mức giảm lớn cho thấy evidence này có vai trò quan trọng (necessity cao) đối với prediction.
- Ví dụ minh họa (evidence chỉ là rationale hậu nghiệm — theo ví dụ NVDA trong đề bài): confidence gốc là 0.88, sau khi bỏ cited evidence còn 0.86 → confidence_drop = 0.02. Mức giảm rất nhỏ cho thấy evidence này có thể không phải nguyên nhân thật sự khiến mô hình ra quyết định, dù lời giải thích nghe hợp lý.
### 1.4. Ngưỡng diễn giải dùng chung cho Confidence Drop
 
Đồ án không có một ngưỡng "chuẩn" tuyệt đối, nhưng để thuận tiện cho việc phân loại khi làm dashboard và báo cáo, nhóm có thể tạm dùng các mức sau (cần nêu rõ trong báo cáo đây là ngưỡng do nhóm tự đề xuất, không phải số liệu chính thức từ đề bài):
 
| Mức confidence_drop | Diễn giải tạm |
|---|
| Lớn hơn 0.2 | Evidence có khả năng faithful, necessity cao |
| Từ 0.05 đến 0.2 | Evidence có ảnh hưởng vừa phải, cần xem thêm các mẫu khác để kết luận |
| Nhỏ hơn 0.05 | Evidence có khả năng chỉ là rationale hậu nghiệm (decorative explanation) |
 
Lưu ý quan trọng: không nên kết luận chắc chắn evidence là faithful hay không chỉ dựa trên 1-2 mẫu. Cần tính confidence_drop trên nhiều mẫu và báo cáo cả giá trị trung bình, để tránh overclaim — đúng theo lưu ý ở mục Evaluation trong bảng Agentic SDLC của `proposal.md`.
 
## Phần 2: Metric nâng cao (chỉ định nghĩa nếu làm Phần B)
 
### 2.1. Sufficiency (B1)
 
- Mục đích: kiểm tra ngược lại với Confidence Drop — nếu chỉ giữ lại cited evidence (bỏ hết các thông tin khác), prediction có còn giữ nguyên không.
- Cách thực hiện: chạy Forecast Model chỉ với cited evidence làm input duy nhất, so sánh với kết quả chạy đầy đủ.
- Ví dụ minh họa: full input cho prediction DOWN với confidence 0.78; chỉ dùng cited evidence cho prediction DOWN với confidence 0.69 — prediction không đổi, confidence giảm nhẹ, cho thấy cited evidence đủ sufficiency để giữ
  nguyên kết luận.
### 2.2. Counterfactual Perturbation (B1)
 
- Mục đích: thay cited evidence bằng một tin trung tính/giả định (counterfactual) để kiểm tra độ nhạy của model.
- Cách thực hiện: thay nội dung evidence gốc bằng một câu trung tính không liên quan đến hướng dự báo, chạy lại model, so sánh prediction và confidence.
- Ví dụ minh họa: evidence gốc "Tesla misses delivery expectations" (negative, DOWN) được thay bằng "Tesla holds annual investor meeting" (neutral). Nếu prediction vẫn là DOWN với confidence gần như không đổi, đây là dấu hiệu mô hình chưa thật sự nhạy với nội dung cụ thể của evidence.
### 2.3. Counterevidence Coverage (B2)
 
- Mục đích: kiểm tra mô hình có nhận diện và cân nhắc cả những tin trái chiều (counterevidence) với prediction, hay chỉ cite một chiều thông tin.
- Công thức: `counterevidence_coverage = số mẫu mô hình phát hiện đúng counterevidence / tổng số mẫu có counterevidence thực tế trong dữ liệu`- Ví dụ minh họa: prediction là UP (vì có tin ra mắt sản phẩm mới), nhưng cùng ngày cũng có tin doanh số iPhone
  tại Trung Quốc giảm. Nếu hệ thống chỉ cite tin tích cực mà không phát hiện tin trái chiều này, counterevidence_coverage của mẫu đó được tính là 0; nếu phát hiện được, tính là 1.
### 2.4. Market Consistency (B3)
 
- Mục đích: kiểm tra evidence được cite có nhất quán với biến động giá/khối lượng giao dịch thực tế sau khi tin được công bố không, để phát hiện trường hợp tin tức đã được phản ánh vào giá trước khi mô hình xử lý.
- Cách thực hiện: so sánh polarity của evidence với `return` và `volume_change` của ngày giao dịch kế tiếp.
- Ví dụ minh họa: tin tiêu cực, cộng với return ngày kế tiếp là -3.2% và volume tăng → mức market consistency cao, cho thấy evidence khớp với phản ứng thực tế của thị trường.
## Phần 3: Cách trình bày metric trên dashboard
 
Theo yêu cầu A7 và B (nếu làm), mỗi mẫu khi hiển thị trên dashboard cần đi kèm tối thiểu các cột sau trong bảng faithfulness: `ticker`, `prediction`, `confidence`, `evidence_support`, `temporal_validity`, `confidence_drop`.
Nếu làm thêm Phần B, bổ sung thêm cột `sufficiency`, `counterevidence_coverage`, `market_consistency`. Cách bố trí cụ thể (bar chart, radar chart, bảng) đã được mô tả trong `design.md`, mục 2.6.
