---
id: T-013
type: task
title: T-013-build-plan-fallback-state
status: done
plan_ref: PLAN-MAIN
priority: p0
estimate: m
scope:
  in:
  - src/taco/tools.py
  - src/taco/router.py
  - src/taco/main.py
  - tests/test_task_complete.py
  - tests/test_tools.py
  - tests/test_integration_mcp_cli.py
  out:
  - "\uC790\uB3D9 \uD0DC\uC2A4\uD06C \uBD84\uD574/\uC0DD\uC131 \uC5D4\uC9C4"
  - "\uC678\uBD80 \uC774\uC288 \uD2B8\uB798\uCEE4 \uC5F0\uB3D9"
references:
  modules:
  - MOD-TOOLS-DISPATCH
  - MOD-ROUTER
  - MOD-MAIN
  flows:
  - FLOW-MODE-TRANSITION
  - FLOW-TASK-RECORD
  schemas:
  - SCH-TASK-NODE
  - SCH-TOOL-ERROR
  - SCH-TOOL-ENVELOPE
  governance:
  - GOV-CODE-PRINCIPLES
deliverables:
- "build->plan fallback \uD45C\uC900 \uC0C1\uD0DC/\uC5D0\uB7EC \uACC4\uC57D"
- "blocked \uC804\uD658 \uBC0F \uAE30\uB85D API/CLI \uACBD\uB85C"
- "fallback \uC2DC plan \uBC18\uC601 \uADDC\uCE59 \uD14C\uC2A4\uD2B8"
verification:
- uv run --extra dev pytest -q
- uv run --extra dev ruff check .
- uv run --extra dev mypy .
links:
- PLAN-MAIN
- FLOW-MODE-TRANSITION
- ARCH-INDEX
---

# Task: T-013-build-plan-fallback-state

## Intent
<!-- taco:pack=task.core -->

- Build 중 설계/범위 충돌이 발생하면 조용히 실패하지 않고, 명시적으로 Plan 모드 복귀 상태를 남긴다.

## Goal
<!-- taco:pack=task.core -->

- `build -> plan` 전환을 표준화해 태스크가 어디서 왜 멈췄는지 추적 가능하게 만든다.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- build 중 전환 사유를 분류한다:
  - `architecture_change_required`
  - `scope_split_required`
  - `verification_ambiguous`
  - `dependency_out_of_scope`
- 전환 시 task 상태를 `blocked`로 업데이트하고 사유를 기록한다.
- plan의 `blocked_tasks`를 자동 동기화한다.
- 정상 완료(`done`) 경로와 blocked 경로가 서로 간섭하지 않게 한다.

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, FLOW-MODE-TRANSITION

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- `task.complete`와 별도 fallback 엔드포인트(또는 옵션)를 정의한다.
- fallback 동작은 dry-run/apply를 모두 지원한다.
- front matter + 본문 섹션을 함께 업데이트해 사람/기계 상태를 일치시킨다.
- 상태 전이 불가능한 경우 표준 에러 코드로 거부한다.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- blocked 전환 성공 케이스 검증
- 이유 코드 누락/잘못된 코드 입력 검증
- done 이후 blocked 재전환 금지 규칙 검증
- 회귀 검증:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

- Implemented build->plan fallback with new task.block flow, reason-code validation, blocked status transition, and plan blocked_tasks synchronization
- fallback flow implemented
## Verification Result

- Pending (do not fill until the task is completed)
- Validated via CLI dry-run/error paths and full ruff+mypy+pytest+doc-validation pass; added integration and unit coverage for block behavior
- tooling and tests passed
