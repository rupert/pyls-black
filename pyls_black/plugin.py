from typing import Dict

import black
import toml
from pyls import hookimpl


@hookimpl(tryfirst=True)
def pyls_format_document(document):
    return format_document(document)


@hookimpl(tryfirst=True)
def pyls_format_range(document, range):
    range["start"]["character"] = 0
    range["end"]["line"] += 1
    range["end"]["character"] = 0
    return format_document(document, range)


def format_document(document, range=None):
    if range:
        start = range["start"]["line"]
        end = range["end"]["line"]
        text = "".join(document.lines[start:end])
    else:
        text = document.source
        range = {
            "start": {"line": 0, "character": 0},
            "end": {"line": len(document.lines), "character": 0},
        }

    config = load_config(document.path)

    try:
        formatted_text = format_text(text=text, config=config)
    except (
        ValueError,
        # raised when the file is already formatted correctly
        black.NothingChanged,
        # raised when the file being formatted has an indentation error
        IndentationError,
        # raised when black produces invalid Python code or formats the file
        # differently on the second pass
        AssertionError,
    ):
        return []

    return [{"range": range, "newText": formatted_text}]


def format_text(*, text, config):
    fast = config["fast"]
    mode = black.FileMode(
        target_versions=black.PY36_VERSIONS
        if config["py36"]
        else set(config["target_versions"]),
        line_length=config["line_length"],
        is_pyi=config["is_pyi"],
        string_normalization=config["string_normalization"],
    )
    return black.format_file_contents(text, fast=fast, mode=mode)


def load_config(filename: str) -> Dict:
    defaults = {
        "line_length": 88,
        "fast": False,
        "target_versions": [],
        "py36": False,
        "is_pyi": filename.endswith(".pyi"),
        "string_normalization": False,
    }

    root = black.find_project_root((filename,))

    pyproject_filename = root / "pyproject.toml"

    if not pyproject_filename.is_file():
        return defaults

    try:
        pyproject_toml = toml.load(str(pyproject_filename))
    except (toml.TomlDecodeError, OSError):
        return defaults

    config = pyproject_toml.get("tool", {}).get("black", {})
    config = {
        key.replace("--", "").replace("-", "_"): value for key, value in config.items()
    }

    return {**defaults, **config}
