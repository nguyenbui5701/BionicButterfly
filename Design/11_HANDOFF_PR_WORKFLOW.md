# BionicButterfly — SA ↔ Developer Handoff & PR Review Workflow

- **Document ID:** BB-WF-001
- **Version:** 0.1
- **Date:** 2026-11-12
- **Owner:** Solution Architect
- **Status:** PROPOSED — chờ chủ dự án phê duyệt

## 1. Vai trò và quyết định cuối cùng

| Công việc | Chủ dự án (Owner) | Solution Architect | Developer / AI Code |
|---|---|---|---|
| Định nghĩa mục tiêu, chi phí, mức chấp nhận rủi ro | **Quyết định** | Tư vấn | Góp ý |
| Phân tích video/source tham khảo | Cung cấp input | **Chịu trách nhiệm** | Được đọc |
| Tạo/sửa Design và rules | **Phê duyệt** | **Soạn/commit** | Đề nghị thay đổi |
| Tạo Task từ Design đã duyệt | Ưu tiên | **Chịu trách nhiệm** | Thực hiện |
| Code và kiểm thử Source | Theo dõi | Review | **Chịu trách nhiệm** |
| Review PR và nhận xét | Quyết định merge | **Review + comment** | Trả lời/sửa |
| Dọn ReviewPR + Task sau merge | Xác nhận hoàn tất | **Thực hiện** | Không tự xóa |

## 2. State machine

```text
VIDEO / SOURCE RESEARCH
         ↓
DESIGN DRAFT → DESIGN PROPOSED
         ↓  [Owner approves]
    DESIGN APPROVED
         ↓  [SA issues task]
      TASK OPEN
         ↓  [Dev codes / tests / opens PR]
       PR OPEN
         ↓
      SA REVIEW
      ├── BLOCKER/MAJOR ──→ CHANGES REQUESTED
      │                           ↓ [Dev fixes and updates PR]
      │                       SA RE-REVIEW
      └── NO BLOCKER ─────→ READY FOR OWNER DECISION
                                  ↓ [Owner accepts / merges]
                            TASK COMPLETE / CLEANUP
```

**Không bỏ qua các cổng phê duyệt**; `PROPOSED` không tương đương `APPROVED`.

## 3. Task template (chỉ dùng sau design approval)

Tên file: `Task/TASK-001_<short-title>.md`.

```markdown
# TASK-001 — <Name>
Status: OPEN
Owner: Developer / AI Coding Agent
Approved design: Design/<file>.md @ <commit SHA / revision>
Purpose: ...
Required reading: [Design/07_AI_CODING_RULES.md, Design/..., Source/...]
Allowed files: Source/<...>
Out of scope: ...
Acceptance criteria:
- [ ] ... (measurable)
Test plan / commands: ...
Safety & license checks: ...
PR link: ...
Review findings: ...
```

## 4. Recommended Git workflow

SA design update (ở root của repository chính):

```powershell
git status
git add Design/01_REFERENCE_AUDIT.md Design/07_AI_CODING_RULES.md Design/10_SA_OPERATING_RULES.md Design/11_HANDOFF_PR_WORKFLOW.md
git commit -m "docs(design): add SA and developer role policies"
git push origin main
```

Khi team đã áp dụng protected branch, SA chuyển sang nhánh `design/...` và mở PR cho thay đổi Design thay vì push thẳng `main`. Không push nếu không có quyền; lúc đó gửi patch/file cho Owner.

Developer thực hiện task:

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/TASK-001-example
# ... sửa code Source và chạy test ...
git add Source/
git commit -m "feat(TASK-001): implement approved behavior"
git push -u origin feature/TASK-001-example
# Tạo Pull Request trên GitHub
```

SA review PR #123 bằng **Git worktree** cô lập từ root project:

```powershell
git fetch origin "pull/123/head:refs/remotes/origin/pr/123"
git worktree add --detach ReviewPR/pr-123 origin/pr/123
# Review file/test trong ReviewPR/pr-123, KHÔNG sửa Source/ của dev
```

Sau khi chủ dự án xác nhận PR đã chấp nhận/merge và **không còn BLOCKER/MAJOR**:

```powershell
git worktree remove ReviewPR/pr-123
git worktree prune
# Sau đó SA xóa đúng file Task/TASK-XXX... liên quan,
# commit việc dọn Task, rồi push lên repository.
```

Nếu PR còn BLOCKER/MAJOR: **không** chạy lệnh cleanup; giữ checkout và bổ sung mục sửa vào task.

## 5. PR review comment template

```markdown
Review: REQUEST_CHANGES | COMMENT | APPROVE
Task: TASK-XXX
Design reference: <file + revision>

Finding BB-PR-001 — [BLOCKER | MAJOR | MINOR | NOTE]
Location: Source/path/file.cpp:<line>
Evidence: <behavior / test / diff>
Impact: <safety / wrong behavior / regression>
Requested fix: ...
How to verify: ...

Summary: <what passed, what did not>
```

Nếu không có quyền `APPROVE` hay `REQUEST_CHANGES` với PR, gửi comment và nêu rõ giới hạn quyền. Chỉ báo “đã post comment” sau khi GitHub xác nhận thành công.

## 6. Security / housekeeping

- `ReviewPR/` phải nằm trong `.gitignore`; không commit checkout hoặc `.git` nội bộ của worktree.
- Bảo vệ `main` bằng PR reviews/branch protection khi bắt đầu làm việc nhóm; quyền push chỉ cấp người cần thiết.
- Không đưa secrets/firmware độc quyền/bản vẽ chưa được cấp phép vào repo Public.
- Chỉ xóa đúng checkout và task đã xác nhận hoàn tất; không dọn toàn bộ thư mục chung.

## 7. Changelog

- 2026-11-12: Định nghĩa RACI, state gates, template task, cách review PR cô lập và cleanup.
