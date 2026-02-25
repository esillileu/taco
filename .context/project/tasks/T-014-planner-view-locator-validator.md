---
id: T-014
type: task
title: T-014-planner-view-locator-validator
status: todo
plan_ref: PLAN-MAIN
priority: p1
estimate: l
scope:
  in:
    - src/taco/tools.py
    - src/taco/indexer.py
    - src/taco/pack.py
    - tests/test_tools.py
    - tests/test_integration_mcp_cli.py
    - scripts/validate_docs.py
    - .context/project/architecture/flows/mode-transition.md
  out:
    - 전체 문서 요약 생성기
    - LLM 기반 비결정적 추천 로직
references:
  modules: [MOD-TOOLS-DISPATCH, MOD-INDEXER, MOD-PACK]
  flows: [FLOW-MODE-TRANSITION, FLOW-TASK-PACK, FLOW-TOOL-DISPATCH]
  schemas: [SCH-INDEX-GRAPH, SCH-TASK-NODE, SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
  governance: [GOV-CODE-PRINCIPLES, GOV-DOC-INDEX]
deliverables:
  - plan mode용 조회(view) 툴 세트
  - 작성 위치(locator) 제안 툴
  - 검증(validator) 결과 envelope 표준화
verification:
  - uv run --extra dev pytest -q
  - uv run --extra dev ruff check .
  - uv run --extra dev mypy .
links: [PLAN-MAIN, FLOW-MODE-TRANSITION, ARCH-INDEX]
---

# Task: T-014-planner-view-locator-validator

## Intent
<!-- taco:pack=task.core -->

- Plan 모드가 문서 직접 탐색 없이도 동작하도록 최소 Planner 도구(View/Locator/Validator)를 제공한다.

## Goal
<!-- taco:pack=task.core -->

- 문서 작성 에이전트가 필요한 맥락 조회, 수정 위치 결정, 규칙 검증을 tool surface로 수행할 수 있게 한다.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- View:
  - plan 요약(phase/active/blocked/next)
  - task 요약(goal/scope/references/status)
  - architecture 인덱스 요약(modules/flows/schemas)
- Locator:
  - 요청된 변경 타입(모듈/흐름/스키마/태스크)에 대한 대상 파일/섹션 후보 반환
- Validator:
  - 문서 무결성 체크 결과를 tool envelope로 반환
  - 기존 `scripts/validate_docs.py`와 결과 코드/메시지 정합 유지

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, FLOW-MODE-TRANSITION

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- `tools.py`에 planner 계열 액션을 추가한다(예: `plan.view`, `plan.locate`, `plan.validate`).
- index graph를 재사용해 조회/대상추론/검증 결과를 구성한다.
- 결과는 deterministic ordering을 유지한다.
- 대용량 문서 전체 반환을 금지하고 요약/슬라이스 중심으로 제한한다.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- 각 도구별 정상/오류 envelope 테스트 추가
- 동일 입력 반복 호출 시 동등 결과 검증
- validator 결과와 `scripts/validate_docs.py`의 실패 조건 일치 검증
- 회귀 검증:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
