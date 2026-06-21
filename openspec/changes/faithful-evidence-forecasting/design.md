# Design: Faithful Evidence-Centric Financial News Forecasting

## 1. Kiến trúc tổng quan (Pipeline)

#Hệ thống được tổ chức thành một pipeline tuần tự gồm 6 khối xử lý, dữ liệu đi qua từng khối theo đúng thứ tự dưới đây:
#News -> Price Data -> Bộ lọc thời gian -> Bộ trích xuất evidence -> Bộ chọn evidence -> Mô hình dự báo -> Bộ đánh giá độ tin cậy -> Dashboard trực quan hóa

| Khối | Nhiệm vụ | Ví dụ đầu ra |
|---|
| Temporal Retriever (Bộ lọc thời gian) | Chỉ giữ lại tin tức xuất hiện trước thời điểm dự báo | valid_news, invalid_future_news |
| Evidence Extractor (Bộ trích xuất evidence) | Trích xuất đoạn bằng chứng nhỏ và gán hướng tác động từ mỗi tin tức | "weak iPhone sales" được gán negative, hướng DOWN |
| Evidence Selector (Bộ chọn evidence) | Phân loại evidence thành pro (ủng hộ) và counterevidence (trái chiều) | pro: "earnings beat"; counter: "weak guidance" |
| Forecast Model (Mô hình dự báo) | Tổng hợp evidence để đưa ra dự báo UP/DOWN/HOLD | DOWN, confidence = 0.72 |
| Faithfulness Evaluator (Bộ đánh giá độ tin cậy) | Tính các chỉ số evidence support, temporal validity, confidence drop | confidence_drop = 0.21 |
| Dashboard | Hiển thị prediction, evidence, cảnh báo và biểu đồ cho người dùng | bảng dữ liệu, biểu đồ cột, radar chart |

Lưu ý: khối Evidence Selector hiện chưa được mô tả chi tiết trong `spec.md` ở phiên bản MVP (Phần A), vì yêu cầu cơ bản A4 chỉ cần trích xuất evidence, chưa bắt buộc phân tách pro/counter. Khối này sẽ được hiện thực đầy đủ khi nhóm triển khai phần nâng cao B2 (Counterevidence Coverage). Ở MVP, có thể tạm coi Evidence Selector là một bước rút gọn: chọn toàn bộ evidence đã trích xuất làm input cho Forecast Model.

## 2. Chi tiết từng thành phần

### 2.1. Temporal Retriever
- Input: danh sách tin tức (mỗi tin có `news_time`), và `forecast_time` của lượt dự báo.
- Output: hai danh sách `valid_news` (tin có `news_time` < `forecast_time`) và `invalid_future_news` (tin có `news_time` >= `forecast_time`).
- Thuật toán MVP: so sánh trực tiếp 2 giá trị thời gian (dùng kiểu dữ liệu datetime), không cần model.
- File code dự kiến: `src/retriever.py`.

### 2.2. Evidence Extractor
- Input: `valid_news` từ bước trên.
- Output: danh sách evidence, mỗi evidence gồm `evidence_text`, `polarity` (positive/negative/neutral), `expected_direction` (UP/DOWN/HOLD).
- Thuật toán MVP: rule-based theo từ khóa (ví dụ: tập từ khóa tiêu cực như "miss", "weak", "decline"; tập từ khóa tích cực như "beat", "launch", "growth"). Nếu không khớp từ khóa nào -> polarity = neutral.
- File code dự kiến: `src/evidence_extractor.py`.

### 2.3. Evidence Selector
- Input: danh sách evidence từ bước trên.
- Output: hai nhóm `pro_evidence` (cùng hướng với prediction sau cùng) và `counterevidence` (ngược hướng).
- Thuật toán MVP: chưa tách pro/counter, dùng toàn bộ evidence. Thuật toán nâng cao (B2): so sánh `expected_direction` của từng evidence với prediction cuối cùng để phân loại.
- File code dự kiến: gộp chung vào `src/forecast_model.py` ở MVP, tách riêng `src/evidence_selector.py` nếu làm phần nâng cao.

### 2.4. Forecast Model
- Input: danh sách evidence (đã chọn ở bước trên).
- Output: `prediction` (UP/DOWN/HOLD) và `confidence` (0 đến 1).
- Thuật toán MVP: rule-based đếm số evidence positive và negative theo công thức:
  - Nếu (số lượng positive - số lượng negative) > 0 -> prediction = UP
  - Nếu (số lượng positive - số lượng negative) < 0 -> prediction = DOWN
  - Nếu bằng 0 -> prediction = HOLD
  - Confidence được tính theo tỉ lệ giữa số evidence cùng hướng với prediction trên tổng số evidence.
- File code dự kiến: `src/forecast_model.py`.

### 2.5. Faithfulness Evaluator
- Input: prediction gốc, danh sách evidence đã cite, và khả năng gọi lại Forecast Model.
- Output: 3 chỉ số `evidence_support`, `temporal_validity`, `confidence_drop`.
- Thuật toán MVP:
  - `temporal_validity`: tỉ lệ evidence có `news_time` hợp lệ trên tổng số evidence được cite.
  - `evidence_support`: tỉ lệ evidence có `expected_direction` khớp với prediction cuối cùng.
  - `confidence_drop`: chạy lại Forecast Model sau khi loại bỏ evidence được cite khỏi input, lấy confidence gốc trừ confidence mới.
- File code dự kiến: `src/faithfulness_metrics.py`.

### 2.6. Dashboard
- Input: toàn bộ output của các bước trên (prediction, evidence, faithfulness scores) cho một hoặc nhiều mẫu.
- Output: tối thiểu 4 bảng/hình theo yêu cầu A7: prediction distribution, evidence table, confidence drop chart, temporal leakage warning.
- Công nghệ MVP: Jupyter Notebook (hiển thị bảng và biểu đồ tĩnh bằng matplotlib/pandas). Có thể nâng cấp lên Streamlit nếu nhóm còn thời gian, để có giao diện tương tác (chọn ticker, bấm nút "remove cited evidence" như kịch bản demo).
- File code dự kiến: `src/dashboard.py`.

## 3. Cấu trúc dữ liệu (Data Schema)

Cấu trúc input/output đầy đủ (tên trường, ý nghĩa, ví dụ) đã được định nghĩa chi tiết trong
`openspec/specs/forecasting/spec.md`, phần "Định dạng dữ liệu đầu vào" và "Định dạng dữ liệu đầu ra". Design.md này không lặp lại toàn bộ, chỉ tham chiếu để tránh hai tài liệu lệch nhau khi cập nhật.

## 4. Lựa chọn công nghệ

| Hạng mục | Lựa chọn cho MVP (Phần A) | Hướng nâng cấp sau (Phần B / điểm cộng) |
|---|
| Ngôn ngữ | Python | Python + Streamlit (nếu nâng dashboard) |
| Dữ liệu | CSV mô phỏng, tự tạo | Yahoo Finance + dataset tin tức thật (điểm cộng C1) |
| Evidence Extraction | Rule-based theo từ khóa | FinBERT/LLM extraction (điểm cộng C2) |
| Forecast Model | Rule-based (đếm positive/negative) | Logistic Regression / LSTM / Transformer (điểm cộng C2) |
| Dashboard | Jupyter Notebook | Streamlit + Plotly (tương tác) |
| Testing | pytest đơn giản | pytest + schema validation |

Lý do chọn rule-based và dữ liệu mô phỏng cho MVP: đây là lựa chọn nhanh nhất để hoàn thành đủ 7 điểm Phần A, không phụ thuộc vào việc thu thập dữ liệu thật hoặc cài đặt môi trường GPU, đồng thời rule-based dễ giải thích - phù hợp với mục tiêu cốt lõi của đồ án là kiểm chứng faithfulness hơn là tối ưu accuracy.

## 5. Cấu trúc thư mục mã nguồn

Cấu trúc thư mục mã nguồn bám theo đúng cây thư mục đề bài yêu cầu (mục 9), mỗi file ứng với một thành phần ở mục 2:

- `data/sample_news_price.csv` - dữ liệu mẫu, đầu vào cho toàn bộ pipeline
- `src/retriever.py` - Temporal Retriever (mục 2.1)
- `src/evidence_extractor.py` - Evidence Extractor (mục 2.2)
- `src/forecast_model.py` - Forecast Model, gộp luôn Evidence Selector ở MVP (mục 2.3, 2.4)
- `src/faithfulness_metrics.py` - Faithfulness Evaluator (mục 2.5)
- `src/dashboard.py` - Dashboard (mục 2.6)
- `tests/test_temporal_retriever.py` - test cho Temporal Retriever
- `tests/test_metrics.py` - test cho Faithfulness Evaluator
- `outputs/prediction_results.csv`, `outputs/faithfulness_results.csv` - kết quả chạy pipeline
- `outputs/figures/` - hình ảnh biểu đồ xuất ra từ Dashboard

## 6. Các quyết định thiết kế quan trọng và lý do lựa chọn

- **Vì sao tính confidence_drop bằng cách chạy lại model thay vì ước lượng**: chạy lại Forecast Model với input đã loại bỏ evidence cho kết quả chính xác và dễ kiểm chứng hơn so với việc ước lượng gián tiếp, dù tốn thêm một lượt tính toán cho mỗi mẫu.
- **Vì sao Evidence Selector được gộp tạm vào Forecast Model ở MVP**: tránh tạo thêm một module riêng khi yêu cầu A4/A5 chưa bắt buộc phân tách pro/counterevidence, giảm độ phức tạp ban đầu; sẽ tách riêng khi triển khai B2.
- **Vì sao chọn rule-based theo từ khóa cho Evidence Extractor**: đáp ứng đúng yêu cầu tối thiểu của A4 (ít nhất 5 ví dụ đúng/sai), không cần huấn luyện model hay tải thư viện NLP nặng, dễ debug khi evidence trích sai.
- **Vì sao chọn Jupyter Notebook làm Dashboard mặc định**: thỏa điều kiện tối thiểu của A7 ("dashboard hoặc notebook chạy được"), không yêu cầu cài đặt phức tạp, mọi thành viên có thể chạy ngay trên Google Colab.

## 7. Giới hạn của thiết kế MVP

- Rule-based theo từ khóa có thể trích sai evidence khi tin tức dùng từ ngữ mơ hồ hoặc phủ định kép (ví dụ: "not as weak as expected").
- Confidence ở Forecast Model rule-based chỉ phản ánh tỉ lệ số lượng evidence, chưa phản ánh được mức độ quan trọng (severity) của từng evidence.
- Thiết kế này chưa xử lý trường hợp một tin tức ảnh hưởng đến nhiều ticker khác nhau cùng lúc.
- Các giới hạn này sẽ được ghi nhận lại trong phần Limitations của báo cáo cuối kỳ, theo đúng lưu ý đạo đức ở mục 12 của đề bài).
