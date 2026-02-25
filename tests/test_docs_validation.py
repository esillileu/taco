from pathlib import Path


def test_key_docs_exist() -> None:
    required = [
        Path('docs/intent.md'),
        Path('docs/architecture.md'),
        Path('docs/plan.md'),
        Path('docs/glossary.md'),
        Path('docs/dev/docs.md'),
        Path('docs/dev/principles.md'),
        Path('docs/dev/todo.md'),
        Path('docs/dev/tasks/T-007-pre-implementation-readiness.md'),
        Path('taco.yaml'),
        Path('pyproject.toml'),
        Path('scripts/validate_docs.py'),
    ]
    missing = [str(p) for p in required if not p.exists()]
    assert not missing, f"Missing required readiness files: {missing}"
