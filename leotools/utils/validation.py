"""
Helper functions for validation purpose
"""

from typing import List, Dict

from cerberus import Validator


# --------------------- INPUT VALIDATION -------------------- #
class ValidationError(BaseException):

    def __init__(self, message: str):
        self.message = message
        super(ValidationError, self).__init__(message)


def require_in_list(item, valid_items: List):
    if item not in valid_items:
        failure_message = f"Item '{item}' not in valid items list: {', '.join(valid_items)}"
        raise ValidationError(message=failure_message)


def validate_schema(document: Dict, schema: Dict, allow_unknown: bool = False, require_all: bool = True) \
        -> Dict:
    """
    Validate a document (usually a Python dictionary object against) against a predefined schema.
    Can be used to validate configuration dictionaries, or data formats.

    Args:
        document (dict): a dictionary object containing the document to be validated
        schema (dict): a schema, defined according to the 'cerberus' library, which defines which keys are expected
            in the document and what type they can be
        allow_unknown (bool): allow for unknown keys in the document. Default is False
        require_all (bool): require all keys to be present. Default is True
    """

    v = Validator(allow_unknow=allow_unknown, require_all=require_all)
    normalized_document = v.normalized(document=document, schema=schema)

    if not v.validate(document=normalized_document, schema=schema):
        raise ValidationError(f"Document is invalid according to the pre-defined schema."
                              f"The following errors where detected: {v.errors}")

    return normalized_document


# --------------------- INPUT PARSING -------------------- #
def format_input_to_list(item_to_format):

    if not isinstance(item_to_format, list):
        item_to_format = [item_to_format]

    return item_to_format


def format_input_to_type(item_to_format, target_type):

    if not isinstance(item_to_format, target_type):
        item_to_format = target_type(item_to_format)

    return item_to_format
