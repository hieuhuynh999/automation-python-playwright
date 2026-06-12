from pathlib import Path

ATTACHMENT_DIR = Path("test-results/attachments")


def attach_text(name: str, content: str) -> None:
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    (ATTACHMENT_DIR / f"{name}.txt").write_text(content, encoding="utf-8")


def attach_png(name: str, content: bytes) -> None:
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    (ATTACHMENT_DIR / f"{name}.png").write_bytes(content)


def attach_file(path: str | Path, name: str | None = None) -> None:
    source = Path(path)
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    target = ATTACHMENT_DIR / (name or source.name)
    target.write_bytes(source.read_bytes())
