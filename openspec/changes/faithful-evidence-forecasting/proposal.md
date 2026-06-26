# Proposal

# Faithful Evidence-Centric Financial News Forecasting

## 1. Giới thiệu

### a. Bối cảnh

Trong lĩnh vực tài chính, việc dự báo xu hướng giá cổ phiếu từ tin tức là một bài toán được nghiên cứu rộng rãi trong Financial NLP và Financial Machine Learning. Nhiều mô hình hiện đại có khả năng đọc tin tức, phân tích sentiment và đưa ra dự báo về biến động thị trường.

Tuy nhiên, độ chính xác (Accuracy) không phải là yếu tố duy nhất quyết định mức độ đáng tin cậy của một hệ thống AI. Một mô hình có thể đưa ra prediction đúng nhưng lại giải thích bằng những evidence không thực sự ảnh hưởng đến quyết định của mô hình.

Điều này tạo ra một vấn đề quan trọng:

> *Evidence được mô hình trích dẫn có thật sự là nguyên nhân dẫn đến prediction hay chỉ là một lời giải thích hợp lý được tạo ra sau khi prediction đã được đưa ra?*

Để giải quyết vấn đề này, đồ án tập trung vào việc xây dựng một hệ thống dự báo xu hướng cổ phiếu từ tin tức theo hướng Faithful AI, trong đó evidence phải được kiểm chứng thay vì chỉ được hiển thị như một rationale.

### b. Vấn đề nghiên cứu

Các hệ thống Explainable AI truyền thống thường cung cấp lời giải thích cho prediction nhưng không đảm bảo rằng lời giải thích đó thực sự ảnh hưởng đến quá trình ra quyết định.

Trong bài toán dự báo cổ phiếu từ tin tức, điều này dẫn đến các rủi ro:

- Hiển thị evidence không liên quan đến prediction.
- Bỏ qua các evidence trái chiều.
- Sử dụng thông tin tương lai (Temporal Leakage).
- Đưa ra giải thích nghe hợp lý nhưng không faithful.

Do đó, cần có cơ chế đánh giá mức độ ảnh hưởng thực tế của evidence đối với prediction.

## 2. Ý nghĩa của đề tài

### Ý nghĩa học thuật

- Nghiên cứu mối quan hệ giữa prediction và evidence.
- Áp dụng Faithful AI vào bài toán Financial NLP.
- Minh họa quy trình phát triển phần mềm theo Agentic SDLC.

### Ý nghĩa thực tiễn

- Giúp người dùng hiểu nguyên nhân của dự báo.
- Hỗ trợ đánh giá độ tin cậy của hệ thống AI.
- Là nền tảng để phát triển các hệ thống Explainable AI trong tài chính.

## 3. Mục tiêu đề tài

### a. Mục tiêu tổng quát

Xây dựng một prototype dự báo xu hướng cổ phiếu từ tin tức tài chính có khả năng:

- Dự báo UP/DOWN/HOLD.
- Trích xuất evidence từ tin tức.
- Đánh giá faithfulness của evidence.
- Trực quan hóa kết quả trên dashboard.

### b. Mục tiêu cụ thể

#### Xây dựng Temporal Retriever

- Lọc các tin tức hợp lệ.
- Loại bỏ dữ liệu tương lai.
- Kiểm tra Temporal Leakage.

#### Xây dựng Evidence Extractor

- Trích xuất evidence từ tin tức.
- Xác định polarity.
- Suy ra expected direction.

#### Xây dựng Forecast Model

- Sinh prediction.
- Sinh confidence score.

#### Xây dựng Faithfulness Evaluator

Đánh giá:

- Evidence Support
- Temporal Validity
- Confidence Drop

#### Xây dựng Visualization Dashboard

Hiển thị:

- Prediction
- Evidence
- Faithfulness Metrics
- Temporal Leakage Warning

#### Áp dụng Agentic AI trong SDLC

Sử dụng AI Agent hỗ trợ:

- Requirement Analysis
- Design
- Implementation
- Testing

đồng thời duy trì Human Review và Quality Gate ở mỗi giai đoạn.

## 4. Tiêu chí thành công

Đồ án được xem là hoàn thành khi đáp ứng các tiêu chí sau:

| Tiêu chí | Mục tiêu |
|----------|----------|
| Dataset | Tối thiểu 30 mẫu dữ liệu gồm cả valid news và future news |
| Temporal Retriever | Loại bỏ 100% tin tức có news_time > forecast_time |
| Evidence Extraction | Trích xuất được ít nhất một evidence từ mỗi tin tức hợp lệ |
| Forecast Model | Trả về prediction thuộc tập {UP, DOWN, HOLD} và confidence trong khoảng [0,1] |
| Faithfulness Evaluation | Tính được đầy đủ Evidence Support, Temporal Validity và Confidence Drop |
| Dashboard | Hiển thị prediction, confidence, evidence, faithfulness metrics và cảnh báo temporal leakage |
| Agentic SDLC | Hoàn thành proposal.md, spec.md, design.md, mã nguồn, test và dashboard có Human Review ở mỗi giai đoạn |

## 5. Câu hỏi nghiên cứu

Đề tài tập trung trả lời các câu hỏi sau:

### RQ1

Evidence được mô hình trích dẫn có thực sự ảnh hưởng đến prediction hay không?

### RQ2

Khi loại bỏ evidence đã được cite, confidence của prediction thay đổi như thế nào?

### RQ3

Hệ thống có phát hiện được các trường hợp Temporal Leakage không?

### RQ4

Hệ thống có thể nhận diện Counterevidence hay không?

### RQ5

Liệu một prediction có accuracy cao nhưng faithfulness thấp có đáng tin cậy hay không?

## 6. Phạm vi đề tài

### Trong phạm vi

- Dự báo xu hướng cổ phiếu.
- Phân tích tin tức tài chính.
- Trích xuất evidence.
- Faithfulness Evaluation.
- Dashboard Visualization.
- Agentic SDLC.

### Ngoài phạm vi

- Hệ thống giao dịch tự động.
- Khuyến nghị đầu tư thực tế.
- Real-time prediction.
- Portfolio Management.
- High Frequency Trading.
- Risk Management chuyên sâu.

## 7. Hướng tiếp cận

### a. Kiến trúc tổng quát

```mermaid
flowchart LR
  A[News + Price Data] --> B[Temporal Retriever]
    B --> C[Evidence Extractor]
    C --> D[Evidence Selector]
    D --> E[Forecast Model]
    E --> F[Faithfulness Evaluator]
    F --> G[Visualization Dashboard]
```

### b. Dataset

Phiên bản cơ bản sử dụng:

- Dataset mô phỏng.
- Tối thiểu 30 mẫu.

Mỗi mẫu bao gồm:

| Field | Description |
|--------|--------|
| ticker | Mã cổ phiếu |
| forecast_time | Thời điểm dự báo |
| news_id | Mã tin tức |
| news_time | Thời điểm xuất bản tin |
| title | Tiêu đề tin tức |
| news_text | Nội dung tin tức |
| price_5d_return | Biến động giá 5 ngày |
| volume_change | Biến động khối lượng giao dịch |
| label | Nhãn thực tế (UP/DOWN/HOLD) |

Dataset sẽ chứa cả:

- Tin hợp lệ.
- Tin vi phạm thời gian.

### c. Forecast Model

Trong phạm vi đồ án, nhóm lựa chọn Rule-Based Forecast Model.

Nguyên tắc:

- Positive Evidence --> UP
- Negative Evidence --> DOWN
- Neutral Evidence --> HOLD

Confidence được tính từ tỷ lệ evidence cùng chiều với prediction.

### d. Faithfulness Evaluation

Ba metric chính được sử dụng:

#### Evidence Support

Đo mức độ hỗ trợ của evidence đối với prediction.

#### Temporal Validity

Đo tỷ lệ tin tức hợp lệ theo thời gian.

#### Confidence Drop

So sánh confidence trước và sau khi loại bỏ evidence.

Confidence Drop = Original Confidence - Confidence Without Evidence

- Nếu Confidence Drop lớn:

--> Evidence có khả năng ảnh hưởng mạnh đến prediction.

- Nếu Confidence Drop nhỏ:

--> Evidence có thể chỉ là rationale hậu nghiệm.

## 8. Công nghệ sử dụng

| Thành phần | Công nghệ |
|--------|--------|
| Ngôn ngữ | Python |
| Xử lý dữ liệu | Pandas |
| Visualization | Matplotlib, Plotly |
| Dashboard | Streamlit |
| Testing | Pytest |
| OpenSpec | OpenSpec Workflow |
| Agentic SDLC | ChatGPT, Cursor |

## 9. Kế hoạch thực hiện

### Các giai đoạn

#### Giai đoạn 1

Requirement Analysis

Sản phẩm:

- proposal.md
- spec.md

#### Giai đoạn 2

System Design

Sản phẩm:

- design.md

#### Giai đoạn 3

Implementation

Sản phẩm

- retriever.py
- evidence_extractor.py
- forecast_model.py
- faithfulness_metrics.py

#### Giai đoạn 4

Testing

Sản phẩm:

- test_temporal_retriever.py
- test_metrics.py

#### Giai đoạn 5

Visualization

Sản phẩm:

- dashboard.py
- figures/

#### Giai đoạn 6

Evaluation và Demo

Sản phẩm:

- prediction_results.csv
- faithfulness_results.csv
- report.pdf
- demo_video

### Timeline thực hiện

```text
Tuần        1   2   3   4   5   6
-----------------------------------
Proposal    ███
Spec        ███
Design          ███
Coding              ██████
Testing                 ███
Dashboard               ███
Evaluation                  ███
Report                      ███
Demo                        ███
```

## 10. Phân công vai trò

| Thành viên | Vai trò | Sản phẩm |
|------------|---------|--------------|
| Sinh viên 1 | Requirement & Design | proposal.md, spec.md, design.md, task.md |
| Sinh viên 2 | ML/NLP Engineer | sample_news_price.csv, retriever.py, evidence_extractor.py, evidence_selector.py, forecast_model.py |
| Sinh viên 3 | Evaluation & Visualization | faithfulness_metrics.py, dashboard.py, test_temporal_retriever.py, test_metrics.py, prediction_results.csv, faithfulness_results.csv |

## 11. Kết quả mong đợi

Sau khi hoàn thành, hệ thống có thể:

- Dự báo xu hướng cổ phiếu từ tin tức.
- Hiển thị evidence được sử dụng.
- Kiểm tra temporal validity.
- Đánh giá mức độ faithful của evidence.
- Trực quan hóa kết quả bằng dashboard.
- Minh họa quy trình áp dụng Agentic AI trong Software Development Life Cycle.

## 12. Rủi ro và hạn chế

- Dataset nhỏ có thể không phản ánh đầy đủ thị trường thực tế.
- Rule-Based Model có độ chính xác hạn chế.
- Evidence Extraction có thể bỏ sót thông tin quan trọng.
- Faithfulness Metrics chỉ đánh giá một phần khả năng giải thích của mô hình.
- Kết quả không được sử dụng cho quyết định đầu tư thực tế.

## 13. Kết luận

Đề tài hướng tới việc xây dựng một hệ thống dự báo xu hướng cổ phiếu từ tin tức có khả năng giải thích và kiểm chứng evidence. Thay vì chỉ tập trung vào độ chính xác của prediction, hệ thống đánh giá liệu evidence được trích dẫn có thực sự ảnh hưởng đến quyết định của mô hình hay không.

Thông qua việc kết hợp Forecasting, Explainable AI, Faithfulness Evaluation và Agentic SDLC, đồ án giúp sinh viên tiếp cận một hướng nghiên cứu hiện đại trong lĩnh vực AI đáng tin cậy (Trustworthy AI).