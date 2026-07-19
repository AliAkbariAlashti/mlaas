class MLEngineError(ValueError):
    """Base error for input data that cannot be analyzed."""


class EmptyColumnError(MLEngineError):
    pass


class RowParsingError(MLEngineError):
    pass
