"""Manifest rule sets, written as data. This file says what is valid; engine.py says how to check.

Mirrors docs/architecture/track-a-spec.md section 8. A released rule set is never edited:
a change means a new version, recorded in git and an ADR (spec section 10).

Rules that apply to every column: values are trimmed first, an empty cell counts as missing,
enum values are case-sensitive and text values may hold printable characters only.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType


@dataclass(frozen=True, kw_only=True)
class Column:
    name: str
    required: bool = True


@dataclass(frozen=True, kw_only=True)
class TextColumn(Column):
    pattern: str  # must match the whole value
    expected: str  # plain English, used in the error message


@dataclass(frozen=True, kw_only=True)
class EnumColumn(Column):
    allowed: tuple[str, ...]


@dataclass(frozen=True, kw_only=True)
class DecimalColumn(Column):
    minimum: Decimal  # inclusive
    maximum: Decimal  # inclusive


@dataclass(frozen=True, kw_only=True)
class DateColumn(Column):
    """ISO YYYY-MM-DD, a real date, not later than the validation date."""


ColumnRule = TextColumn | EnumColumn | DecimalColumn | DateColumn


@dataclass(frozen=True, kw_only=True)
class DependentValueRule:
    """The value of `column` is decided by the value of `depends_on`."""

    column: str
    depends_on: str
    required_value: Mapping[str, str]


@dataclass(frozen=True, kw_only=True)
class RuleSet:
    version: str
    columns: tuple[ColumnRule, ...]
    unique_column: str  # no value may appear twice in one file
    dependent_value: DependentValueRule


# Patterns use [0-9] and not \d, which would also accept digits from other alphabets.
RULE_SET_V1 = RuleSet(
    version="v1",
    columns=(
        TextColumn(
            name="sample_id",
            pattern=r"S-[0-9]{4}",
            expected="'S-' followed by exactly 4 digits",
        ),
        TextColumn(
            name="client_sample_label",
            required=False,
            pattern=r"[A-Za-z0-9_-]{1,64}",
            expected="1 to 64 letters, digits, '_' or '-'",
        ),
        EnumColumn(name="organism", allowed=("Homo sapiens", "Mus musculus")),
        EnumColumn(name="reference_genome", allowed=("GRCh38", "GRCm39")),
        EnumColumn(
            name="sample_type",
            allowed=("blood", "saliva", "tissue", "cell_line", "dna_extract"),
        ),
        EnumColumn(name="assay", allowed=("WGS", "WES", "targeted_panel")),
        TextColumn(
            name="variant_file",
            pattern=r"[^/\\]+\.vcf(\.gz)?",
            expected="a file name without folders, ending '.vcf' or '.vcf.gz'",
        ),
        DecimalColumn(name="dna_conc_ng_per_ul", minimum=Decimal("0.5"), maximum=Decimal("500")),
        DateColumn(name="collection_date"),
    ),
    unique_column="sample_id",
    dependent_value=DependentValueRule(
        column="reference_genome",
        depends_on="organism",
        required_value=MappingProxyType({"Homo sapiens": "GRCh38", "Mus musculus": "GRCm39"}),
    ),
)
