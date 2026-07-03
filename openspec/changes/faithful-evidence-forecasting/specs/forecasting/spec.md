# Technical Specification

## 1. Tổng quan

### a. Tên hệ thống

Faithful Evidence-Centric Financial News Forecasting

### b. Mục tiêu

Xây dựng hệ thống dự báo xu hướng giá cổ phiếu (UP/DOWN/HOLD) từ dữ liệu tin tức tài chính và dữ liệu giá lịch sử, đồng thời kiểm chứng mức độ ảnh hưởng thực sự của evidence đến prediction thông qua các faithfulness metrics.

Hệ thống sẽ:

- Chỉ sử dụng các tin tức xuất hiện trước thời điểm dự báo.
- Trích xuất evidence từ tin tức.
- Sinh prediction cùng confidence score.
- Đánh giá mức độ faithful của evidence.
- Hiển thị kết quả bằng dashboard trực quan.


## 2. Phạm vi hệ thống

### a. Trong phạm vi:

- Đọc dữ liệu cổ phiếu và tin tức.
- Kiểm tra temporal validity.
- Trích xuất evidence.
- Dự báo UP/DOWN/HOLD.
- Đánh giá faithfulness.
- Trực quan hóa kết quả.
- Hỗ trợ phân tích counterevidence cơ bản.

### b. Ngoài phạm vi:

- Giao dịch chứng khoán thực tế.
- Hệ thống khuyến nghị đầu tư.
- Real-time trading.
- High-frequency trading.
- Portfolio optimization.

## 3. User Story

### US-01: Xem dự báo cổ phiếu

Là một nhà phân tích tài chính,

Tôi muốn xem prediction của hệ thống,

Để biết cổ phiếu có xu hướng tăng, giảm hoặc đi ngang.

### US-02: Xem evidence

Là một nhà phân tích tài chính,

Tôi muốn biết evidence nào được sử dụng cho prediction,

Để đánh giá mức độ đáng tin cậy của dự báo.

### US-03: Kiểm tra temporal validity

Là một người kiểm thử,

Tôi muốn xác nhận hệ thống không sử dụng tin tức trong tương lai,

Để tránh temporal leakage.

### US-04: Đánh giá faithfulness

Là một nhà nghiên cứu AI,

Tôi muốn biết prediction có thực sự phụ thuộc vào evidence được trích xuất hay không,

Để đánh giá tính faithful của mô hình.

## 4. Functional Requirements

### FR-01: Data Loading

Hệ thống phải đọc được dữ liệu đầu vào bao gồm:

- ticker
- forecast_time
- news[news_id, news_time, title, text]
- label

### FR-02: Temporal Retriever

Hệ thống phải:

- So sánh news_time với forecast_time.
- Loại bỏ các tin xuất hiện sau forecast_time.
- Trả về: valid_news, invalid_future_news

### FR-03: Evidence Extraction

Hệ thống phải:

- Trích xuất evidence_text từ news_text.
- expected_direction: UP, DOWN, HOLD.

### FR-04: Evidence Selection

Hệ thống phải:

- Chọn evidence quan trọng nhất.
- Hỗ trợ phân loại: pro evidence, counterevidence.

### FR-05: Forecast Model

Hệ thống phải sinh:

- prediction
- confidence score

Prediction gồm:

- UP
- DOWN
- HOLD

### FR-06: Faithfulness Evaluation

Hệ thống phải tính:

**Evidence Support:** Đánh giá evidence có phù hợp với prediction hay không.

ES = số evidence cùng chiều prediction / tổng evidence

**Temporal Validity:** Đánh giá dữ liệu có vi phạm thời gian hay không.

TV = số evidence hợp lệ / tổng evidence

**Confidence Drop:** So sánh confidence trước khi loại evidence và sau khi loại evidence.

CD = Original Confidence − Confidence Without Evidence

### FR-07: Visualization Dashboard

Dashboard phải hiển thị:

- Prediction Distribution
- Evidence Table
- Confidence Drop Chart
- Temporal Leakage Warning

### FR-08 Error Handling

Hệ thống phải phát hiện và ghi log các dữ liệu không hợp lệ.

### FR-09 Dataset Validation

Dataset phải có tối thiểu 30 bản ghi.

Dataset phải chứa cả:
- valid news
- invalid future news

## 5. Non-Functional Requirements

### NFR-01: Performance

Hệ thống phải xử lý ít nhất 30 bản ghi dữ liệu trong vòng dưới 5 giây trên máy tính cá nhân.

### NFR-02: Reliability

Lỗi của một bản ghi không được làm dừng toàn bộ pipeline.

### NFR-03 Maintainability

Các module Retriever, Extractor, Forecast, Evaluator và Dashboard phải hoạt động độc lập.

### NFR-04 Explainability

Mọi prediction phải có ít nhất một evidence đi kèm.

## 6. Input Specification

### Input Schema

```json
{
  "ticker": "AAPL",
  "forecast_time": "2025-03-12 09:00",
  "news": [
    {
      "news_id": "N001",
      "news_time": "2025-03-11 08:30",
      "title": "Apple reports weak iPhone sales in China",
      "text": "..."
    }
  ],
  "price_features": {
    "price_5d_return": -0.02,
    "volume_change": 0.15
  },
  "label": "DOWN"
}
```

## 7. Output Specification

### Output Schema

```json
{
  "ticker": "AAPL",
  "prediction": "DOWN",
  "confidence": 0.72,
  "evidence": [
    {
      "news_id": "N001",
      "evidence_text": "weak iPhone sales in China",
      "polarity": "negative",
      "expected_direction": "DOWN",
      "support_score": 1.0
    }
  ],
  "faithfulness": {
    "temporal_validity": 1.0,
    "evidence_support": 1.0,
    "confidence_drop": 0.21
  }
}
```

## 8. Module Specification

### Module 1: Temporal Retriever

#### Input:

- forecast_time
- news_list

#### Output:

- valid_news
- invalid_future_news

### Module 2: Evidence Extractor

#### Imput:

- valid_news

#### Output:

- evidence_text
- polarity
- expected_direction

### Module 3: Evidence Selector

#### Input:
- extracted evidence

#### Output:
- pro evidence
- counterevidence
- top-k evidence

### Module 4: Forecast Model

#### Input:

- evidence
- price_features

#### Output:

- prediction
- confidence

### Module 5: Faithfulness Evaluator

#### Input:

- prediction
- confidence
- evidence

#### Output:

- evidence_support
- temporal_validity
- confidence_drop

### Module 6: Dashboard

#### Input:

- prediction result
- faithfulness metrics

#### Output:

- Charts
- Tables
- Warnings

## 9. Acceptance Criteria

### AC-01: Temporal Filtering

Given một news có news_time > forecast_time

When hệ thống thực hiện retrieval

Then news đó phải nằm trong invalid_future_news

And không được sử dụng trong prediction.

### AC-02: Evidence Extraction

Given một tin tức hợp lệ

When hệ thống thực hiện extraction

Then phải sinh được ít nhất một evidence.

### AC-03: Prediction

Given dữ liệu hợp lệ

When hệ thống chạy forecasting

Then phải sinh prediction thuộc tập:

- UP
- DOWN
- HOLD

And confidence phải nằm trong khoảng [0,1].

### AC-04: Faithfulness Metric

Given một prediction có evidence

When evidence bị loại bỏ

Then hệ thống phải tính được confidence drop.

### AC-05: Dashboard

Given prediction đã được sinh

When người dùng mở dashboard

Then hệ thống phải hiển thị:

- prediction
- confidence
- evidence
- faithfulness metrics

### AC-06: Temporal Leakage Warning

Given tồn tại future news

When dashboard được hiển thị

Then hệ thống phải hiển thị cảnh báo temporal leakage.

### AC-07: Counterevidence Coverage

Khi tin tức có chứa từ khóa trái ngược, hệ thống phải trích xuất được counter_evidence và cập nhật has_counter = True.

### AC-08: Market Consistency

Hệ thống phải tính toán được consistency_score dựa trên tương quan giữa label và price_5d_return.

### AC-09: Agentic Trace

Mỗi luồng thực thi phải ghi lại được Trace Log (JSONL) bao gồm role, task và reflection.

## 10. Agentic SDLC Integration

### Research Agent

Nhiệm vụ:

- Phân tích yêu cầu.
- Xây dựng user stories.
- Đề xuất metrics.

### Coding Agent

Nhiệm vụ:

- Sinh code mẫu.
- Hỗ trợ implementation.

### Testing Agent

Nhiệm vụ:

- Sinh test cases.
- Kiểm tra temporal leakage.
- Đánh giá chất lượng đầu ra.

### Quality Gate:

- Spec approved
- Test passed
- No temporal leakage
- Dashboard displays metrics correctly

### Human Quality Gate

Con người phải:

- Review spec.
- Review design.
- Review code.
- Review test results.
- Phê duyệt trước khi tích hợp.

## 11. Giới hạn hệ thống

- Không đảm bảo lợi nhuận đầu tư.
- Dataset nhỏ có thể gây bias.
- Evidence extraction có thể sai với tin tức mơ hồ.
- Rule-based model có độ chính xác hạn chế.
- Faithfulness metric chỉ phản ánh một phần mức độ giải thích của mô hình.
- Tuyệt đối không sử dụng dữ liệu xuất hiện sau forecast_time.