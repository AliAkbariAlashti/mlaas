import pandas as pd

from .exceptions import EmptyColumnError, RowParsingError


def require_columns(data_frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in data_frame.columns]
    if missing:
        raise EmptyColumnError(f"Missing mapped columns: {', '.join(missing)}")
    empty = [column for column in columns if data_frame[column].dropna().empty]
    if empty:
        raise EmptyColumnError(f"Mapped columns contain no values: {', '.join(empty)}")


def parse_datetime(series: pd.Series, column_name: str) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", utc=True)
    if parsed.isna().any():
        raise RowParsingError(f"Datetime format in column '{column_name}' cannot be parsed.")
    return parsed


def parse_numeric(series: pd.Series, column_name: str) -> pd.Series:
    parsed = pd.to_numeric(series, errors="coerce")
    if parsed.isna().any():
        raise RowParsingError(f"Numeric values in column '{column_name}' cannot be parsed.")
    return parsed
