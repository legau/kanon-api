# Starlette quote monkey patching. See https://github.com/encode/starlette/issues/1162

from urllib.parse import quote

from kanon.tables import HTable
from starlette import responses

_to_pandas = HTable.to_pandas


def to_pandas(self: HTable, *args, **kwargs):
    if not hasattr(self, "cached_to_pandas"):
        self.cached_to_pandas = _to_pandas(self, *args, **kwargs)
    return self.cached_to_pandas


HTable.to_pandas = to_pandas  # type: ignore

responses.quote_plus = quote
