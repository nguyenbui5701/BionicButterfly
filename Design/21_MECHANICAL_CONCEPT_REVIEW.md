# BionicButterfly — Review Gate cho Mechanical Concept V1

- **Document ID:** BB-MECH-GATE-021
- **Version:** 0.1 · 2026-11-12
- **Owner:** Solution Architect · **Status:** PROPOSED / NO-GO UNTIL VERIFIED
- **Inputs:** `03_HARDWARE_DESIGN.md`, `17_MECHANICAL_FLIGHT_FEASIBILITY.md`, `18_MECHANICAL_EXPERIMENT_PLAN.md`, `19_MECHANICAL_CONCEPT_DESIGN.md`, `20_PRELIMINARY_BOM_MASS_POWER.md`.

## 1. Thiết kế chưa “approved” là điều bình thường

V1 yêu cầu **bay tự do được điều khiển bằng tay cầm**, nhưng chọn phần cứng phải đi qua kiểm chứng. Cần phân biệt ba trạng thái: (a) mẫu để bàn thử, (b) mẫu đủ điều kiện đánh giá bay, (c) mẫu bay thật điều khiển được. Không chấp nhận mô phỏng waveform hay một clip bay tham khảo như bằng chứng đạt (c).

## 2. Design review checklist MC-01 … MC-12

| ID | Điều kiện | Evidence / pass rule đề nghị | Trạng thái |
|---|---|---|---|
| MC-01 | Mục tiêu và scope | V1 RC manual / V2 autonomy đã xác nhận | **DECIDED scope** |
| MC-02 | Hệ trục/hình học | CAD/drawing có `b`, `S`, chiều dài thân, góc lắp, clearance có dung sai | NOT RUN |
| MC-03 | Cấu trúc cánh | cân L/R, vật liệu và khả năng xoắn, va chạm, độ cứng/độ bền | NOT RUN |
| MC-04 | Servo và truyền động | datasheet model, biên độ/trục/servo horn, dòng & nhiệt khi tải thực; không stall | NOT RUN |
| MC-05 | Mass budget | cân m_total từng revision, đo CG, xác định biên dự phòng và rework nếu vượt | NOT RUN |
| MC-06 | Nguồn điện | sơ đồ 2S, BEC, rail servo/logic, peak I, thermal, safe charging; không brownout | NOT RUN |
| MC-07 | RC receiver | signal level, bind, link, arm switch, mất sóng, một owner | NOT RUN |
| MC-08 | Force / moment | MX-07 baseline+calibration+uncertainty, không suy diễn free flight từ lực tĩnh | NOT RUN |
| MC-09 | Steering authority | MX-08 chứng minh chiều và lặp lại của moment ứng với RC steer | NOT RUN |
| MC-10 | Pitch/roll | kế hoạch xác minh ổn định dọc/ngang; cách giải quyết nếu 2 servo không đủ | NOT RUN |
| MC-11 | Failsafe khi bay | flight-specific plan sau G3, không mặc định cắt cánh giữa không trung là an toàn | NOT RUN |
| MC-12 | LED configuration | C0 pass trước; C1 cân/đo lại `f_actual`, lực, nhiệt, EMI, ổn định | NOT RUN |

## 3. Decision gates

**G0 Concept selection** — cần: (i) owner approve architecture intent, (ii) CAD sơ bộ và danh sách ứng viên, (iii) kế hoạch kiểm thử & rig an toàn, (iv) risk register và BOM đo khối lượng tối thiểu có mục tiêu. `G0` không phải phép bay.

**G1 Simulator** — state machine/safety/command timing được test bằng virtual time; chỉ phần mềm, không tự xác minh khí động.

**G2 Free servo bench** — đo PWM/servo/BEC, hết lỗi cấp nguồn, soft-limit; không gắn cánh.

**G3 Restrained wing rig** — đo `f_actual`, L/R, lực, mô-men, rung, dòng & nhiệt, liên kết RC/failsafe. Có checkpoint Go/No-Go giữa các dải tải; sau đó đánh giá cả pitching moment, không chỉ yaw.

**G4 Controlled flight** — riêng một buổi xem xét bay có địa điểm/người điều khiển/rủi ro/kế hoạch thu hồi/thiết bị bảo vệ. Nếu vẫn không thể điều khiển pitch/roll hoặc chứng minh ổn định thì **KHÔNG ĐƯỢC qua G4**. Kết quả bay ghi video/log và số liệu theo FR-019, MX-10.

## 4. Quyết định bắt buộc trước khi tạo Task phát triển

- [ ] **D-015:** chấp thuận concept `M1/C0` để thiết kế CAD/bench (không phê duyệt bay hay BOM); phương án M2/M3 là fallback.
- [ ] **D-016:** phê duyệt phân bổ khối lượng 70 g như **target phân tích**, không cam kết hiệu năng; hoặc chọn giá trị khác.
- [ ] **D-017:** đồng ý C1 LED là revision bay phải được đánh giá độc lập, sau C0.
- [ ] **D-018:** phê duyệt nguồn 2S + regulator đúng datasheet như kiến trúc thăm dò (không chốt part).
- [ ] Xác định **ngân sách phần cứng**, vật tư/thiết bị đã có và địa điểm bench phù hợp.
- [ ] Tài liệu requirements + architecture + safety + SA/dev rules được owner duyệt trước khi tạo `Task/`.

**Không ai được chuyển `PROPOSED` thành `APPROVED` chỉ vì tài liệu đã được đưa lên GitHub.**

## 5. Biểu mẫu review decision

```text
Review date / revision:
Reviewed artifacts and version:
Owner decision: APPROVE CONCEPT / REWORK / DEFER
Selected concept: M1 C0 / M2 / M3
Budget cap (currency, excluding or including tools):
Evidence accepted:
Blocking unknowns / next measurements:
Safety constraints:
Sign-off reference (user message/issue/PR):
Next artifact (Design only):
```

## 6. Điểm cần nghiên cứu thêm của SA (không phải yêu cầu Dev)

1. Dựng bản CAD có kích thước sau khi chủ dự án quyết định phong bì b/spans, vật liệu và nhà chế tạo. Không tự ý tái dùng STL có giấy phép không rõ.
2. Đề xuất 2–3 thiết bị đo tối thiểu/rig dựa vào budget; xây dựng worksheet nhập số cân và lực thực.
3. Xác định điều khiển được cả hướng dọc/ngang: có thể cần thay wing geometry hoặc mở quyết định stabilization assistance dù V1 vẫn là RC manual.
4. Kiểm tra ngân sách mass/power của C0 so với datasheet và chi phí thực tại Việt Nam, chỉ lập shopping list khi owner chọn ngân sách.

*Changelog v0.1 — Mechanical Concept Review draft; no code task.*
