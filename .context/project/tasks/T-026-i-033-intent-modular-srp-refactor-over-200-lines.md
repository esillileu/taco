---
id: T-026
type: task
title: T-026-i-033-intent-modular-srp-refactor-over-200-lines
status: blocked
plan_ref: PLAN-MAIN
scope:
  in:
  - src/taco
  - tests
  - .context/project
  out: []
references:
  modules:
  - ARCH-INDEX
  flows:
  - PLAN-MAIN
  schemas:
  - GOV-CODE-PRINCIPLES
links:
- PLAN-MAIN
- I-033
- ARCH-INDEX
- GOV-CODE-PRINCIPLES
---

# Task: T-026-i-033-intent-modular-srp-refactor-over-200-lines

## Intent

- 200줄 초과 파일을 책임 단위로 분해해 확장성과 유지보수성을 높인다.

## Goal

- 단순 파일 쪼개기가 아니라 목적 중심 모듈 경계로 재설계한다.
- 기존 CLI/MCP 공개 계약은 유지하고 내부 구조만 분리한다.

## Scope

- 코드 영역:
  - `src/taco/core/usecases/plan/intent.py` 분해
  - `src/taco/apps/cli/mapper.py` 분해
  - `src/taco/core/task/pack.py` 분해
  - `src/taco/core/usecases/build/actions.py` 분해
  - `src/taco/apps/mcp/main.py` 분해
- 테스트 영역:
  - `tests/test_tools.py`, `tests/test_cli_main.py`, `tests/test_integration_mcp_cli.py`를 기능군별 테스트 모듈로 분리
- 문서 영역:
  - 아키텍처 모듈 문서와 플로우 문서를 신규 경계에 맞춰 동기화

## Implementation Approach

1. 책임 매핑과 분해 기준 확정
   - 파일별 책임을 `orchestration`, `validation`, `payload-mapping`, `state-transition`, `io-adapter`로 분류한다.
   - 모듈명 규칙을 기능 중심으로 통일한다.
     - 예: `plan/intent_proposal.py`, `plan/intent_design.py`, `plan/intent_review.py`, `plan/intent_apply.py`
     - 예: `cli/map/task_commands.py`, `cli/map/plan_commands.py`, `cli/map/build_commands.py`
2. 도메인별 모듈 분할 실행
   - `plan/intent.py`:
     - fingerprint 단계별 처리와 문서 갱신 로직을 독립 모듈로 분리한다.
     - refactor gate, review gate, apply gate를 별도 모듈로 분리한다.
   - `core/task/pack.py`:
     - pack assembly, readiness check, budget allocation, reference slicing을 분리한다.
   - `build/actions.py`:
     - precheck validator와 postcheck drift analyzer를 분리한다.
     - postcheck 입력 정규화 모듈을 분리한다.
   - `apps/mcp/main.py`:
     - request validation, method dispatch, lifecycle state machine, io loop를 분리한다.
3. 테스트 구조 리팩터링
   - 통합 테스트 파일을 기능군으로 재배치한다.
     - `tests/cli/`, `tests/build/`, `tests/mcp/`, `tests/plan/`, `tests/task/`
   - fixture 재사용 모듈(`tests/fixtures/`)을 도입해 중복 셋업을 제거한다.
4. 문서 동기화
   - `.context/project/architecture/modules/*`에 신규 분해 경계 반영.
   - `.context/project/architecture/flows/*`에서 단계 책임과 호출 경로 갱신.
   - `entrypoint-build`, `entrypoint-plan`의 실행 예시를 변경된 경계에 맞춰 정리.
5. 단계적 적용 순서
   - 1차: `build/actions.py`, `apps/mcp/main.py`처럼 범위가 작은 실행 계층부터 분해
   - 2차: `cli/mapper.py`, `core/task/pack.py`
   - 3차: `core/usecases/plan/intent.py`와 대형 테스트 파일 분해

## Verification Approach

- 구조 검증:
  - 분해 후 200줄 초과 파일 재집계(`wc -l`) 결과 확인
  - 순환 의존 및 역의존 여부 점검(`core -> apps/adapters` 금지)
- 동작 검증:
  - `uv run pytest -q`
  - 리팩터링 대상 기능군별 테스트 선택 실행
- 계약 검증:
  - CLI 명령 매핑과 MCP 툴 응답 계약이 기존과 동일한지 회귀 확인
  - `uv run taco plan validate`
  - `uv run python scripts/validate_docs.py`

## Implementation Result

- Plan-mode authored task only. Implementation is deferred to build-mode execution.

- - Refactored CLI mapper into responsibility-based modules under src/taco/apps/cli/map (dispatch/task/plan/doc/build/common) while keeping public facade src/taco/apps/cli/mapper.py stable.\n- Split build usecases into focused modules: precheck.py, postcheck.py, diagnostics.py, misc.py and removed oversized build/actions.py.\n- Split MCP runtime responsibilities into catalog.py, protocol.py, handlers.py, runtime.py with main.py as thin entrypoint facade.\n- Synced architecture docs for new module boundaries (cli-mapper/apps/tools-dispatch).
- blocked: [scope_split_required] Remaining >200-line decomposition targets (core/usecases/plan/intent.py, core/task/pack.py, and large test suites) require separate staged tasks to avoid high-risk mixed refactor in one loop.
## Verification Result

- Plan readiness only. Build verification pending.
- - uv run ruff check src/taco/apps/cli src/taco/core/usecases/build src/taco/apps/mcp tests/test_cli_main.py tests/test_integration_mcp_cli.py tests/test_tools.py : pass\n- uv run pytest -q tests/test_cli_main.py tests/test_integration_mcp_cli.py tests/test_tools.py : pass\n- uv run python scripts/validate_docs.py : pass\n- uv run pytest -q : pass\n- uv run taco plan validate : pass
