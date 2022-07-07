from enum import Enum, EnumMeta

from .table_classes import TableSet


class KeyEnumMeta(EnumMeta):
    def __call__(
        cls, value, names=None, *, module=None, qualname=None, type=None, start=1
    ):
        if isinstance(value, str):
            return getattr(cls, value)
        return super().__call__(  # pragma: no cover
            cls,
            value,
            names=names,
            module=module,
            qualname=qualname,
            type=type,
            start=start,
        )


class TableSets(TableSet, Enum, metaclass=KeyEnumMeta):
    parisian_alphonsine_tables = "parisian_alphonsine_tables.json"

    @property
    def value(self):
        return self.name
