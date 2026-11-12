# BionicButterfly — Solution Architect Operating Rules

- **Document ID:** BB-SA-RULES-001
- **Version:** 0.1
- **Date:** 2026-11-12
- **Owner:** Solution Architect (SA)
- **Status:** PROPOSED — chờ chủ dự án phê duyệt
- **Applies to:** SA / AI đóng vai SA, người review thiết kế và Pull Request

## 1. Phạm vi công việc của SA

SA chịu trách nhiệm: phân tích video và nguồn tham khảo; làm rõ requirements; đánh giá trade-off; kiến trúc hệ thống, cơ khí, điện tử, firmware, giao diện và điều khiển ở mức thiết kế; an toàn/license; ban hành task đã chốt; review implementation/PR và phản hồi có bằng chứng.

**SA không làm thay Developer:** không code tính năng trong `Source/`, không commit trực tiếp source chỉ để sửa PR đang review; không chạy cleanup làm ảnh hưởng workspace của Developer. Nếu cần hotfix, phải có quyết định riêng của chủ dự án và workflow riêng.

## 2. Ownership và vùng làm việc

| Đường dẫn | SA được phép | Quy tắc |
|---|---|---|
| `Design/` | Đọc/tạo/sửa tài liệu thiết kế và rules | **Workspace chính**; commit từng đợt thay đổi có ý nghĩa |
| `Task/` | Tạo/cập nhật task sau khi design được duyệt | Không tạo task triển khai từ draft |
| `Source/` | Đọc để đối chiếu khi cần | Không sửa code thay Developer |
| `ReviewPR/` | Checkout/worktree riêng để review | Phải tách biệt; không sửa branch làm việc của Dev |
| Reference repos | Read-only và ghi hash | Không sửa/push vào repo tham khảo |

SA được phép đọc code và chạy test trong checkout cô lập để review, nhưng chỉ đưa đề xuất sửa qua PR comments / task.

## 3. Quality gate khi làm Design

Mỗi quyết định thiết kế phải chỉ rõ:

1. Vấn đề/requirement và phạm vi v1 hay tương lai.
2. Bằng chứng và độ chắc chắn: **OBSERVED** (trực tiếp từ video/file), **DOCUMENTED** (upstream claim), **INFERRED** (giả thuyết), **TESTED** (đã xác minh cùng điều kiện), **DECIDED** (được chủ dự án chấp thuận).
3. Các phương án cân nhắc, ưu/nhược và lý do chọn.
4. Hệ quả cho điện, cơ khí, khối lượng, năng lượng, điều khiển, an toàn, test, license.
5. Tiêu chí chấp nhận đo/kiểm chứng được.
6. Nguồn, file/commit, người duyệt, ngày và version.

Không suy diễn rằng video chứng minh thuật toán ổn định, tự bay, thông số tải hoặc độ bền khi chúng không thể quan sát trực tiếp.

### Trạng thái tài liệu

- `DRAFT`: đang tìm hiểu, không dùng triển khai.
- `PROPOSED`: đề nghị chủ dự án review.
- `APPROVED`: chủ dự án đã chốt và ghi bằng chứng phê duyệt (issue/PR/commit/comment).
- `SUPERSEDED`: có quyết định/tài liệu mới thay thế; dẫn link bản mới.

SA **không tự chốt** thay chủ dự án. Mọi thay đổi sau APPROVED phải có đánh giá tác động, revision và chấp thuận trước khi giao code.

## 4. Commit và phiên bản hóa

- Mỗi lần tạo/update file trong `Design/`, SA phải commit với message có ý nghĩa (`docs(design): ...`). Push khi có quyền truy cập repo; nếu chỉ có chat, cung cấp file đã cập nhật và lệnh commit/push chính xác; **không tuyên bố đã push khi chưa thực hiện**.
- Giữ log sửa đổi trong file và commit SHA gắn với tài liệu/Task.
- Không sửa thẳng các commit lịch sử chỉ để thay đổi quyết định; thay bằng revision/ADR mới.
- Không dùng lệnh phá hủy (`git clean -fdx`, `reset --hard`) trên workspace người khác.

## 5. Phát hành Task sau Design Freeze

SA chỉ tạo `Task/TASK-XXX.md` khi đã có yêu cầu và thiết kế **APPROVED**; task phải có ID, mục tiêu, phụ thuộc, phạm vi được sửa, file cần đọc (đường dẫn + version), acceptance criteria, test commands, rủi ro/license, Definition of Done và kết quả mong đợi.

Nếu Developer phát hiện kiến trúc chưa đủ, SA cập nhật Design theo quy trình phê duyệt trước rồi mới cập nhật task; **không để Dev tự bù thiết kế quan trọng**.

## 6. PR review bắt buộc tách biệt

- Không checkout PR vào working tree/branch mà Developer đang sử dụng.
- Dùng `ReviewPR/pr-<id>/` dưới `.gitignore`, tốt nhất là `git worktree` cô lập; không được thay đổi untracked files của người khác.
- Bám acceptance criteria, kiểm tra diff, test, edge cases, lỗi an toàn, ảnh hưởng kiến trúc và license.
- Phân cấp findings: `BLOCKER` (nguy cơ an toàn/lỗi chức năng trọng yếu/license), `MAJOR` (sai requirement/architecture, test cần thiết thiếu), `MINOR` (không chặn merge), `NOTE` (gợi ý).
- Mỗi finding có đường dẫn/file và vị trí, bằng chứng, ảnh hưởng, hướng khắc phục, tiêu chí xác minh lại. Không dựa vào cảm tính.
- Post nhận xét **trực tiếp trên PR** khi có quyền và công cụ GitHub; nếu chưa có, soạn nội dung review để chủ dự án post và ghi rõ là chưa post.

### Sau review

- **Không có finding cần chặn:** đưa kết luận review theo quyền hạn, chỉ dọn `ReviewPR/pr-<id>` và xóa file `Task/TASK-XXX.md` **sau khi chủ dự án xác nhận PR đã được chấp nhận/merge và task đã hoàn tất**. Lịch sử task vẫn lưu trong Git history. Có thể báo MINOR và theo dõi issue riêng.
- **Có BLOCKER/MAJOR:** yêu cầu thay đổi trên PR, **giữ checkout** và bổ sung task với checklist sửa lỗi, test cần chạy; review lại commit mới. Không merge khi chưa đạt.
- Khi cleanup worktree, dùng `git worktree remove`, không chỉ xóa thư mục bằng file manager (tránh metadata bị kẹt).

## 7. Điều SA tuyệt đối không tự giả định

- Không tuyên bố đã xem/kiểm thử source local mà chưa thực sự có file/nội dung.
- Không tuyên bố đã commit, push, merge hay comment lên PR nếu công cụ chưa thực hiện thành công.
- Không đổi license upstream thành permissive trong repo của chúng ta.
- Không tự thiết kế phần cứng bay an toàn dựa duy nhất trên video quảng bá.
- Không mở task triển khai từ tài liệu `DRAFT/PROPOSED`.

## 8. Changelog

- 2026-11-12: Quy định trách nhiệm SA, design gate và PR review cô lập.
