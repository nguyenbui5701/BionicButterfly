# BionicButterfly — Kế hoạch thử nghiệm cơ khí, năng lượng và lực khí động V1

- **Document ID:** BB-MECH-TEST-018
- **Version:** 0.1 — 2026-11-12
- **Status:** PROPOSED / NOT RUN — không phải giấy phép vận hành thử
- **Owner:** Solution Architect
- **Refs:** `03_HARDWARE_DESIGN.md`, `14_V1_VERIFICATION_PLAN.md`, `17_MECHANICAL_FLIGHT_FEASIBILITY.md`, `16_RC_INTERFACE_CONTRACT.md`

## 1. Nguyên tắc

Chạy tuần tự **G0 (design) → G1 (simulator) → G2 (servo không cánh) → G3a (cơ cấu cánh trên rig) → G3b (đánh giá lực/điều hướng) → G4 (bay thật có phê duyệt riêng)**. Ở mỗi bước phải ghi nguồn dữ liệu, cấu hình, điều kiện và trạng thái `NOT RUN | PASS | FAIL | BLOCKED`. Kiểm thử rig không đủ để tuyên bố máy bay có thể bay được; chuyển sang G4 cần duyệt rủi ro độc lập.

## 2. Kế hoạch thử / chỉ số / tiêu chí

| ID | Gate | Mục tiêu | Đại lượng cần ghi | PASS tạm thời — sẽ cụ thể khi có phần cứng |
|---|---|---|---|---|
| MX-01 | G0 | Cân mass budget và CG | m từng cụm [g], m_total [g], x/y/z CG [mm] | Tổng khối lượng khớp tổng cụm trong sai số cân; CG có phương pháp và ảnh |
| MX-02 | G0 | Kiểm tra hình học | b [m], S [m²], khối lượng màng/gân, góc lắp, đối xứng | Mẫu đo có ảnh/thước, vùng sai số; không va chạm bằng kiểm tra tay khi chưa cấp điện |
| MX-03 | G2 | Lệnh PWM và giới hạn servo không cánh | min/max thực [deg], pulse [µs], t đáp ứng, dao động và dòng | Không overtravel, không tự kích ở boot/arming, ngắt/mất tín hiệu xử lý đúng bench policy |
| MX-04 | G2 | Đường nguồn khi servo tải nhẹ | V_bat, V_servo, V_MCU, I_peak, I_avg, nhiệt, reset | Không vượt datasheet; không reset MCU; chưa chọn ngưỡng số đến khi biết bộ nguồn |
| MX-05 | G3a | Chuyển động cánh có tải trên rig | `f_cmd`, `f_actual`, biên độ L/R, lag, nhiệt, dòng, video | Không kẹt/gãy; sai lệch được định lượng; tối thiểu 3 mức lệnh với thời gian định trước |
| MX-06 | G3a | Độ bền ban đầu | chu kỳ hoạt động, độ lỏng khớp, rạn nứt, nhiệt | Kết thúc chu kỳ kiểm định dự kiến không hư hỏng (số chu kỳ sẽ chốt sau risk review) |
| MX-07 | G3b | Lực khí động/mô-men | `F_x`, `F_z`, `M_yaw` nếu đo được; zero/offset; sai số; f | Dữ liệu tin cậy, baseline và nhiễu được công bố; xem tăng/giảm lực theo flap, không suy diễn sức bay |
| MX-08 | G3b | Thẩm quyền lái | chênh lệch lực/mô-men khi `steering = -s/0/+s` | Xác định đúng dấu phản hồi, biên độ và tính lặp; nếu không đáp ứng phải REWORK |
| MX-09 | G3b | Radio/failsafe/nguồn trong rig | tuổi frame, link flag, timeout, pin sag, output state | Không servo chạy vượt giới hạn; các tình huống mất sóng/nguồn xử lý theo chính sách bench được duyệt |
| MX-10 | G4 | Bay tự do bằng tay cầm RC | takeoff, đường bay, thao tác lái, hạ cánh, video, log | Chỉ sau phê duyệt G4; số lần, thời gian, an toàn và ngưỡng do owner phê duyệt dựa trên G3 |

## 3. Thiết kế rig (mức yêu cầu, chưa hướng dẫn chế tạo cuối)

```text
  Safety shield / clear space
             |
         Winged frame --- calibrated rigid mount
             |
    1-axis or multi-axis force sensor
             |
    stable bench structure, anti-vibration

  Independent measurement:
  - power: voltage/current logger at servo rail and MCU
  - movement: high-frame-rate video, markers at L/R wing tip
  - forces: raw sample + tare baseline + calibrated direction
  - logs: trusted controller time + commanded/actual sample when available
```

**Cảnh báo đo:** phản lực rung, cộng hưởng rig, độ cứng gá và thay đổi chuyển động cánh do bị cố định đều có thể làm sai khác so với bay tự do. `F_z` đo trên rig không phải mô hình aerodynamic đầy đủ. Phải ghi hướng trục, đơn vị, tare, tần số lấy mẫu, bộ lọc (nếu có), nhiễu nền và độ lệch khi chạy không cánh. Ví dụ các nghiên cứu sử dụng load cell và theo dõi lực tức thời; không sao chép máy đo hay suy ra lực từ động tác cánh: https://www.mdpi.com/2313-7673/11/3/207 ; https://www.sciencedirect.com/science/article/pii/S0888327015002022

## 4. Ma trận biến độc lập tối thiểu

Khi có cấu hình cơ cấu và giới hạn đã được duyệt, khảo sát từng biến một; mọi mức giá trị là **TBD cho đến khi servo và cánh thật được đo**.

| Sweep | Giữ nguyên | Thay đổi | Đầu ra chính |
|---|---|---|---|
| A — nhịp vỗ | cánh, pin/điện áp, biên độ | `f_cmd` ở mức thấp/vừa/cao an toàn | `f_actual`, I, nhiệt, lực |
| B — biên độ | tần số, cánh, cấp nguồn | biên độ lệnh trong soft limit | góc thực, lực, I |
| C — vật liệu cánh | actuator, hành trình, rig | 2 thiết kế màng/gân, mass ghi rõ | lực/khối lượng, tải và rung |
| D — steering | flap và nguồn | lệch trái/giữa/phải | moment/force differential |
| E — battery sag | điều kiện G2/G3 an toàn được duyệt | nguồn giả lập mức cao/trung bình/thấp | timing, brownout, fault behavior |

Không kéo dài chạy khi nhiệt/dòng bất thường hoặc có dấu hiệu stall; số giây/chuyến đo/tần số sẽ chốt từ đặc tính phần cứng và thử tải thấp ban đầu, không bịa trước.

## 5. Mẫu báo cáo số đo (SA/Tester điền sau thử)

```text
Experiment ID: MX-__
Status: NOT RUN / PASS / FAIL / BLOCKED
Airframe rev + wing rev + servo model + firmware commit:
RC TX/RX + battery + regulator + test rig:
Date/site/operator/reviewer:
Calibrations + instrument uncertainty:
Setpoint: flap_hz=__ amplitude=__ steering=__
Measured: f_actual=__Hz; amp_L/R=__deg; I_peak=__A;
          V_min=__V; T_max=__C; F_x=__N; F_z=__N; M_yaw=__Nm
Mass and CG: __g; (x,y,z)=__mm
Video path / raw CSV / graph path:
Expected / Actual / Deviation:
Hazard, defect, corrective action:
SA decision: CONTINUE / REWORK / SWITCH / STOP
```

## 6. G3 → G4: No-Go nếu chưa đáp ứng

- Chưa có cân mass/CG, sơ đồ cấp nguồn và thông số servo đã được xác minh.
- Servo kẹt, rung lớn, nguồn reset hoặc xung đột RC gây điều khiển không dự đoán được.
- Chưa có bằng chứng đo lực/mô-men và đánh giá khả năng điều khiển hướng.
- Chưa xác định khu vực bay an toàn, người điều khiển, khoảng cách an toàn, phương án thu hồi và yêu cầu pháp lý tại địa điểm thử.
- Chưa thử tình huống mất sóng, pin yếu hoặc chưa chốt ứng xử an toàn **khi đang bay**.
- Chưa có phê duyệt G4 riêng của chủ dự án sau xem xét toàn bộ bằng chứng G0–G3.

## 7. Quy tắc thực hiện

File này là tài liệu **thiết kế thử nghiệm**, chưa phải task Developer, chưa yêu cầu mua linh kiện hoặc cấp điện. SA sửa Design; khi thiết kế đã chốt mới phát hành task tương ứng qua `Task/`. Người thử có thể kiến nghị thay đổi nhưng không được tự điều chỉnh safety gate không qua review.
