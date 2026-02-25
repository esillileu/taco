# Architecture

> TACO의 경계와 데이터 흐름을 정의해 문서 기반 작업 오케스트레이션의 재현성을 보장한다.

## References

- [Intent](./intent.md) - 문제와 목표
- [Plan](./plan.md) - 단계별 진행 범위
- [Glossary](./glossary.md) - 용어 정합성

## 시스템 경계
<!-- taco:pack=arch.snippets -->

- TACO는 로컬 STDIO MCP 서버다.
- Git 문서가 SSOT이며 캐시는 보조 인덱스 용도다.
- 컨텍스트 생성은 요약이 아니라 파싱/슬라이싱 기반 추출이다.

## 구현 전략 경계
<!-- taco:pack=arch.snippets -->

- 1차 구현은 Python으로 빠르게 제공한다.
- 최종 런타임은 순수 Rust 바이너리로 전환한다.
- 전환 시에도 MCP/CLI 도구 표면과 DTO 계약은 유지한다.

## 처리 파이프라인

1. Scan: 문서 목록 수집
2. Parse: 헤딩/앵커 구조 파싱
3. Index: 문서 타입/ID/링크 그래프 생성
4. Assemble: Task 중심 섹션 조립
5. Budget: 섹션 단위 예산 절단
6. Respond: MCP 응답 반환

## 핵심 모듈

- `parser`: heading/anchor 파싱과 section slice 계산
- `indexer`: 문서 탐색, 타입 분류, ID 추출, 링크 그래프 생성
- `pack`: task-centric context 조립
- `budget`: 토큰 추정과 우선순위 절단
- `router`: write target 계산과 기록 지시
- `server`: MCP tool surface 노출 및 라우팅

## 인터페이스 표면(요약)

- `task.list`
- `task.pack`
- `task.targets`
- `task.record`
- `issue.triage`
- `doc.snippet`
- `convention.get` (git on-demand)

## CLI 매핑 규칙

- 형식: `taco <domain> <action> [options]`
- MCP 도구명과 CLI는 1:1로 매핑한다.

## 의존성 규칙

- `server -> core -> storage`
- `core`는 `server`를 import 하지 않는다.
- `parser`는 `storage`를 import 하지 않는다.

## 포팅 친화 설계 원칙

- Tool boundary에서 DTO를 고정하고 내부 언어별 표현과 분리한다.
- `core`는 순수 함수 중심으로 설계하고 I/O는 adapter에 한정한다.
- 에러는 표준 구조(`code`, `message`, `details`)로 정규화한다.
- 정책값(헤딩 규칙, 우선순위, 토큰 예산, 경로)은 설정 파일에서 로드한다.
- 동시성/캐시 정책은 `core`와 분리해 교체 가능하게 둔다.

## Dogfooding 원칙

- 구현된 도구는 이 레포의 계획/검증 흐름에 즉시 적용한다.
- dogfooding에서 발견된 결함은 동일 이터레이션에서 우선 수정한다.
