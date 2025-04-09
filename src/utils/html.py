from typing import Any, NamedTuple, overload


def code(string: str):
    return f"<code>{string}</code>"


def bold(string: str):
    return f"<b>{string}</b>"


class TableColumn(NamedTuple):
    title: str
    results: list[Any]


@overload
def table(
    title: str,
    *,
    row_header: list[Any],
    rows: list[list[Any]],
) -> str: ...


@overload
def table(
    title: str,
    *,
    columns: list[TableColumn],
) -> str: ...


def table(
    title: str,
    *,
    row_header: list[Any] | None = None,
    rows: list[list[Any]] | None = None,
    columns: list[TableColumn] | None = None,
) -> str:
    head = ""

    rows_: list[list[str]] = []
    if columns:
        for col in columns:
            head += f"<th>{col.title}</th>"
            for index, row in enumerate(col.results):
                if col.title in ("value", "值"):
                    row = code(row)
                row = f"<td>{row}</td>"
                try:
                    if isinstance(rows_[index], list):
                        rows_[index].append(row)
                except IndexError:
                    rows_.append([row])

        rows___ = [f"<tr>{''.join(row)}</tr>" for row in rows_]
    else:
        assert row_header is not None
        head = "".join(f"<th>{title_}</th>" for title_ in row_header)

        assert rows is not None
        rows___ = [
            f"<tr>{''.join(f'<td>{i}</td>' for i in row)}</tr>" for row in rows
        ]

    head = f"<thead>{head}</thead>"
    body = f"<tbody>{''.join(rows___)}</tbody>"

    return f"<table><caption>{bold(title)}</caption>{head}{body}</table>"
