from pydantic import BaseModel

from t2c_backend.utils.enums import Scheme


class ResolvedRef(BaseModel):
    """What the URL means, once parsed."""

    scheme: Scheme
    token: str  # the opaque per-asset id we actually look up on
    gtin: str | None = None  # present only for GTIN scheme (for integrity check)
