from .literals import MATCH_ALL_VALUES


def get_match_all_value(value):
    if value is not None:
        return value.lower() in MATCH_ALL_VALUES
