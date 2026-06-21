# Project Proposal: Faithful Evidence-Centric Financial News Forecasting

## Why

Nhiều hệ thống AI hiện nay có thể đọc tin tức tài chính và dự báo cổ phiếu sẽ tăng, giảm hoặc đi ngang, đồng thời đưa ra một đoạn giải thích (*rationale*) nghe có vẻ hợp lý. Tuy nhiên, một lời giải thích nghe hợp lý không đồng nghĩa với việc nó thật sự là nguyên nhân khiến mô hình ra quyết định đó. 

Đây chính là khoảng trống nghiên cứu (*research gap*) mà đồ án này muốn giải quyết: **phần lớn các hệ thống dự báo hiện tại chỉ được đánh giá bằng `accuracy`, mà bỏ qua việc kiểm chứng `explanation faithfulness` — liệu evidence được trích dẫn có thật sự quyết định prediction hay không.**

### Câu hỏi nghiên cứu trung tâm của đồ án:
> *Khi một mô hình dự báo stock movement từ news, liệu evidence mà nó đưa ra có thật sự quyết định prediction không?*

Nếu không kiểm chứng được điều này, một mô hình có thể trông đáng tin (vì giải thích nghe hợp lý) trong khi thực chất dự báo dựa trên một yếu tố khác hoàn toàn không liên quan, hoặc tệ hơn là dựa trên dữ liệu tương lai bị lọt vào (*temporal leakage*) — điều cực kỳ nguy hiểm nếu áp dụng trong môi trường tài chính thực tế.

---

## What Changes

Đồ án xây dựng một prototype nhỏ gồm các thành phần sau (không xây dựng hệ thống giao dịch thật):

* **Temporal Retriever:** Lọc tin tức, chỉ giữ lại tin xuất hiện trước thời điểm dự báo (`forecast_time`), loại bỏ tin vi phạm thời gian (*temporal leakage*).
* **Evidence Extractor:** Trích xuất các đoạn evidence ngắn từ tin tức, gán `polarity` (positive/negative/neutral) và `expected_direction` (UP/DOWN/HOLD).
* **Forecast Model:** Dự báo xu hướng cổ phiếu UP/DOWN/HOLD kèm `confidence score`, có khả năng giải thích bằng evidence được trích dẫn (*cited evidence*).
* **Faithfulness Evaluator:** Tính các metric kiểm chứng evidence — *Evidence Support*, *Temporal Validity*, *Confidence Drop* (khi bỏ cited evidence khỏi input).
* **Visualization Dashboard:** Hiển thị prediction, evidence, cảnh báo temporal leakage và các biểu đồ liên quan để con người (nhà phân tích) có thể tự đánh giá độ tin cậy của dự báo.

> **Phạm vi triển khai ban đầu (MVP):** Tập trung vào yêu cầu cơ bản (Phần A trong đề bài) bao gồm dữ liệu mô phỏng, rule-based model, 3 metric faithfulness cơ bản và dashboard ở dạng notebook. 
> 
> Các yêu cầu nâng cao (Phần B: *counterfactual perturbation, counterevidence coverage, market consistency, agentic SDLC maturity*) và điểm cộng (dữ liệu thật, GPU) sẽ được xem xét bổ sung sau khi MVP hoàn chỉnh, theo nguyên tắc làm tới đâu chắc tới đó.

---

## AI Agent trong SDLC

Đồ án sử dụng AI agent (ví dụ: Claude / ChatGPT / Cursor) như một tác nhân hỗ trợ có kiểm soát trong từng pha của SDLC, không để agent tự quyết định thiếu kiểm soát. Cụ thể:

| Pha SDLC | AI Agent hỗ trợ | Sinh viên kiểm soát | Minh chứng |
| :--- | :--- | :--- | :--- |
| **Requirement** | Soạn user stories, acceptance criteria nháp | Kiểm tra yêu cầu có rõ ràng và test được không | `proposal.md`, `spec.md` |
| **Design** | Đề xuất kiến trúc pipeline, data schema | Chọn thiết kế phù hợp với năng lực nhóm | `design.md` |
| **Implementation** | Sinh code mẫu, gợi ý hàm xử lý | Đọc hiểu, kiểm tra và chỉnh sửa code trước khi dùng | `src/`, commit log |
| **Testing** | Sinh test case (bao gồm test temporal leakage) | Tự chạy test, xác minh và sửa lỗi | `tests/`, test report |
| **Evaluation** | Gợi ý metric, hỗ trợ phân tích kết quả | Không overclaim kết quả, tự đối chiếu với giới hạn dữ liệu | Bảng kết quả, hình ảnh |
| **Operation** | Gợi ý cấu trúc trace/log | Không để agent tự quyết định, luôn có người review | `run_log.json`, dashboard |

Mọi output do AI agent tạo ra đều phải qua review của con người (**human-in-the-loop**) trước khi được chấp nhận vào sản phẩm cuối cùng — điều này được ghi nhận cụ thể trong các file log/trace ở phần Operation và trong `tasks.md`.

---

## Impact

* **Affected specs:** `forecasting` (capability mới, xem tại `specs/forecasting/spec.md`).
* **Affected code:** Toàn bộ thư mục `src/` (`retriever`, `evidence_extractor`, `forecast_model`, `faithfulness_metrics`, `dashboard`) — đây là capability đầu tiên của dự án, chưa có code cũ bị ảnh hưởng.
* **Out of scope:** Hệ thống giao dịch thật, khuyến nghị mua/bán cổ phiếu thật (xem giới hạn đạo đức trong báo cáo, mục *Limitations*).
