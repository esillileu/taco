---
id: T-015
type: task
title: T-015-init-context-bootstrap
status: todo
plan_ref: PLAN-MAIN
priority: p1
estimate: m
scope:
  in:
    - src/taco/main.py
    - src/taco/cli.py
    - src/taco/tools.py
    - scripts/validate_docs.py
    - tests/test_cli_main.py
    - tests/test_tools.py
    - tests/test_integration_mcp_cli.py
  out:
    - 기존 task/doc/pack 동작의 breaking change
    - 프로젝트별 커스텀 템플릿 생성기
references:
  modules: [MOD-MAIN, MOD-CLI-MAPPER, MOD-TOOLS-DISPATCH]
  flows: [FLOW-TOOL-DISPATCH, FLOW-MODE-TRANSITION]
  schemas: [SCH-TOOL-ENVELOPE, SCH-TOOL-ERROR]
  governance: [GOV-CODE-PRINCIPLES, GOV-DOC-INDEX]
deliverables:
  - "`taco init` CLI 엔트리포인트"
  - "`.context` 기본 디렉토리/문서 템플릿 생성"
  - front matter 기본값과 작성 가이드 섹션 포함
  - "init 후 `validate_docs.py` 통과 가능한 최소 상태 보장"
verification:
  - uv run --extra dev ruff check .
  - uv run --extra dev mypy .
  - uv run --extra dev pytest -q
  - uv run --extra dev python scripts/validate_docs.py
links: [PLAN-MAIN, ARCH-INDEX, FLOW-MODE-TRANSITION]
---

# Task: T-015-init-context-bootstrap

## Intent
<!-- taco:pack=task.core -->

- 새 레포에서 초기 문서 구조를 수동으로 만들지 않고 `taco init` 한 번으로 시작 가능하게 한다.

## Goal
<!-- taco:pack=task.core -->

- 표준 `.context` 골격과 필수 문서를 자동 생성해 즉시 task-first workflow를 시작할 수 있게 한다.

## Scope
<!-- taco:pack=task.core,pack.next_actions -->

- `taco init` 명령을 추가한다.
- 생성 대상:
  - `.context/project/overview.md`
  - `.context/project/plan.md`
  - `.context/project/architecture/index.md`
  - `.context/project/architecture/modules/`
  - `.context/project/architecture/flows/`
  - `.context/project/architecture/schemas/`
  - `.context/project/tasks/`
  - `.context/governance/code-principles.md`
  - `.context/governance/git/index.md`
  - `.context/governance/doc/index.md`
- 각 기본 문서에 front matter 템플릿과 최소 작성 가이드를 포함한다.
- 이미 파일이 존재하는 경우 안전하게 실패하거나 skip 정책을 명확히 적용한다.

## Context Requirements

- required: ARCH-INDEX, PLAN-MAIN, FLOW-MODE-TRANSITION

## Implementation Approach
<!-- taco:pack=task.plans,pack.next_actions -->

- CLI에 `init` 도메인/액션을 추가한다.
- 템플릿 생성 로직은 tools 레이어에서 파일 I/O로 구현한다.
- 템플릿 값은 Rust 이관을 고려해 단순 DTO/문자열 기반으로 유지한다.
- init 결과를 표준 envelope(`ok/data` 또는 `error`)로 반환한다.

## Verification Approach
<!-- taco:pack=task.plans,pack.acceptance_checks,pack.verification_commands -->

- 빈 임시 디렉토리에서 `taco init` 실행 시 필수 구조 생성 확인
- 재실행 시 정책(실패/skip) 일관성 확인
- 생성 후 `python scripts/validate_docs.py` 통과 확인
- 회귀 검증:
  - `uv run --extra dev ruff check .`
  - `uv run --extra dev mypy .`
  - `uv run --extra dev pytest -q`
  - `uv run --extra dev python scripts/validate_docs.py`

## Implementation Result

- Pending (do not fill until the task is completed)

## Verification Result

- Pending (do not fill until the task is completed)
