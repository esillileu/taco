# Plan

> 현재 구현 준비 단계를 기준으로 문서 정합성부터 구현 착수 준비까지의 순서를 정의한다.

## References

- [Intent](./intent.md) - 프로젝트 목표와 성공 기준
- [Architecture](./architecture.md) - 설계 경계와 모듈 책임
- [Glossary](./glossary.md) - 용어 정합성

## Phase 0: Implementation Readiness (Current)

- SSOT 4문서와 `docs/dev` 운영 문서 역할을 고정한다.
- task 추적/기록 규칙을 문서로 확정한다.
- 기능 정의(도구 표면, 입력/출력, 라우팅 기준)를 문서에 반영한다.

## Phase 1: Scope and Interface Definition

- task별 `Intent/Goal/Scope`를 SSOT 기반으로 구체화한다.
- MCP 도구별 입력/출력 스키마를 명확히 정리한다.
- 도구 네이밍을 단수 도메인 + 간결 액션으로 고정하고 CLI(`taco <domain> <action>`)와 1:1 매핑한다.
- Python 구현과 Rust 포팅 간 공통 DTO/에러 계약을 고정한다.
- 문서 참조 체계를 `selector group` 중심에서 `stable reference id` 중심으로 고정한다.

## Phase 2: Approach and Verification Design

- task별 구현 접근과 검증 접근을 설계한다.
- 결정/미정/리스크를 문서에서 추적 가능하게 정리한다.
- I/O 분리, 순수 코어, 설정 기반 규칙, 캐시/동시성 분리 원칙을 task 설계에 반영한다.
- 행동 기반 테스트와 golden fixture 전략을 확정한다.
- task 문서에서 `Context Requirements`를 통해 필요한 참조 식별자를 선언하도록 표준화한다.
- pack 조립은 `공통 베이스 + task 선언 참조`만 포함하도록 제한한다.

## Phase 3: Implementation Kickoff Preparation

- parser -> indexer -> pack -> router -> server -> integration tests 순서를 확정한다.
- 구현 결과 기록 섹션(`Implementation Result`, `Verification Result`) 사용 조건을 고정한다.
- 구현된 `taco`를 본 레포 운영에 적용하는 dogfooding 경로를 고정한다.
- 문서 검증 단계에서 참조 식별자 중복/누락/해결 불가 항목을 실패로 처리한다.
