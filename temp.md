# TACO Front Matter Spec (Common + Per-Document)

> 목적: 모든 문서를 “참조 단위(node)”로 취급하고, TACO가 필요한 조각을 안정적으로 수집/번들링할 수 있게 한다.
> 주의: 아래는 **필드 스펙**이다. 실제 값/예시는 최소로만 든다.

---

## 0) Common Front Matter (All Documents)

```yaml
---
id:            # 전역 유니크 ID (예: ARCH-INDEX, MOD-GENERATOR, FLOW-PUZZLE-GEN, SCH-PuzzleSpec, TASK-001)
type:          # anchor|module|flow|schema|task|plan|governance
title:         # 짧은 제목
status:        # draft|active|deprecated (task는 todo|active|done|blocked 권장)

owner:         # optional: 담당자/팀/에이전트 이름
tags:          # optional: 검색용 태그 배열
created:       # optional: YYYY-MM-DD
updated:       # optional: YYYY-MM-DD

links:         # optional: 이 문서가 참조하는 문서들(경로 또는 id)
  -            # 예: project/architecture/modules/generator.md

notes:         # optional: 짧은 메모
---
```

### Common Rules

* `id`는 절대 바뀌지 않는 “주소”로 취급한다.
* `type`은 파싱/필터링의 1차 키다.
* 내용 중복을 피하고, 연결은 `links` 또는 문서 내 링크로 한다.

---

## 1) /project/plan.md (Plan)

```yaml
---
id:
type: plan
title:
status:

phase:         # 현재 페이즈/포커스 이름
focus:         # 한 줄 요약(지금의 목표)

active_tasks:  # 활성 task id/경로 목록
  -            # 예: project/tasks/TASK-001.md

blocked_tasks: # optional: 차단된 task 목록
  -

next_tasks:    # optional: 다음 후보 task 목록
  -

milestones:    # optional: 마일스톤 키워드/링크
  -

links:
  -
---
```

### Boundary

* 설계(구조/흐름/계약) 재서술 금지
* task 본문 복사 금지

---

## 2) /project/architecture/index.md (Architecture Anchor)

```yaml
---
id:
type: anchor
title:
status:

modules_dir:   # optional: project/architecture/modules
flows_dir:     # optional
schemas_dir:   # optional

modules:       # 인덱스(목록) - id 또는 경로
  -
flows:
  -
schemas:
  -

dependency_rules:  # optional: 한 줄 규칙 리스트(요약)
  -

links:
  -
---
```

### Boundary

* 상세(구현/알고리즘/내부 구조) 금지
* “지도(목록/링크/한 줄 요약)”만 유지

---

## 3) /project/architecture/modules/*.md (Module Leaf)

```yaml
---
id:
type: module
title:
status:

role:          # 모듈 역할(한 문장)
boundary:      # 경계/책임 요약(짧게)

depends_on:    # 의존 대상(모듈/라이브러리/패키지) - id 또는 이름
  -
provides:      # 제공하는 계약/스키마 - schema id
  -
consumes:      # 소비하는 계약/스키마 - schema id
  -

must_not:      # 금지 규칙(레이어 역참조 등)
  -
invariants:    # optional: 불변 조건(짧게)
  -

decomposable:  # optional: true|false
children:      # optional: 하위 모듈 - module id/경로
  -

related_flows: # optional: 관련 흐름 - flow id
  -

links:
  -
---
```

### Boundary

* 전역 흐름 장문 재서술 금지(필요하면 flow 링크)
* schema 정의 복사 금지(schema 링크)

---

## 4) /project/architecture/flows/*.md (Flow Leaf)

```yaml
---
id:
type: flow
title:
status:

purpose:       # 이 흐름의 목적(한 문장)

path:          # 모듈 경계 레벨 경로(문자열 또는 배열)
              # 예: ["generator", "validator", "interaction"]

touches_modules:
  -            # module id

inputs:        # optional: 입력 스키마 - schema id
  -
outputs:       # optional: 출력 스키마 - schema id
  -

state_owner:   # optional: 상태 변경 소유자(모듈 id)
branches:      # optional: 주요 분기 조건 요약
  -

constraints:   # optional: 이 흐름에서 지켜야 할 제약(요약)
  -

links:
  -
---
```

### Boundary

* 모듈 내부 함수 호출/알고리즘 상세 금지
* 모듈 경계 레벨(A → B → C) 유지

---

## 5) /project/architecture/schemas/*.md (Schema Leaf)

```yaml
---
id:
type: schema
title:
status:

purpose:       # 스키마 목적(한 문장)

used_by_modules:  # optional: module id
  -
used_in_flows:    # optional: flow id
  -

shape:         # optional: 형상 요약(필드/타입 힌트). 상세는 본문.
               # 예: { fieldA: string, fieldB: int }

rules:         # optional: 제약/불변 규칙(요약)
  -

compatibility: # optional: 호환성/버전 규칙 요약
  -

links:
  -
---
```

### Boundary

* 비즈니스 로직/동작 흐름 과다 금지
* “계약”만 유지

---

## 6) /project/tasks/*.md (Task Node)

```yaml
---
id:
type: task
title:
status:        # todo|active|done|blocked

plan_ref:      # plan 항목/페이즈/마일스톤 참조(문자열 또는 링크)
priority:      # optional: p0|p1|p2
estimate:      # optional: s|m|l 또는 포인트

scope:
  in:
    -          # 모듈/경로/파일 패턴
  out:
    -          # 금지/제외 범위

references:
  modules:
    -          # module id/경로
  flows:
    -          # flow id/경로
  schemas:
    -          # schema id/경로
  governance:
    -          # optional: 필요한 규칙 문서 경로

deliverables:  # optional: 산출물 체크 항목(요약)
  -

verification:  # optional: 검증 방법/커맨드/기준(요약)
  -

links:
  -
---
```

### Boundary

* 설계 정의 복사 금지(요약 + 링크)
* Task는 “실행 번들”로서 Goal/Scope/Plan/DoD/Verification을 본문에 둔다

---

## 7) /governance/code-principles.md (Governance)

```yaml
---
id:
type: governance
title:
status:

scope:         # optional: global|project|language|repo
applies_to:    # optional: ["python", "docs"] 등

must:          # optional: 반드시 지켜야 하는 규칙(요약)
  -
must_not:      # optional: 금지 규칙(요약)
  -

links:
  -
---
```

---

## 8) /governance/git/*.md, /governance/doc/*.md (Governance Sub)

```yaml
---
id:
type: governance
title:
status:

domain:        # git|doc
scope:         # global|repo

must:
  -
must_not:
  -

links:
  -
---
```

---

## 운영 규칙(요약)

1. 정의(SSOT)는 architecture/에만 둔다. Task는 요약 + 참조만.
2. plan.md는 얇게: 활성 task 링크와 우선순위만.
3. architecture/index.md는 지도: 목록/링크/한 줄 요약만.
4. 문서가 커지면 Leaf → Anchor 승격 후 children으로 분해.
5. 에이전트에는 항상 Task 1개 + 관련 문서의 필요한 섹션만 전달.
