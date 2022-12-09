import os

ENV = os.getenv("ENV") or "dev"
assert ENV in ["dev", "test", "prod"]
