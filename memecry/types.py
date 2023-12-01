from typing import TypeAlias

from relax.app import Request as BaseRequest

from memecry.schema import UserRead

Request: TypeAlias = BaseRequest[UserRead]
