class ParsingError(Exception):
    pass


class MediaTypeValueError(ParsingError):
    pass


class SubtypeValueError(ParsingError):
    pass
