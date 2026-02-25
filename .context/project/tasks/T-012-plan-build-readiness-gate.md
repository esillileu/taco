---
id: T-012
type: task
title: T-012-plan-build-readiness-gate
status: done
plan_ref: PLAN-MAIN
priority: p0
estimate: m
scope:
  in:
  - src/taco/tools.py
  - src/taco/pack.py
  - src/taco/cli.py
  - src/taco/main.py
  - tests/test_tools.py
  - tests/test_cli_main.py
  - tests/test_integration_mcp_cli.py
  out:
  - "\uC2E0\uADDC MCP transport \uAD6C\uD604"
  - "\uBB38\uC11C \uAD6C\uC870 \uB300\uADDC\uBAA8 \uAC1C\uD3B8"
references:
  modules:
  - MOD-TOOLS-DISPATCH
  - MOD-PACK
  - MOD-CLI-MAPPER
  - MOD-MAIN
  flows:
  - FLOW-MODE-TRANSITION
  - FLOW-TOOL-DISPATCH
  - FLOW-TASK-PACK
  schemas:
  - SCH-TASK-NODE
  - SCH-PACK-RESULT
  - SCH-TOOL-ENVELOPE
  - SCH-TOOL-ERROR
  governance:
  - GOV-CODE-PRINCIPLES
deliverables:
- "plan->build readiness \uD310\uC815 \uD568\uC218\uC640 \uC5D0\uB7EC \uCF54\uB4DC"
- "task.pack \uD638\uCD9C \uC804 readiness \uAC80\uC99D \uACBD\uB85C"
- "readiness \uC2E4\uD328/\uC131\uACF5 \uD14C\uC2A4\uD2B8 \uCF00\uC774\uC2A4"
verification:
- uv run --extra dev pytest -q
- uv run --extra dev ruff check .
- uv run --extra dev mypy .
links:
- PLAN-MAIN
- FLOW-MODE-TRANSITION
- ARCH-INDEX
---

# Task: T-012-plan-build-readiness-gate

## Intent
<!-- taco:pack=task.core -->

- Build 모드 진입 전에 태스크 실행 가능 상태를 기계적으로 검증해, 준비되지 않은 태스크 실행을 막는다.

## Goal
<!-- taco:pack=task.core -->

- `plan -> build` 전환 조건(목표/범위/참조/검증)의 최소 충족 여부를 코드로 강제한다.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- readiness 판정 규칙을 정의한다:
  - 필수 헤딩/필드 존재
  - `references.modules/flows/schemas` 비어있지 않음
  - `Verification Approach`가 실행 가능한 검증 명령 또는 기준 포함
- `task.pack` 진입 전에 readiness 검사 훅을 추가한다.
- readiness 실패 시 표준 에러 코드와 details를 반환한다.
- dry-run/apply 의미와 독립적으로 readiness는 동일하게 적용한다.

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, FLOW-MODE-TRANSITION

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- 태스크 문서 파싱 결과를 입력으로 받는 `readiness` 판정 유틸을 추가한다.
- `task.pack` 핸들러에서 판정 실패 시 조기 종료한다.
- 실패 details에는 누락 항목 목록을 명시한다.
- CLI/MCP 경로 모두 동일 에러 envelope를 유지한다.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- 성공 케이스:
  - 준비된 태스크는 기존처럼 `task.pack` 성공
- 실패 케이스:
  - 참조 누락
  - 검증 기준 누락
  - scope 불완전
- 회귀 검증:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

- Added task.pack readiness gate: validates task front matter shape, required task headings, non-empty module/flow/schema references, and verification criteria before pack assembly
- readiness gate implemented and merged
## Verification Result

- Pending (do not fill until the task is completed)
- Verified with ruff/mypy/pytest/doc-validation; added regression tests for task_not_ready failures and updated CLI/integration fixtures to front matter id-based references
- ruff mypy pytest validate_docs passed
