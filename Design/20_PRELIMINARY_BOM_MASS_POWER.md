# BionicButterfly — BOM sơ bộ, ngân sách khối lượng và nguồn V1

- **Document ID:** BB-BOM-020 · **Version:** 0.2 · **Date:** 2026-11-12
- **Owner:** Solution Architect · **Status:** PROPOSED / ESTIMATED — **NOT FOR PROCUREMENT**
- **Refs:** `03_HARDWARE_DESIGN.md`, `19_MECHANICAL_CONCEPT_DESIGN.md`, `18_MECHANICAL_EXPERIMENT_PLAN.md`.
- **Cơ sở:** phân bổ concept cho M1 hai servo, V1 bay thật bằng RC; mọi khối lượng chưa cân ghi `ESTIMATE` và **không được ghi `TESTED`**.

## 1. Ví dụ linh kiện tham khảo (KHÔNG chốt mua)

| Cụm | Qty | Ứng viên ban đầu / yêu cầu tối thiểu | Bằng chứng / ràng buộc |
|---|---:|---|---|
| MCU | 1 | Seeed XIAO ESP32-C3 hoặc board nhỏ tương đương | Board 21 x 17.8 mm, UART/PWM; chân BAT chỉ dành cho pin 1S 3,7 V, VIN 5 V cần mạch bảo vệ theo tài liệu Seeed; **không đưa 2S trực tiếp vào BAT/VIN**. [Seeed](https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/) |
| Servo trái/phải | 2 | Servo digital hạng 4–6 g, không xác nhận model đến khi có số đo torque/speed/dòng/refresh under load | Ví dụ EMAX ES9051 hãng công bố 4,3 g mỗi chiếc, **chỉ tham khảo khối lượng**, không chứng minh đủ lực, tốc độ, duty-cycle để vỗ cánh. [EMAX](https://shop.emax-usa.com/collections/servos/products/emx-sv-0272-es9051) |
| RC receiver | 1 | Nano ExpressLRS 2.4 GHz / UART CRSF, anten an toàn cơ khí | Ví dụ RadioMaster RP1 V2 2,2 g cả anten, 5 V, CRSF theo nhà sản xuất; cần kiểm tra tương thích và áp logic UART thực. [RadioMaster](https://radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver) |
| Tay cầm RC (ngoài máy bay) | 1 | Transmitter có **ELRS 2.4 GHz**, công tắc arm riêng, hỗ trợ kiểm thử failsafe | Chỉ ví dụ dòng RadioMaster Pocket **bản ELRS**; bản CC2500 không dùng được với RX ELRS trực tiếp. Loại TX chưa duyệt. |
| Pin bay | 1 | LiPo 2S dung lượng nhỏ như 220 mAh là tham khảo từ upstream; chọn sau phép thử tải | `7.4 V` danh định; `8.4 V` lúc đầy. Năng lượng danh định 220 mAh ~ `1.63 Wh`, **không phải thời gian bay cam kết**. Cần nguồn sạc cân bằng 2S chuyên dụng. |
| Nguồn | 1 bộ | BEC/buck có điện áp cho servo và logic đúng datasheet, chịu **dòng đỉnh đo được** | Không lấy 5 V từ MCU để nuôi servo; 2S trực tiếp chỉ nếu servo được rated HV phù hợp. BEC cũng phải có mass/cooling xác minh. |
| Cánh | 2 tổ hợp | Màng polyester/Mylar mỏng và gân carbon/nhẹ, hai nửa đối xứng | Chưa chọn độ dày/hình dạng; cân từng bên và đo độ cứng, xoắn dưới tải. |
| Frame/linkage | 1 bộ | Khung, bản lề, horn, pushrod, fasteners, foam/nhựa in nhẹ | Kích thước và clearance sẽ ở CAD sau, không copy STL thương mại khi chưa có quyền. |
| LED C1 | tùy chọn | LED nhẹ + mạch driver + dây mềm nhẹ | **Không dùng cho C0**; gắn gần gốc nếu có thể, không đặt dây đi qua khớp kẹt, đo lại nguồn và mô-men quán tính. |

## 2. Phân bổ khối lượng thiết kế C0 (giả định để lập phương án)

Mục tiêu **dùng để phân bổ**, chưa phải điều kiện cất cánh đã chứng minh: `m_C0_budget = 70.0 g`; nên giảm càng nhiều càng tốt, không tối ưu phần mềm để bù cơ cấu thừa cân.

| Hạng mục | Phân bổ C0 (g) | Trạng thái | Cần xác minh |
|---|---:|---|---|
| 2 tổ hợp cánh, gân và màng | 10.0 | ESTIMATE | cân trái/phải độc lập |
| 2 servo, gồm phần servo | 10.0 | ESTIMATE | cân cả dây cáp thực tế |
| Khung thân | 10.0 | ESTIMATE | CAD và cân mẫu |
| Horn, linkage và bản lề | 5.0 | ESTIMATE | mẫu thực, chiều dài tay đòn |
| MCU và anten đi kèm nếu có | 4.0 | ESTIMATE | cân board + antenna |
| RC receiver và antenna | 2.5 | ESTIMATE | cân RX thực |
| Pin bay | 16.0 | ESTIMATE | cân viên pin đầy đủ dây/jack |
| BEC, chia nguồn và bảo vệ | 5.0 | ESTIMATE | cân mạch + tụ + dây chính |
| Dây tín hiệu, jack | 3.0 | ESTIMATE | cân dây đã cắt |
| Keo, đai, vít | 3.0 | ESTIMATE | cân sau lắp |
| **Dự phòng phân bổ** | **1.5** | ESTIMATE | biên thấp, cần cảnh báo |
| **Tổng** | **70.0 g** | **NOT MEASURED** | đo hoàn thiện C0 |

**Lưu ý:** chỉ 1,5 g dự phòng là ít; nếu thực tế vượt ngân sách không được bù bằng giảm bộ phận an toàn, nguồn hay độ bền. Phải thiết kế lại/chọn lại linh kiện trước khi tiếp tục. Không đưa transmitter, bộ sạc, test rig vào `m_total` vì chúng không bay; nhưng chúng vẫn thuộc chi phí dự án.

Tại 70 g: `W = 0.070 × 9.80665 ≈ 0.686 N` — **đây là trọng lực**, không phải lực nâng đã đo, không khẳng định có thể bay. Dữ liệu rig phải được đánh giá cùng lực/mô-men theo thời gian, tốc độ bay, hành trình và ổn định.

### C1 — Tính thêm LED sau C0

| Mục bổ sung so với C0 | Phân bổ gia tăng (g, chỉ ước tính) |
|---|---:|
| LED + dây trên cánh/thân | 6.0 |
| Driver/bảo vệ nguồn LED | 2.0 |
| Gia cường/khớp để tránh đứt dây | 2.0 |
| Dự phòng sai lệch sau tích hợp | 2.0 |
| **Gia tăng C1** | **12.0** |
| **C1 projected** | **82.0 g** |

82 g tương đương `W≈0.804 N`. Không đặt mục tiêu C1 “bay như C0” dựa duy nhất trên cộng khối lượng; **LED ở mép cánh làm tăng quán tính**, có thể làm servo hụt hành trình, tiêu thụ điện cao và suy giảm điều khiển. Phải kiểm tra MX-01…MX-09 lại cho revision C1 và có rủi ro bổ sung do điện/EMI.

## 3. Ngân sách điện ban đầu (chưa có dòng đo)

```text
               [2S LiPo] -- fuse / connector / protection --+-- [servo BEC rail] -- servo L
                                                           |                    +-- servo R
                                                           +-- [logic BEC] ----- MCU 5V input (per Seeed rules)
                                                                              +--- RX 5V rail (verify RX)
                                                           +-- [LED supply] ----- C1 ONLY

                      common GND, correct voltage level & power source are mandatory;
                      rail topology may consolidate after current/thermal review.
```

- Năng lượng danh định (ví dụ 2S 220 mAh): `E_nom = 7.4 V × 0.22 Ah = 1.628 Wh`. Không suy ra 5 phút bay chỉ bằng E vì còn mức xả, sag, hiệu suất BEC, tải theo nhịp vỗ, reserve và nhiệt.
- `I_peak_servo`, `I_avg_servo`, dòng RX/MCU/LED, `V_min_at_load`, nhiệt BEC và brownout MCU là **TBD**. Không tính BEC chỉ bằng dòng không tải; đo dòng đồng thời hai servo dưới cánh thật.
- XIAO ESP32-C3 có đường sạc 1S theo nhà sản xuất; không dùng nó như bộ sạc cho LiPo 2S. Chọn bộ sạc cân bằng được nhà sản xuất pin khuyến nghị, sạc ngoài máy bay tại vị trí an toàn.
- Nếu C0 dùng **các BEC tách biệt**, kiểm tra mass/hiệu suất. Nếu gộp 1 BEC phải đánh giá nhiễu điện, reset, quá dòng và tách logic bằng lọc/cấp nguồn phù hợp.

## 4. Chi phí: chưa chốt ngân sách mua

Mức giá dưới đây là **khoảng lập kế hoạch USD giả định**, không phải báo giá ở Việt Nam, chưa gồm vận chuyển/thuế, cũng không bảo đảm là model cuối cùng tương thích. Nguồn tham khảo ví dụ: Seeed XIAO, EMAX ES9051 và một bảng BOM cộng đồng ESP-FLUTTER (không phải kết quả thử của chúng ta).

| Nhóm chi phí | Khoảng lập kế hoạch USD | Ghi chú |
|---|---:|---|
| 2 servo | $10–30 | phụ thuộc torque, speed, tuổi thọ, dây/horn |
| MCU | $5–12 | board/antenna/shipping |
| Receiver RC | $12–30 | ELRS CRSF phù hợp |
| Pin + BEC + phân phối nguồn | $15–40 | cần tính khả năng xả và bảo vệ |
| Màng, gân carbon, khung, linkage | $15–45 | tùy có máy in 3D/máy cắt |
| Dây, jack, vật tư phụ | $5–15 | không cắt giảm phần kết nối an toàn |
| **Tổng cụm C0 trên máy bay** | **$62–172** | dự trù trước mua, không gồm chi phí thử sai |
| Bộ sạc cân bằng 2S | $15–35 | dụng cụ mặt đất bắt buộc |
| Tay cầm RC tương thích ELRS | $60–110+ | dụng cụ mặt đất, cần xác minh phiên bản ELRS |
| C1 LED/driver/vật tư | +$5–25 | phải chứng minh lại bay và nguồn |
| Rig đo lực, đồng hồ, cân, dự phòng | TBD | có thể là khoản chi lớn; không bỏ qua |

Không có mục nào được duyệt mua qua tài liệu này. Nếu bạn đã có tay cầm/pin/servo/máy in 3D, cập nhật BOM để tránh mua trùng. **Cần chốt ngân sách và kiểm chứng datasheet trước khi đề xuất shopping list.**

## 5. Bảng khảo sát khi bắt đầu làm mẫu

| Field | Phải ghi |
|---|---|
| Component code + vendor + datasheet revision | link/file/hình chụp model |
| `mass_g` (gồm dây nếu dùng) | số đo + độ phân giải cân |
| Đơn giá/thời điểm/nguồn | VNĐ hoặc USD, shipping, số lượng |
| Vmin/Vmax/logic level/servo pulse Hz | datasheet + kế hoạch kiểm thử |
| Peak current, average current, thermal | số đo riêng & đồng thời trong tải thật |
| Delivery constraints and licenses | người chịu trách nhiệm, provenance |
| Airframe revision C0/C1 | cấu hình đúng với video/test log |

## 6. References

- https://wiki.seeedstudio.com/XIAO_ESP32C3_Getting_Started/
- https://shop.emax-usa.com/collections/servos/products/emx-sv-0272-es9051
- https://radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver
- https://www.expresslrs.org/quick-start/receivers/wiring-up/
- https://github.com/maximagination1/ESP-FLUTTER (PolyForm Noncommercial; research only)
- https://github.com/builtbysai/esp-flutter-butterfly (community build log, unverified for our project)

**Safety / status:** Chưa có hardware và chưa đo đạc, do đó **no-go cho bay thử**, chưa phát hành Task AI Code.

## 7. Electrical interface clarification (v0.2 — PROPOSED)

- `22_ELECTRICAL_POWER_ARCHITECTURE.md` defines candidate 2S power branching and **safe XIAO external 5V input/USB isolation**, which the high-level BOM figure above does not fully show. **Never connect 2S directly to XIAO BAT/5V or normal 5V servos.**
- `23_PINOUT_AND_SIGNAL_CONTRACT.md` proposes receiver UART, dual PWM and scaled pack sensing. An isolated voltage meter/divider must not be interpreted as a validated battery state-of-charge estimate.
- Do not interpret the illustrative 2S 220mAh battery or the hypothetical 10W load as an approved procurement choice. Run current/mass/temperature tests and re-evaluate 2S-versus-1S on evidence.

*Changelog v0.2: cross-reference electrical architecture; no BOM price or mass changes.*
