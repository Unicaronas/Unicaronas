from .base import BaseResult, BaseResultItem


class Result(BaseResult):
    """Results"""

    def __str__(self):
        return f"Result: ({len(self.items)} items)"

    def __repr__(self):
        return str(self)


class ResultItem(BaseResultItem):
    """Result item"""

    def __str__(self):
        return f"ResultItem: (dest '{self.destination[:10]}', ori '{self.origin[:10]}', dt '{self.datetime}', price '{self.price}')"

    def __repr__(self):
        return str(self)
