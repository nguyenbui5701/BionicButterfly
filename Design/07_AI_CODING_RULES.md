# BionicButterfly — Developer / AI Coding Rules

- **Document ID:** BB-DEV-RULES-001
- **Version:** 0.1
- **Date:** 2026-11-12
- **Owner:** Solution Architect (SA)
- **Status:** PROPOSED — chờ chủ dự án phê duyệt
- **Applies to:** Developer, AI Coding Agent, contributor trong repository BionicButterfly

## 1. Mục tiêu và nguồn sự thật

Developer **triển khai và kiểm thử** thiết kế đã duyệt; không có quyền tự thay đổi phạm vi, tiêu chí nghiệm thu hoặc kiến trúc đã chốt.

Thứ tự ưu tiên khi thực thi: (1) chỉ đạo mới nhất của chủ dự án; (2) Design tài liệu có trạng thái **APPROVED**; (3) Task được SA phát hành; (4) code và test hiện hành. Nếu mâu thuẫn, **dừng thay đổi liên quan và báo SA**, không tự chọn cách hiểu thuận tiện. Draft/Proposed là tài liệu nghiên cứu, **không** được coi là lệnh triển khai.

## 2. Quyền hạn và ranh giới thư mục

| Đường dẫn | Developer được làm | Không được làm |
|---|---|---|
| `Design/` | Đọc; gửi câu hỏi, issue, đề xuất thay đổi | Tự sửa/ghi đè, tự chuyển `DRAFT` thành `APPROVED` |
| `Task/` | Đọc và cập nhật minh chứng tiến độ khi task cho phép | Tự tạo/đóng/xóa task hoặc sửa acceptance criteria |
| `Source/` | Thực hiện code, test, refactor trong phạm vi task | Thay đổi ngoài scope hoặc import firmware tham khảo không được phê duyệt |
| `ReviewPR/` | Không sử dụng | Checkout, sửa hoặc xóa checkout của SA |
| Repo tham khảo ở ngoài project | Đọc phiên bản pin cố định | Sửa, commit, push hay coi code là source chính |

**Ngoại lệ:** Chỉ được làm khác nếu chủ dự án/SA phê duyệt và ghi rõ vào task hoặc quyết định thiết kế.

## 3. Điều kiện bắt đầu một task

Trước khi code phải có: (a) Task ID và người giao; (b) link/đường dẫn Design `APPROVED`; (c) file/phân hệ cho phép sửa; (d) acceptance criteria; (e) tiêu chuẩn test; (f) ràng buộc an toàn/license. Nếu thiếu hoặc trái nhau, báo `BLOCKED — DESIGN CLARIFICATION`.

Developer phải đọc ít nhất:

1. `Design/07_AI_CODING_RULES.md` (file này).
2. `Design/10_SA_OPERATING_RULES.md` (để biết ranh giới SA).
3. `Design/11_HANDOFF_PR_WORKFLOW.md` (quy trình bàn giao/review).
4. Các mục Design được task chỉ định (`requirements`, `architecture`, `controls`, `hardware`, `tests`, v.v.).
5. File `Task/TASK-XXX.md` được giao và phần code liên quan.

## 4. Quy tắc triển khai

1. **Một task = một nhánh** dạng `feature/TASK-XXX-short-name` hoặc `fix/TASK-XXX-short-name`; không commit trực tiếp vào `main` nếu đang dùng PR workflow.
2. Thay đổi nhỏ, có lý do, có commit rõ ràng; không `push --force`, `reset --hard`, xóa lịch sử hoặc sửa cấu hình bảo vệ nhánh khi chưa được phép.
3. Giữ module tách biệt: đọc input, kiểm tra/arming, giám sát an toàn, sinh quỹ đạo vỗ cánh, điều khiển actuator, LED/UI. Không trộn logic an toàn với hiệu ứng giao diện.
4. Mọi thông số có đơn vị/miền hợp lệ (Hz, độ, microsecond, Volt, timeout ms); không đặt hằng số điều khiển thiếu chú thích hoặc bỏ qua giới hạn servo.
5. Mặc định hệ thống ở **disarmed**; xác thực input và timeout khi mất liên lạc; trạng thái lỗi phải chuyển đến trạng thái đã được thiết kế xác định. Không tự tuyên bố chính sách failsafe an toàn khi chưa test.
6. Không dùng `hover` theo nghĩa auto-hold nếu chưa có thuật toán cảm biến/điều khiển và bằng chứng thử nghiệm.
7. Không sao chép code, mô hình 3D, ảnh hoặc linh kiện thiết kế từ repo tham khảo khi chưa rà giấy phép/quyền sử dụng. Giữ ghi nhận provenance và attribution khi phù hợp.
8. Không commit secrets, token, mật khẩu, private key hoặc thông tin nhạy cảm. Không đưa dữ liệu máy cá nhân vào logs công khai.
9. Không thay đổi pin map, thông số servo, bộ cấp nguồn hoặc quy trình nạp firmware ngoài thiết kế duyệt. Thử phần cứng sau khi có bench safety checklist.
10. Không tự xóa hoặc làm sạch file chưa commit của người khác.

## 5. Verification / Definition of Done

Task chỉ sẵn sàng review khi có:

- Danh sách file thay đổi và giải thích ngắn lý do thay đổi.
- Bảng đối chiếu từng acceptance criterion với test/bằng chứng.
- Build và unit/integration test có kết quả; nêu rõ test không thể chạy và nguyên nhân (không ghi `PASS` giả).
- Kiểm tra input boundary, timeout/arming/failsafe nếu task đụng firmware điều khiển.
- Báo cáo rủi ro, nợ kỹ thuật và những hành vi chưa được xác minh trên phần cứng.
- Pull Request liên kết Task ID, Design version/commit, hướng dẫn tái hiện và lệnh kiểm thử.

**Không được tự merge PR**, tự approve, hoặc xóa task sau khi nộp PR. SA/chủ dự án quyết định review và kết thúc.

## 6. Mẫu thông báo khi bị chặn

```text
Task: TASK-XXX
Status: BLOCKED — DESIGN CLARIFICATION
Design section / requirement: ...
Observed conflict / unknown: ...
Options and consequences: ...
Requested SA decision: ...
Code changed so far: ...
```

## 7. Changelog

- 2026-11-12: Tạo bộ quy tắc dành riêng cho Developer / AI Coding Agent.
