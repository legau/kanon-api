# Starlette quote monkey patching. See https://github.com/encode/starlette/issues/1162

from urllib.parse import quote

from starlette import responses

responses.quote_plus = quote
