"""
Helper functions for validation purpose
"""

from typing import List


# --------------------- INPUT VALIDATION -------------------- #
class ValidationError(BaseException):

    def __init__(self, message: str):
        self.message = message
        super(ValidationError, self).__init__(message)


def require_in_list(item, valid_items: List):
    if item not in valid_items:
        failure_message = f"Item '{item}' not in valid items list: {', '.join(valid_items)}"
        raise ValidationError(message=failure_message)


# --------------------- INPUT PARSING -------------------- #
def format_input_to_list(item_to_format):

    if not isinstance(item_to_format, list):
        item_to_format = [item_to_format]

    return item_to_format


def format_input_to_type(item_to_format, target_type):

    if not isinstance(item_to_format, target_type):
        item_to_format = target_type(item_to_format)

    return item_to_format
