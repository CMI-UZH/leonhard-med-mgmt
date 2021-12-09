"""
Author: @matteobe
"""

from typing import List, Dict


def replace_by_dict(values: List[str], replace: Dict[str, str]) -> List[str]:
    """
    Replace the text in the values list according to the dictionary stating search string and corresponding substitution
    """

    for substring, replacement in replace.items():
        values = [item.replace(substring, replacement) for item in values]

    return values
