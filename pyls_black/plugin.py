import logging
import subprocess
from pathlib import Path

from pyls import hookimpl

logger = logging.getLogger(__name__)


class BlackError(Exception):
    pass


@hookimpl
def pyls_format_document(document):
    return format_document(document)


@hookimpl
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

    try:
        formatted_text = format_text(text=text, path=document.path)
    except BlackError:
        logger.exception("Error running black")
        return []

    if text == formatted_text:
        return []

    return [{"range": range, "newText": formatted_text}]


def format_text(*, text, path):
    cwd = Path(path).parent
    p = subprocess.Popen(
        ["python3", "-m", "black", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
    )
    stdout, stderr = p.communicate(text.encode("utf-8"))

    if p.returncode != 0:
        raise BlackError(stderr.decode().strip())

    return stdout.decode("utf-8")
