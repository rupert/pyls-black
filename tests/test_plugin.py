from pathlib import Path

import pytest
from pyls.workspace import Document

from pyls_black.plugin import pyls_format_document, pyls_format_range

here = Path(__file__).parent
fixtures_dir = here / "fixtures"


@pytest.fixture
def unformatted_document():
    path = fixtures_dir / "unformatted.txt"
    uri = f"file:/{path}"
    return Document(uri)


@pytest.fixture
def formatted_document():
    path = fixtures_dir / "formatted.txt"
    uri = f"file:/{path}"
    return Document(uri)


@pytest.fixture
def invalid_document():
    path = fixtures_dir / "invalid.txt"
    uri = f"file:/{path}"
    return Document(uri)


@pytest.fixture
def config_document():
    path = fixtures_dir / "config" / "config.txt"
    uri = f"file:/{path}"
    return Document(uri)


def test_pyls_format_document(unformatted_document, formatted_document):
    result = pyls_format_document(unformatted_document)

    assert result == [
        {
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 2, "character": 0},
            },
            "newText": formatted_document.source,
        }
    ]


def test_pyls_format_document_unchanged(formatted_document):
    result = pyls_format_document(formatted_document)

    assert result == []


def test_pyls_format_document_syntax_error(invalid_document):
    result = pyls_format_document(invalid_document)

    assert result == []


def test_pyls_format_document_with_config(config_document):
    result = pyls_format_document(config_document)

    assert result == [
        {
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": 1, "character": 0},
            },
            "newText": (
                "run(\n"
                "    these,\n"
                "    arguments,\n"
                "    should,\n"
                "    be,\n"
                "    wrapped,\n"
                ")\n"
            ),
        }
    ]


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [(0, 0, 'a = "hello"\n'), (1, 1, "b = 42\n"), (0, 1, 'a = "hello"\nb = 42\n')],
)
def test_pyls_format_range(unformatted_document, start, end, expected):
    range = {
        "start": {"line": start, "character": 0},
        "end": {"line": end, "character": 0},
    }

    result = pyls_format_range(unformatted_document, range=range)

    assert result == [
        {
            "range": {
                "start": {"line": start, "character": 0},
                "end": {"line": end + 1, "character": 0},
            },
            "newText": expected,
        }
    ]


def test_pyls_format_range_unchanged(formatted_document):
    range = {"start": {"line": 0, "character": 0}, "end": {"line": 1, "character": 0}}

    result = pyls_format_range(formatted_document, range=range)

    assert result == []


def test_pyls_format_range_syntax_error(invalid_document):
    range = {"start": {"line": 0, "character": 0}, "end": {"line": 1, "character": 0}}

    result = pyls_format_range(invalid_document, range=range)

    assert result == []
