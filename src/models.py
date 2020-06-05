from typing import Optional


class AttributeData:
    """
    Models an SQL table's attribute along with its constraints and other data
    """
    def __init__(self, position: int, index: bool = False, unique: bool = False, foreign_key: Optional[str] = None):
        self.position = position
        self.index = index
        self.unique = unique
        self.foreign_key = foreign_key
