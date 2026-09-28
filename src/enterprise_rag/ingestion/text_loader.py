from pathlib import Path

def load_txt(file_path:str | Path)-> list[dict]:
    "load text from a text file"
    path=Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"path not found{path}")

    text=path.read_text(encoding="utf-8").strip()

    if not text:
        return []

    return [{

        "text": text,
            "source": path.name,
            "file_type": "txt",
            "page": None,
    }]