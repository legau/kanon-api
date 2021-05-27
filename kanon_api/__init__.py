# Starlette quote monkey patching. See https://github.com/encode/starlette/issues/1162

from urllib.parse import quote

from kanon.tables import HTable
from starlette import responses

_to_pandas = HTable.to_pandas
_init = HTable.__init__


def to_pandas(self: HTable, *args, **kwargs):
    return self.cached_to_pandas


def init(self: HTable, *args, **kwargs):
    _init(self, *args, **kwargs)
    self.cached_to_pandas = _to_pandas(self)


HTable.__init__ = init  # type: ignore
HTable.to_pandas = to_pandas  # type: ignore

responses.quote_plus = quote
