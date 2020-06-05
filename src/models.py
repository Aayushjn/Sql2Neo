from typing import Optional


class Attribute:
    """
    Models an SQL table's attribute along with its constraints and other data
    """
    def __init__(self, name: str, index: bool = False, unique: bool = False, foreign_key: Optional[str] = None):
        self.name = name
        self.index = index
        self.unique = unique
        self.foreign_key = foreign_key
