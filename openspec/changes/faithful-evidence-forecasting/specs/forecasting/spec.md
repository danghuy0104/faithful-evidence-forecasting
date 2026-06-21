# Technical Specification: Financial News Forecasting & Faithfulness Evaluation

# Đặc tả: Forecasting (Dự báo cổ phiếu từ tin tức có kiểm chứng evidence)

## Mục đích

Đặc tả này định nghĩa một pipeline dự báo xu hướng cổ phiếu từ tin tức tài chính, có khả năng tự kiểm chứng tính
"faithful" của evidence (bằng chứng) được dùng để giải thích prediction. Pipeline gồm 5 thành phần chính: Bộ lọc
tin theo thời gian (Temporal Retriever), Bộ trích xuất evidence (Evidence Extractor), Mô hình dự báo (Forecast
Model), Bộ đánh giá độ tin cậy evidence (Faithfulness Evaluator), và Dashboard trực quan hóa.

## Quy ước đọc đặc tả này

Mỗi yêu cầu (Requirement) có một hoặc nhiều tình huống minh họa (Scenario), viết theo 4 bước cố định:

- GIVEN (giả sử có) — mô tả điều kiện đầu vào
- WHEN (khi) — mô tả hành động hoặc sự kiện xảy ra
- THEN (thì) — mô tả kết quả bắt buộc phải xảy ra
- AND (và) — mô tả thêm điều kiện/kết quả phụ đi kèm

Bốn từ khóa này được giữ nguyên tiếng Anh vì là quy ước chuẩn của định dạng OpenSpec, dùng để công cụ và người
đọc dễ nhận diện ranh giới giữa điều kiện và kết quả. Toàn bộ nội dung diễn giải còn lại được viết bằng tiếng
Việt. Từ "SHALL" (phải) trong câu mô tả yêu cầu nghĩa là điều kiện bắt buộc, không phải tùy chọn.

## Định dạng dữ liệu đầu vào

| Trường | Giá trị ví dụ | Ý nghĩa |
|---|---|---|
| ticker | AAPL | Mã cổ phiếu cần dự báo |
| forecast_time | 2025-03-12 09:00 | Thời điểm hệ thống ra dự báo |
| news (danh sách tin tức) | — | Mỗi tin tức gồm các trường con dưới đây |
| news.news_id | N001 | Mã định danh của tin tức |
| news.news_time | 2025-03-11 08:30 | Thời điểm tin tức được công bố |
| news.title | Apple reports weak iPhone sales in China | Tiêu đề tin tức |
| news.text | (nội dung đầy đủ) | Nội dung chi tiết của tin tức |
| price_features.price_5d_return | -0.02 | Biến động giá 5 ngày gần nhất |
| price_features.volume_change | 0.15 | Biến động khối lượng giao dịch |
| label | DOWN | Nhãn thực tế dùng để đánh giá (UP/DOWN/HOLD) |

## Định dạng dữ liệu đầu ra

| Trường | Giá trị ví dụ | Ý nghĩa |
|---|---|---|
| ticker | AAPL | Mã cổ phiếu |
| prediction | DOWN | Kết quả dự báo (UP/DOWN/HOLD) |
| confidence | 0.72 | Độ tự tin của dự báo, giá trị từ 0 đến 1 |
| evidence (danh sách) | — | Mỗi evidence gồm các trường con dưới đây |
| evidence.news_id | N001 | Mã tin tức được dùng làm evidence |
| evidence.evidence_text | weak iPhone sales in China | Đoạn văn bản trích ra làm bằng chứng |
| evidence.polarity | negative | Tính chất của evidence: positive/negative/neutral |
| evidence.expected_direction | DOWN | Hướng dự báo mà evidence này ngụ ý |
| evidence.support_score | 1.0 | Mức độ evidence ủng hộ prediction, từ 0 đến 1 |
| faithfulness.temporal_validity | 1.0 | Điểm hợp lệ về thời gian của evidence |
| faithfulness.evidence_support | 1.0 | Điểm ủng hộ của evidence đối với prediction |
| faithfulness.confidence_drop | 0.21 | Mức giảm confidence khi bỏ cited evidence khỏi input |

## Các yêu cầu (Requirements)

### Yêu cầu 1: Dữ liệu đầu vào phải đúng cấu trúc (Data Schema)

Mọi dữ liệu đưa vào hệ thống bắt buộc phải có đầy đủ các trường: ticker, forecast_time, news_time, news_text,
label.

#### Tình huống: Dữ liệu thiếu trường bắt buộc
- GIVEN một bản ghi tin tức bị thiếu trường news_time
- WHEN hệ thống nạp dữ liệu để xử lý
- THEN hệ thống SHALL từ chối bản ghi đó và ghi log lỗi
- AND SHALL không đưa bản ghi lỗi vào pipeline dự báo

### Yêu cầu 2: Bộ lọc tin theo thời gian (Temporal Retriever)

Hệ thống SHALL chỉ sử dụng các tin tức có news_time trước forecast_time để dự báo, và phải tách riêng tin hợp lệ
với tin vi phạm thời gian.

#### Tình huống: Tin tức hợp lệ được giữ lại
- GIVEN một tin tức có news_time trước forecast_time
- WHEN hệ thống chạy bộ lọc thời gian
- THEN tin tức đó SHALL được đưa vào danh sách valid_news

#### Tình huống: Tin tức vi phạm thời gian bị loại
- GIVEN forecast_time là 2025-03-12 09:00 và một tin có news_time là 2025-03-12 15:30
- WHEN hệ thống chạy bộ lọc thời gian
- THEN tin tức đó SHALL bị loại khỏi input dự báo
- AND SHALL được ghi vào danh sách invalid_future_news

### Yêu cầu 3: Trích xuất evidence (Evidence Extractor)

Hệ thống SHALL trích xuất được đoạn văn bản làm evidence từ mỗi tin tức hợp lệ, kèm theo polarity và
expected_direction tương ứng.

#### Tình huống: Trích xuất evidence từ tin tức tiêu cực
- GIVEN một tin tức hợp lệ chứa nội dung tiêu cực, ví dụ "misses expectations"
- WHEN hệ thống chạy bộ trích xuất evidence
- THEN hệ thống SHALL trả về đoạn evidence_text tương ứng
- AND SHALL gán polarity là "negative"
- AND SHALL gán expected_direction là "DOWN"

#### Tình huống: Trích xuất evidence từ tin tức tích cực
- GIVEN một tin tức hợp lệ chứa nội dung tích cực, ví dụ "earnings beat expectations"
- WHEN hệ thống chạy bộ trích xuất evidence
- THEN hệ thống SHALL gán polarity là "positive"
- AND SHALL gán expected_direction là "UP"

#### Tình huống: Tin tức trung tính không tạo evidence định hướng
- GIVEN một tin tức hợp lệ không mang sắc thái rõ ràng, ví dụ "company holds annual investor meeting"
- WHEN hệ thống chạy bộ trích xuất evidence
- THEN hệ thống SHALL gán polarity là "neutral"
- AND SHALL gán expected_direction là "HOLD"

### Yêu cầu 4: Mô hình dự báo (Forecast Model)

Hệ thống SHALL dự báo xu hướng cổ phiếu thuộc một trong ba nhãn UP/DOWN/HOLD, kèm confidence score, và phải chỉ
ra được evidence nào được dùng để giải thích cho dự báo đó.

#### Tình huống: Dự báo UP khi evidence tích cực chiếm đa số
- GIVEN danh sách evidence trong đó số lượng positive nhiều hơn negative
- WHEN hệ thống chạy mô hình dự báo
- THEN hệ thống SHALL trả về prediction là "UP" kèm confidence score
- AND SHALL liệt kê các evidence positive đã dùng để ra quyết định

#### Tình huống: Dự báo DOWN khi evidence tiêu cực chiếm đa số
- GIVEN danh sách evidence trong đó số lượng negative nhiều hơn positive
- WHEN hệ thống chạy mô hình dự báo
- THEN hệ thống SHALL trả về prediction là "DOWN" kèm confidence score

#### Tình huống: Dự báo HOLD khi evidence cân bằng
- GIVEN danh sách evidence có số lượng positive bằng số lượng negative
- WHEN hệ thống chạy mô hình dự báo
- THEN hệ thống SHALL trả về prediction là "HOLD"

### Yêu cầu 5: Đánh giá độ tin cậy evidence (Faithfulness Evaluator)

Hệ thống SHALL tính được tối thiểu 3 chỉ số: Evidence Support, Temporal Validity, và Confidence Drop.

#### Tình huống: Tính Evidence Support
- GIVEN một prediction và evidence được cite cho prediction đó
- WHEN hệ thống đối chiếu polarity của evidence với prediction
- THEN hệ thống SHALL trả về điểm Evidence Support trong khoảng từ 0 đến 1, thể hiện mức độ evidence ủng hộ đúng
  chiều của prediction

#### Tình huống: Tính Temporal Validity
- GIVEN danh sách evidence được cite cho một prediction
- WHEN hệ thống kiểm tra news_time của từng evidence so với forecast_time
- THEN hệ thống SHALL trả về điểm Temporal Validity bằng 1.0 nếu toàn bộ evidence hợp lệ về thời gian, và nhỏ
  hơn 1.0 nếu có evidence vi phạm

#### Tình huống: Tính Confidence Drop khi loại bỏ cited evidence
- GIVEN một prediction gốc có confidence là 0.80, được giải thích bởi một evidence cụ thể
- WHEN hệ thống chạy lại dự báo sau khi loại bỏ evidence đó khỏi input
- THEN hệ thống SHALL trả về confidence mới, ví dụ 0.55
- AND SHALL tính confidence_drop bằng confidence gốc trừ confidence mới, ví dụ 0.25

### Yêu cầu 6: Dashboard hiển thị evidence và cảnh báo

Dashboard SHALL hiển thị evidence ủng hộ prediction, thời gian xuất bản của evidence, và cảnh báo nếu evidence vi
phạm thời gian.

User story gốc: Là một nhà phân tích tài chính, tôi muốn xem evidence nào khiến mô hình dự báo cổ phiếu giảm, để
biết dự báo đó có đáng tin hay không.

#### Tình huống: Hiển thị evidence ủng hộ prediction DOWN
- GIVEN một prediction là "DOWN"
- WHEN người dùng mở dashboard
- THEN hệ thống SHALL hiển thị ít nhất 1 evidence ủng hộ DOWN
- AND SHALL hiển thị thời gian xuất bản (news_time) của evidence đó
- AND SHALL cảnh báo nếu evidence đó xuất hiện sau forecast_time

#### Tình huống: Hiển thị bảng tổng hợp faithfulness cho nhiều mẫu
- GIVEN một tập nhiều prediction đã được đánh giá faithfulness
- WHEN người dùng mở dashboard
- THEN hệ thống SHALL hiển thị bảng tổng hợp gồm các cột: ticker, prediction, confidence, evidence_support,
  temporal_validity, confidence_drop

### Yêu cầu 7: Dataset kiểm thử

Dataset dùng để kiểm thử hệ thống SHALL có tối thiểu 30 dòng dữ liệu, bao gồm cả tin hợp lệ và tin vi phạm thời
gian.

#### Tình huống: Dataset đủ điều kiện kiểm thử temporal leakage
- GIVEN một bộ dataset mẫu
- WHEN dataset được dùng để kiểm thử bộ lọc thời gian
- THEN dataset SHALL chứa ít nhất một số dòng có news_time sau forecast_time để kiểm tra việc loại bỏ đúng tin
  vi phạm
