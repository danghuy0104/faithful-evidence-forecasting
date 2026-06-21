# Task Allocation & Management (Nhóm 3 Thành viên)

**Quy ước trạng thái:**
* `[ ]` = Chưa làm
* `[x]` = Đã hoàn thành

**Phân công vai trò:**
* **SV1:** Research & Spec Owner
* **SV2:** ML/NLP Engineer
* **SV3:** Visualization & QA Engineer

---

## 1. OpenSpec & Agentic SDLC (A1) — Phụ trách: SV1
* [x] Viết `proposal.md` (bối cảnh, động lực, mục tiêu, vai trò AI agent trong SDLC)
* [x] Viết `spec.md` (input/output, chức năng chính, acceptance criteria Given/When/Then)
* [x] Viết `tasks.md` (file này)
* [x] Viết `design.md` (kiến trúc pipeline, data schema chi tiết, lựa chọn công nghệ)
* [x] Viết `metric_definition.md` (định nghĩa công thức Evidence Support, Temporal Validity, Confidence Drop)

## 2. Dataset mẫu (A2) — Phụ trách: SV2
* [ ] Tạo file `data/sample_news_price.csv` với tối thiểu 30 dòng
* [ ] Đảm bảo có đủ các trường: `ticker`, `forecast_time`, `news_time`, `news_text`, `label` (UP/DOWN/HOLD)
* [ ] Đưa vào ít nhất 5-10 dòng có `news_time` sau `forecast_time` để test temporal leakage
* [ ] Thống nhất với cả nhóm bộ ticker mẫu dùng chung (ví dụ: AAPL, TSLA, NVDA) trước khi viết code các module khác để tránh dữ liệu không khớp giữa các phần

## 3. Temporal Retriever (A3) — Phụ trách: SV2
* [ ] Viết `src/retriever.py`: hàm lọc tin theo `forecast_time`, trả về `valid_news` và `invalid_future_news`
* [ ] Viết test case minh họa lỗi temporal leakage (ví dụ: `forecast_time` 09:00, `news_time` 15:00 cùng ngày $\rightarrow$ bị loại)
* [ ] Bàn giao cho SV3 để viết `tests/test_temporal_retriever.py`

## 4. Evidence Extraction (A4) — Phụ trách: SV2
* [ ] Viết `src/evidence_extractor.py`: trích xuất `evidence_text` từ `news_text`
* [ ] Phân loại `polarity` (positive/negative/neutral) và `expected_direction` (UP/DOWN/HOLD)
* [ ] Chuẩn bị tối thiểu 5 ví dụ đúng và 5 ví dụ sai để minh họa độ chính xác của bước trích xuất

## 5. Forecast Model cơ bản (A5) — Phụ trách: SV2
* [ ] Viết `src/forecast_model.py`: xây dựng rule-based model (ví dụ: `positive_count` − `negative_count` > 0 $\rightarrow$ UP, < 0 $\rightarrow$ DOWN, = 0 $\rightarrow$ HOLD)
* [ ] Trả về kèm `confidence`/`score` cho mỗi prediction
* [ ] Tính accuracy hoặc confusion matrix trên dataset mẫu
* [ ] Chuẩn bị 1 ví dụ giải thích chi tiết một prediction cụ thể (để dùng trong báo cáo và demo)

## 6. Faithfulness Metrics cơ bản (A6) — Phụ trách: SV2 *(phối hợp với SV1 về định nghĩa metric)*
* [ ] Viết `src/faithfulness_metrics.py`: tính toán *Evidence Support* và *Temporal Validity*
* [ ] Viết hàm tính *Confidence Drop*: chạy lại forecast sau khi bỏ cited evidence khỏi input, so sánh confidence trước/sau
* [ ] Xuất bảng kết quả faithfulness cho nhiều mẫu ra file `outputs/faithfulness_results.csv`

## 7. Visualization Dashboard & báo cáo (A7) — Phụ trách: SV3
* [ ] Viết `src/dashboard.py` (sử dụng Jupyter Notebook hoặc Streamlit — theo lựa chọn đã thống nhất của nhóm)
* [ ] Tạo tối thiểu 4 bảng/hình:
  * Prediction distribution
  * Evidence table
  * Confidence drop chart
  * Temporal leakage warning
* [ ] Lưu hình ảnh vào thư mục `outputs/figures/`:
  * `prediction_distribution.png`
  * `confidence_drop.png`
  * `temporal_leakage_warning.png`
  * `faithfulness_radar.png`
* [ ] Hỗ trợ SV1 viết phần 4-7 của báo cáo (mô tả dữ liệu, pipeline, metric, kết quả thực nghiệm)

## 8. Testing & QA — Phụ trách: SV3
* [ ] Viết `tests/test_temporal_retriever.py` (dựa trên test case của SV2 ở mục 3)
* [ ] Viết `tests/test_metrics.py` cho các hàm trong `faithfulness_metrics.py`
* [ ] Chạy lại toàn bộ test trước khi nộp, đảm bảo không còn lỗi tồn đọng

## 9. Báo cáo & Demo — Phụ trách: Toàn nhóm *(SV1 chủ trì tổng hợp)*
* [ ] Viết phần 1-3 báo cáo (giới thiệu, research gap, thiết kế Agentic SDLC) — **SV1**
* [ ] Viết phần 4-7 báo cáo (dữ liệu, pipeline, metric, kết quả) — **SV2 + SV3**
* [ ] Viết phần 8-10 báo cáo (phân tích case đúng/sai, limitations, phụ lục) — **Toàn nhóm**
* [ ] Quay video demo theo kịch bản 5 phút (mục 11.1 trong đề bài) — **Toàn nhóm**
* [ ] Chuẩn bị câu trả lời cho các câu hỏi phản biện (mục 11.3 trong đề bài) — **Toàn nhóm** *(SV1 hỗ trợ phần lý thuyết)*

## 10. Mở rộng (Phần B / Điểm cộng) — *Chỉ làm nếu còn thời gian*
* [ ] **B1:** Sufficiency + Counterfactual Perturbation
* [ ] **B2:** Counterevidence Coverage
* [ ] **B3:** Market Consistency + Regime Analysis
* [ ] **B4:** Agentic SDLC Maturity (multi-agent role, trace log, quality gate)
* [ ] **C1:** Thay dataset mô phỏng bằng dữ liệu thật ($\ge$ 3 ticker, $\ge$ 300 mẫu)
* [ ] **C2:** Thay rule-based model bằng FinBERT/LSTM/Transformer (yêu cầu GPU)
