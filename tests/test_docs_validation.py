from pathlib import Path


def test_key_docs_exist() -> None:
    required = [
        Path('.context/project/overview.md'),
        Path('.context/project/intents/index.md'),
        Path('.context/project/intents/I-001-intent-plan-mode.md'),
        Path('.context/project/architecture/index.md'),
        Path('.context/project/plan.md'),
        Path('.context/project/architecture/schemas/glossary.md'),
        Path('.context/governance/doc/index.md'),
        Path('.context/governance/code-principles.md'),
        Path('.context/project/tasks/T-007-pre-implementation-readiness.md'),
        Path('taco.yaml'),
        Path('pyproject.toml'),
        Path('scripts/validate_docs.py'),
    ]
    missing = [str(p) for p in required if not p.exists()]
    assert not missing, f"Missing required readiness files: {missing}"
