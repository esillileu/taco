---
id: T-013
type: task
title: T-013-build-plan-fallback-state
status: todo
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
    - 자동 태스크 분해/생성 엔진
    - 외부 이슈 트래커 연동
references:
  modules: [MOD-TOOLS-DISPATCH, MOD-ROUTER, MOD-MAIN]
  flows: [FLOW-MODE-TRANSITION, FLOW-TASK-RECORD]
  schemas: [SCH-TASK-NODE, SCH-TOOL-ERROR, SCH-TOOL-ENVELOPE]
  governance: [GOV-CODE-PRINCIPLES]
deliverables:
  - build->plan fallback 표준 상태/에러 계약
  - blocked 전환 및 기록 API/CLI 경로
  - fallback 시 plan 반영 규칙 테스트
verification:
  - uv run --extra dev pytest -q
  - uv run --extra dev ruff check .
  - uv run --extra dev mypy .
links: [PLAN-MAIN, FLOW-MODE-TRANSITION, ARCH-INDEX]
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

## Verification Result

- Pending (do not fill until the task is completed)
