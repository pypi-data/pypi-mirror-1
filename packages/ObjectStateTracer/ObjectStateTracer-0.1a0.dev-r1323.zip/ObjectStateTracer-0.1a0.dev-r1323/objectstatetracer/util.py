from sqlobject import SQLObject

from datetime import date, datetime

__all__ = ['normalize_values']

def normalize_values(old_value, new_value):
    """
    This function attempts to normalize data so that old_value and new_value
    are the same type. 
    It's needed because, for example, if a datetime is assigned to a date
    column the old_value == new_value condition would yield False.
    The goal isn't to pass the data through SO validators but just to fix
    the needed cases.
    """
    if isinstance(old_value, SQLObject):
        old_value = old_value.id
    if isinstance(new_value, SQLObject):
        new_value = new_value.id
    if isinstance(old_value, date) and isinstance(new_value, datetime):
        new_value = new_value.date()
    return (old_value, new_value)

