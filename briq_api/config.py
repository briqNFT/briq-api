import os
from typing import Literal, NewType, cast

ENV_VAR = Literal["dev", "test", "prod"]

ENV: ENV_VAR
ENV = cast(ENV_VAR, os.getenv("ENV")) or "dev"
assert ENV in ["dev", "test", "prod"]
