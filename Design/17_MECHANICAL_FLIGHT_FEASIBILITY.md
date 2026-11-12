# BionicButterfly — Nghiên cứu tính khả thi bay và chọn cơ cấu V1

- **Document ID:** BB-MECH-017
- **Version:** 0.1 — 2026-11-12
- **Owner:** Solution Architect (SA)
- **Status:** PROPOSED / RESEARCH — chưa phê duyệt cơ cấu, BOM hoặc chuyến bay
- **Phạm vi:** V1 bay thật bằng tay cầm RC; V2 tự bay sau khi V1 hoàn tất
- **Liên quan:** `02_V1_REQUIREMENTS.md`, `03_HARDWARE_DESIGN.md`, `13_V1_ARCHITECTURE_PROPOSAL.md`, `14_V1_VERIFICATION_PLAN.md`, `15_V1_DECISION_REGISTER.md`, `16_RC_INTERFACE_CONTRACT.md`, `18_MECHANICAL_EXPERIMENT_PLAN.md`

## 1. Mục đích và giới hạn bằng chứng

Mục tiêu là xác định liệu cơ cấu cánh vỗ có thể tạo đủ điều kiện cho **bay có lực đẩy/lực nâng và điều khiển hướng bằng RC**, không chỉ chuyển động trên bàn thử. Video b1–b4 thể hiện hình dáng bướm, hiệu ứng LED và những đoạn bay/điều khiển; video **không xác định chính xác khối lượng, lực khí động, servo, pin, tín hiệu RC hay thuật toán ổn định**.

Quy ước bằng chứng: **OBSERVED** (nhìn được trong video/đọc mã nguồn), **PUBLISHED** (tài liệu tác giả/nghiên cứu), **HYPOTHESIS** (giả thuyết), **MEASURED** (thử trên mẫu của chúng ta), **OWNER-DECIDED** (chủ dự án đã chốt). Không dùng PUBLISHED thay cho MEASURED.

### Nền tảng tham chiếu bên ngoài

| Hệ | Sải cánh | Khối lượng | Tần số | Điều kiện kiểm soát và giới hạn áp dụng |
|---|---:|---:|---:|---|
| Festo eMotionButterflies (2015) | 50 cm | 32 g | ~1–2 Hz | Hai servo; có IMU và hệ camera hồng ngoại định vị bên ngoài; không thể suy ra rằng điều khiển RC thuần túy sẽ đạt hiệu quả tương đương |
| RoboButterfly-I (2016, bảng tổng quan) | 62 cm | 39,6 g | 1,8–3,2 Hz | Có báo cáo bay điều khiển, thông số của mẫu nghiên cứu khác |
| RoboButterfly-II (2020, bảng tổng quan) | 63 cm | 45,8 g | 2–3,9 Hz | Có báo cáo bay điều khiển, không phải cấu hình của chúng ta |
| ESP-FLUTTER (bản maker) | chưa xác minh | ~70 g | chưa xác minh | Khối lượng do tác giả đưa ra theo tài liệu tổng hợp; không phải chứng nhận hiệu năng độc lập |

**Nguồn:**
- Festo, tài liệu kỹ thuật eMotionButterflies: https://www.festo.com/PDF_Flip/corp/Festo_eMotionButterflies/en/index.htm
- Tổng quan các nguyên mẫu mô phỏng bướm (bảng 1): https://cje.ustb.edu.cn/article/doi/10.13374/j.issn2095-9389.2023.10.11.002
- Tổng quan về robot cánh vỗ và cấu hình truyền động: https://journals.sagepub.com/doi/full/10.1177/02783649251343638
- ESP-FLUTTER, thông tin thứ cấp và tuyên bố của tác giả: https://mcuatlas.com/projects/esp-flutter-rc-butterfly/

**Không sao chép** bản vẽ, CAD, STL, hình cánh hoặc firmware chỉ vì có trang công khai; kiểm tra giấy phép từng tài sản và ghi nguồn trong `01_REFERENCE_AUDIT.md`.

## 2. So sánh phương án truyền động

| Tiêu chí | M1: 2 servo riêng L/R (ưu tiên nghiên cứu) | M2: 1 motor quay + crank-rocker | M3: 2 motor giảm tốc độc lập |
|---|---|---|---|
| Khả năng đổi quỹ đạo cánh L/R độc lập | Trực tiếp | Không tự nhiên; cần cơ cấu lái bổ sung | Có, nhưng đòi hỏi đo pha/tốc độ |
| Độ phức tạp phần mềm ban đầu | Vừa | Thấp phần vỗ; tăng ở cơ cấu lái | Cao hơn vì điều khiển motor/pha |
| Rủi ro cơ khí | Rung, tốc độ/torque thực và hộp số servo | Backlash, khớp nối, ứng suất và tổn hao | Khớp truyền và đồng bộ pha |
| Khối lượng, hiệu suất | Chưa đo; 2 servo có thể là gánh nặng | Có tiềm năng tối ưu với thiết kế tốt | Có tiềm năng nhưng cần phát triển nhiều |
| Phù hợp mục tiêu V1 RC-first | **Ưu tiên P0 để thử**, chưa chọn chính thức | Phương án thay thế nếu M1 không đạt | Phương án nghiên cứu sau nếu M1 thất bại |

**Khuyến nghị SA:** bắt đầu từ **M1 — hai servo độc lập**, vì đã có mẫu nghiên cứu trực tiếp cánh L/R và phù hợp nhu cầu hiệu chỉnh/điều hướng từ tay cầm. **Không chốt model servo, tốc độ, số răng truyền hay layout cánh** cho đến khi đo tải; nếu không đạt, SA phải cập nhật ADR và chuyển cơ cấu, không cho Dev tự thay kiến trúc.

## 3. Cơ khí và hình học phải đo

Một bộ cánh ứng viên có ít nhất các tham số sau (đơn vị bắt buộc):

```text
b        : sải cánh tổng [m]
S        : tổng diện tích chiếu bằng thực của hai phía cánh [m²]
m_wing   : khối lượng màng + gân + bản lề [kg]
phi_L/R  : góc vỗ cánh thực đo của trái/phải [deg]
f_actual : tần số vỗ thực [Hz] (không dùng f_command thay thế)
x_CG     : vị trí trọng tâm với hệ trục gốc được định nghĩa [mm]
x_CP     : vùng tâm áp lực/điểm tác dụng lực *ước lượng* [mm]
F_x,F_z  : lực đo trên rig theo trục đã hiệu chuẩn [N]
I,V      : dòng/điện áp trong quá trình vỗ tải [A,V]
```

- **Màng cánh:** tối ưu nhẹ, căng phù hợp nhưng vẫn có độ mềm để tạo biến dạng khí động. So sánh ít nhất hai cấu hình cánh có cùng cách đo; không tự suy đoán chất liệu nào tốt nhất từ màu sắc/video.
- **Gân cánh và bản lề:** quan sát xoắn, lệch pha, dao động riêng, va chạm thân/cánh trong toàn biên độ. Cánh trái/phải phải đối xứng về hình học và cân khối lượng đến mức có thể đo được.
- **Trọng tâm (CG):** xác định CG tổng khi lắp pin và receiver; ghi tọa độ, ảnh chụp và phương pháp đo. Không khẳng định CG phù hợp chỉ vì đặt pin ở giữa.
- **Điều khiển hướng:** chênh lệch quỹ đạo cánh có thể tạo mô-men, nhưng hiệu quả và dấu chiều quay phải đo; **điều khiển yaw không chứng minh điều khiển pitch/roll**. Nếu thiếu thẩm quyền điều khiển, xem xét hình học cánh, góc lắp, vị trí CG hoặc cơ cấu điều khiển bổ sung trong revision kiến trúc.
- **LED:** tùy chọn sau phiên bản cơ khí tối thiểu; LED làm tăng khối lượng ở mép cánh và mô-men quán tính, có thể làm giảm tần số thực và hiệu năng. Không đưa LED vào mẫu thử lực đầu tiên.

## 4. Ngân sách khối lượng và bài toán lực — chỉ là kịch bản

Trọng lực: `W = m*g`, với `g ≈ 9,80665 m/s²`. Lực cần đánh giá phụ thuộc chế độ bay thực tế; **không thể xác nhận bay bằng việc so sánh duy nhất lực đo tĩnh với W**.

| Kịch bản toàn bộ khối lượng (g) | Trọng lượng W (N) | Ghi chú |
|---:|---:|---|
| 40 | 0,392 | Kịch bản nhẹ, không phải cam kết BOM |
| 55 | 0,539 | Kịch bản trung gian |
| 70 | 0,686 | Kịch bản nặng, cần bằng chứng lực mạnh hơn |

Các giá trị làm tròn; chỉ dùng để hình dung **độ nhạy theo khối lượng**. Không có giá trị nào ở bảng này là kết quả cân mẫu thật. Chỉ số wing loading `W/S [N/m²]` chỉ tính được khi **S đo thực tế**. Chưa công bố một chỉ tiêu lift-to-weight hay tần số bắt buộc khi chưa biết chế độ bay và kết quả thử rig.

### Mẫu bảng cân BOM (cần số đo)

| Cụm | Khối lượng dự kiến (g) | Khối lượng thực đo (g) | Dẫn chứng |
|---|---:|---:|---|
| Cánh trái + phải, gân, khớp | TBD | — | cân điện tử + ảnh |
| 2 servo + horn + dây + linkage | TBD | — | model, datasheet, cân |
| Thân/khung/fastener | TBD | — | CAD + cân |
| MCU + RC RX + dây/đầu nối | TBD | — | cân |
| Pin + BEC/regulator + bảo vệ | TBD | — | cân + kiểm tra tải |
| LED / trang trí | TBD | — | chỉ sau mẫu bare-airframe |
| **All-up mass / CG** | **TBD** | **—** | **chưa đo** |

**Dấu hiệu dừng hoặc thiết kế lại:** cơ cấu bị kẹt khi có tải, nhiệt/dòng tăng bất thường, rung làm lệch cánh/servo, tốc độ thực sụt rõ, nguồn tụt khiến MCU reset, hoặc thử lực không cho thấy hướng cải thiện khi tối ưu hình học/khối lượng.

## 5. Điều kiện để quyết định M1 có đáng tiếp tục hay không

1. Có dữ liệu cân từng cụm và CG sau khi lắp toàn bộ cấu hình tối giản.
2. Có ảnh/video vỗ cánh ở nhiều mức lệnh cùng `f_actual`, biên độ thực và sai lệch L/R.
3. Có đồ thị điện áp, dòng trung bình/đỉnh, nhiệt độ, dấu hiệu stall khi gắn cánh.
4. Có đo force/moment ở rig cố định (ít nhất một trục theo thiết kế thí nghiệm) kèm baseline, nhiễu, hướng trục và sai số.
5. Có bằng chứng khả năng đổi mô-men lực khi thay `steering` mà không phá vỡ độ ổn định nguồn/cơ cấu.
6. Có quyết định SA về **CONTINUE M1 / REWORK M1 / SWITCH M2/M3 / NO-GO**, dựa trên dữ liệu; không dùng một video bay của upstream làm PASS của chúng ta.

## 6. Giả thuyết về tự ổn định

**V1 manual RC ≠ bắt buộc không dùng IMU.** Có thể cần bộ ổn định attitude cơ bản để hỗ trợ người lái, vẫn không phải tự bay theo waypoint. Tuy nhiên, việc thêm IMU, hệ PID hay telemetry phải được quyết định sau khi đo điều khiển trên rig và đánh giá ngân sách khối lượng. Không tự động mở rộng scope sang V2.

## 7. Quyết định đang chờ

- D-011: thí nghiệm M1 trước, vẫn giữ M2/M3 làm phương án dự phòng (**PROPOSED**).
- D-012: mẫu bare-airframe không LED để kiểm chứng bay; LED thêm sau (**PROPOSED**).
- D-013: khối lượng/tầm sải cánh lấy từ tài liệu công bố chỉ là **benchmark**, không phê duyệt làm thông số chế tạo (**PROPOSED**).
- D-014: phân biệt RC thủ công và ổn định attitude hỗ trợ (**PROPOSED**).

**Chưa có task `Task/` vì design vẫn đang ở trạng thái PROPOSED.**
