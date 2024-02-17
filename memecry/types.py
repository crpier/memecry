from typing import TypeAlias

from relax.app import Request as BaseRequest

import memecry.schema

Request: TypeAlias = BaseRequest[memecry.schema.UserRead]
