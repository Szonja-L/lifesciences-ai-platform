"""Validation engine tests. The expected fixture issues are listed in the fixtures README."""

from datetime import date
from pathlib import Path

import pytest

from lifesciences_platform.common.validation import (
    RULE_SET_V1,
    IssueCode,
    Severity,
    ValidationIssue,
    validate_manifest,
)

FIXTURES = Path(__file__).parents[1] / "fixtures" / "manifests"
TODAY = date(2026, 11, 27)  # passed in, so no test depends on the system clock

HEADER = ",".join(rule.name for rule in RULE_SET_V1.columns)
GOOD_ROW = {
    "sample_id": "S-0001",
    "client_sample_label": "label_1",
    "organism": "Homo sapiens",
    "reference_genome": "GRCh38",
    "sample_type": "blood",
    "assay": "WES",
    "variant_file": "S-0001.vcf.gz",
    "dna_conc_ng_per_ul": "40",
    "collection_date": "2026-09-01",
}

Found = tuple[IssueCode, int | None, str | None]


def row(**changes: str) -> str:
    return ",".join({**GOOD_ROW, **changes}.values())


def manifest(*rows: str, header: str = HEADER) -> str:
    return "\n".join([header, *rows]) + "\n"


def validate(
    tmp_path: Path, content: str | bytes, *, name: str = "m.csv", max_rows: int = 1000
) -> list[ValidationIssue]:
    path = tmp_path / name
    path.write_bytes(content.encode() if isinstance(content, str) else content)
    return validate_manifest(path, RULE_SET_V1, today=TODAY, max_rows=max_rows)


def summary(issues: list[ValidationIssue]) -> list[Found]:
    return [(issue.code, issue.row, issue.column) for issue in issues]


def validate_fixture(name: str) -> list[ValidationIssue]:
    return validate_manifest(FIXTURES / name, RULE_SET_V1, today=TODAY)


# ------------------------------------------------------------------ the five fixtures


def test_valid_fixture_has_no_issues() -> None:
    assert validate_fixture("valid.csv") == []


def test_missing_columns_fixture() -> None:
    issues = validate_fixture("missing_columns.csv")

    assert summary(issues) == [
        (IssueCode.MISSING_COLUMN, None, "assay"),
        (IssueCode.MISSING_COLUMN, None, "collection_date"),
    ]
    assert {issue.severity for issue in issues} == {Severity.ERROR}


def test_invalid_values_fixture() -> None:
    issues = validate_fixture("invalid_values.csv")

    assert summary(issues) == [
        (IssueCode.UNKNOWN_COLUMN, None, "notes"),
        (IssueCode.INVALID_VALUE, 2, "sample_id"),
        (IssueCode.INVALID_VALUE, 3, "organism"),
        (IssueCode.MISSING_VALUE, 4, "assay"),
        (IssueCode.INVALID_TYPE, 5, "dna_conc_ng_per_ul"),
        (IssueCode.OUT_OF_RANGE, 6, "dna_conc_ng_per_ul"),
        (IssueCode.INVALID_TYPE, 7, "collection_date"),
        (IssueCode.OUT_OF_RANGE, 8, "collection_date"),
        (IssueCode.INCONSISTENT_REFERENCE, 9, "reference_genome"),
        (IssueCode.INVALID_VALUE, 10, "variant_file"),
        (IssueCode.DUPLICATE_SAMPLE_ID, 11, "sample_id"),
        (IssueCode.INVALID_VALUE, 12, "client_sample_label"),
        (IssueCode.INVALID_VALUE, 13, "sample_type"),
    ]
    assert [i.severity for i in issues] == [Severity.WARNING] + [Severity.ERROR] * 12


def test_empty_fixture() -> None:
    assert summary(validate_fixture("empty.csv")) == [(IssueCode.EMPTY_FILE, None, None)]


def test_unsupported_type_fixture() -> None:
    issues = validate_fixture("unsupported_type.txt")

    assert summary(issues) == [(IssueCode.UNSUPPORTED_FILE_TYPE, None, None)]


# ------------------------------------------------------------------ file level


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(b"  \r\n\t\n", id="whitespace only"),
        pytest.param(b"\xef\xbb\xbf", id="byte-order mark only"),
        pytest.param(b",,,\n,,,\n", id="commas only"),
    ],
)
def test_files_without_values_are_empty(tmp_path: Path, content: bytes) -> None:
    assert summary(validate(tmp_path, content)) == [(IssueCode.EMPTY_FILE, None, None)]


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(b"\xff\xfe\x00s", id="UTF-16"),
        pytest.param(manifest(row()).encode() + b"caf\xe9\n", id="Latin-1 byte"),
        pytest.param(manifest(row(variant_file="a\x00.vcf")), id="NUL byte"),
        pytest.param(manifest(row() + ",extra"), id="too many fields"),
        pytest.param(manifest("S-0001,only"), id="too few fields"),
        pytest.param(manifest(row().replace(",", ";")), id="semicolon delimiter"),
        pytest.param(manifest(row(client_sample_label='"unclosed')), id="unclosed quote"),
        pytest.param(manifest(row(client_sample_label='"a"b')), id="text after quote"),
        pytest.param(manifest(row(client_sample_label="x" * 200_000)), id="huge field"),
        pytest.param(manifest(row() + ",WES", header=HEADER + ",assay"), id="repeated column"),
    ],
)
def test_malformed_files_give_one_file_level_issue(tmp_path: Path, content: str | bytes) -> None:
    assert summary(validate(tmp_path, content)) == [(IssueCode.MALFORMED_CSV, None, None)]


def test_header_without_rows(tmp_path: Path) -> None:
    assert summary(validate(tmp_path, manifest())) == [(IssueCode.NO_DATA_ROWS, None, None)]


def test_row_limit_is_inclusive_and_stops_all_other_checks(tmp_path: Path) -> None:
    rows = [row(sample_id=f"S-{n:04d}") for n in range(1001)]

    assert validate(tmp_path, manifest(*rows[:1000])) == []

    # A bad header and bad cells go unreported once the limit is exceeded.
    bad = manifest(*[row(assay="nope")] * 1001, header=HEADER.replace("assay", "Assay"))
    assert summary(validate(tmp_path, bad)) == [(IssueCode.TOO_MANY_ROWS, None, None)]


def test_row_limit_can_be_set(tmp_path: Path) -> None:
    content = manifest(row(), row(sample_id="S-0002"))

    assert summary(validate(tmp_path, content, max_rows=1)) == [
        (IssueCode.TOO_MANY_ROWS, None, None)
    ]


def test_extension_check_ignores_case(tmp_path: Path) -> None:
    assert validate(tmp_path, manifest(row()), name="M.CSV") == []


def test_a_missing_file_is_not_reported_as_a_data_problem(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        validate_manifest(tmp_path / "absent.csv", RULE_SET_V1, today=TODAY)


# ------------------------------------------------------------------ layout that is allowed


def test_byte_order_mark_and_crlf_are_accepted(tmp_path: Path) -> None:
    content = b"\xef\xbb\xbf" + manifest(row()).replace("\n", "\r\n").encode()

    assert validate(tmp_path, content) == []


def test_values_and_column_names_are_trimmed(tmp_path: Path) -> None:
    header = " , ".join(HEADER.split(","))
    content = manifest(row(organism="  Homo sapiens ", assay="\tWES "), header=f"  {header}  ")

    assert validate(tmp_path, content) == []


def test_column_order_is_free(tmp_path: Path) -> None:
    header = ",".join(reversed(HEADER.split(",")))
    content = manifest(",".join(reversed(row().split(","))), header=header)

    assert validate(tmp_path, content) == []


def test_optional_column_may_be_absent(tmp_path: Path) -> None:
    values = {k: v for k, v in GOOD_ROW.items() if k != "client_sample_label"}

    assert validate(tmp_path, manifest(",".join(values.values()), header=",".join(values))) == []


def test_blank_and_comma_only_lines_are_ignored_but_still_counted(tmp_path: Path) -> None:
    content = manifest(row(), "", "   ", ",,,,,,,,", ",,", row(sample_id="bad"))

    assert summary(validate(tmp_path, content)) == [(IssueCode.INVALID_VALUE, 7, "sample_id")]


def test_row_is_the_line_where_a_multi_line_record_starts(tmp_path: Path) -> None:
    content = manifest(
        row(client_sample_label='"two\nlines"'),
        row(sample_id="S-0002", assay="nope"),
    )

    assert summary(validate(tmp_path, content)) == [
        (IssueCode.INVALID_VALUE, 2, "client_sample_label"),
        (IssueCode.INVALID_VALUE, 4, "assay"),
    ]


# ------------------------------------------------------------------ header level


def test_unnamed_header_cells_are_warnings(tmp_path: Path) -> None:
    issues = validate(tmp_path, manifest(row() + ",,", header=HEADER + ",,"))

    assert summary(issues) == [(IssueCode.UNKNOWN_COLUMN, None, None)] * 2
    assert {issue.severity for issue in issues} == {Severity.WARNING}
    assert "Column 10" in issues[0].message


def test_column_names_are_case_sensitive(tmp_path: Path) -> None:
    issues = validate(tmp_path, manifest(row(), header=HEADER.replace("assay", "Assay")))

    assert summary(issues) == [
        (IssueCode.MISSING_COLUMN, None, "assay"),
        (IssueCode.UNKNOWN_COLUMN, None, "Assay"),
    ]


def test_hostile_column_name_is_shortened_and_escaped(tmp_path: Path) -> None:
    name = "bad\tname" + "x" * 1000

    (issue,) = validate(tmp_path, manifest(row() + ",1", header=f"{HEADER},{name}"))

    assert issue.column is not None
    assert issue.column.startswith("bad\\tname")
    assert len(issue.column) == 255
    assert issue.message.isprintable()
    assert len(issue.message) < 200


# ------------------------------------------------------------------ cell values


@pytest.mark.parametrize(
    ("column", "value", "expected"),
    [
        ("sample_id", "S-00001", IssueCode.INVALID_VALUE),
        ("sample_id", "s-0001", IssueCode.INVALID_VALUE),
        ("sample_id", "S-١٢٣٤", IssueCode.INVALID_VALUE),  # Arabic-Indic digits
        ("client_sample_label", "a" * 65, IssueCode.INVALID_VALUE),
        ("assay", "wes", IssueCode.INVALID_VALUE),
        ("variant_file", "data/a.vcf", IssueCode.INVALID_VALUE),
        ("variant_file", "data\\a.vcf", IssueCode.INVALID_VALUE),
        ("variant_file", ".vcf", IssueCode.INVALID_VALUE),
        ("variant_file", "a.VCF", IssueCode.INVALID_VALUE),
        ("variant_file", '"a\nb.vcf"', IssueCode.INVALID_VALUE),
        ("dna_conc_ng_per_ul", "nan", IssueCode.INVALID_TYPE),
        ("dna_conc_ng_per_ul", "inf", IssueCode.INVALID_TYPE),
        ("dna_conc_ng_per_ul", "1e2", IssueCode.INVALID_TYPE),
        ("dna_conc_ng_per_ul", "1_0", IssueCode.INVALID_TYPE),
        ("dna_conc_ng_per_ul", '"4,5"', IssueCode.INVALID_TYPE),
        ("dna_conc_ng_per_ul", "0.49", IssueCode.OUT_OF_RANGE),
        ("dna_conc_ng_per_ul", "500.01", IssueCode.OUT_OF_RANGE),
        ("dna_conc_ng_per_ul", "-5", IssueCode.OUT_OF_RANGE),
        ("collection_date", "20260901", IssueCode.INVALID_TYPE),
        ("collection_date", "01-09-2026", IssueCode.INVALID_TYPE),
        ("collection_date", "2026-02-30", IssueCode.INVALID_TYPE),
        ("collection_date", "2026-11-28", IssueCode.OUT_OF_RANGE),
    ],
)
def test_bad_values(tmp_path: Path, column: str, value: str, expected: IssueCode) -> None:
    issues = validate(tmp_path, manifest(row(**{column: value})))

    assert summary(issues) == [(expected, 2, column)]


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("client_sample_label", "a" * 64),
        ("dna_conc_ng_per_ul", "0.50"),
        ("dna_conc_ng_per_ul", "500.0"),
        ("collection_date", "2026-11-27"),  # the validation date itself
        ("collection_date", "2024-02-29"),
    ],
)
def test_boundary_values_are_accepted(tmp_path: Path, column: str, value: str) -> None:
    assert validate(tmp_path, manifest(row(**{column: value}))) == []


def test_every_required_cell_can_be_missing(tmp_path: Path) -> None:
    # A record with every cell empty is ignored, so the optional cell stays filled.
    cells = {name: "" for name in GOOD_ROW} | {"client_sample_label": "x"}
    issues = validate(tmp_path, manifest(row(**cells)))

    assert summary(issues) == [
        (IssueCode.MISSING_VALUE, 2, rule.name) for rule in RULE_SET_V1.columns if rule.required
    ]


def test_each_later_duplicate_points_to_the_first_use(tmp_path: Path) -> None:
    issues = validate(tmp_path, manifest(row(), row(), row()))

    assert summary(issues) == [
        (IssueCode.DUPLICATE_SAMPLE_ID, 3, "sample_id"),
        (IssueCode.DUPLICATE_SAMPLE_ID, 4, "sample_id"),
    ]
    assert all("line 2" in issue.message for issue in issues)


def test_repeated_invalid_sample_id_is_not_also_a_duplicate(tmp_path: Path) -> None:
    issues = validate(tmp_path, manifest(row(sample_id="S-1"), row(sample_id="S-1")))

    assert summary(issues) == [
        (IssueCode.INVALID_VALUE, 2, "sample_id"),
        (IssueCode.INVALID_VALUE, 3, "sample_id"),
    ]


def test_messages_say_what_was_found_and_expected(tmp_path: Path) -> None:
    (issue,) = validate(tmp_path, manifest(row(organism="Homo sapien")))

    assert issue.message == (
        "organism: found 'Homo sapien', expected one of: Homo sapiens, Mus musculus."
    )


def test_long_values_are_shortened_in_messages(tmp_path: Path) -> None:
    (issue,) = validate(tmp_path, manifest(row(assay="z" * 5000)))

    assert len(issue.message) < 200
