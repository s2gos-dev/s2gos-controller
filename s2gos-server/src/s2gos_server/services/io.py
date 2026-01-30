import os

from pydantic import BaseModel, Field, model_validator, PrivateAttr
from upath import UPath


class Credential:
    def __init__(self, **upath_kwargs):
        self.upath_kwargs = upath_kwargs


def get_credential(cid: str) -> Credential:
    return Credential(cid=cid)


class PathRef(BaseModel):
    """
    Path configuration that preserves credential reference through serialization.

    This model allows paths to reference credentials by ID rather than embedding
    actual credentials. When serialized to JSON, only the path value and credential_id
    are stored (no actual credentials). When deserialized, credentials are resolved
    from the credential provider (environment variables or .secrets.yaml).

    Attributes:
        value: The actual path/URI
        cid: Optional reference to a Credential ID in the credential provider

    Example:
        # With credentials
        path = PathRef(
            path="https://data.earthdatahub.destine.eu/data.zarr",
            cid="earthdatahub"
        )

        # Without credentials (public or local path)
        path = PathRef("/local/path/data.zarr")

        # Access the authenticated UPath
        upath = path.upath
    """

    value: str = Field(description="Full path URI")
    # TODO : rename to credential id
    cid: str | None = Field(default=None, description="Credential ID")
    _upath: UPath | None = PrivateAttr(default=None)

    def __init__(self, value, cid=None, **kwargs):
        if isinstance(value, (UPath, os.PathLike)):
            path = str(value)
        elif isinstance(value, PathRef):
            path = value.value
            cid = value.cid
        elif isinstance(value, dict):
            path = value["value"]
            cid = value["cid"]
        else:
            path = value

        super(PathRef, self).__init__(value=path, cid=cid, **kwargs)

    @model_validator(mode="before")
    @classmethod
    def convert_to_pathref(cls, value):
        if isinstance(value, str):
            return {"value": value}

        elif isinstance(value, UPath):
            cid = value.storage_options.get("cid")
            return {"value": str(value), "cid": cid}

        return value

    @property
    def upath(self) -> UPath:
        """
        Get the authenticated UPath by resolving credentials.

        If `cid` is set, retrieves the credential from the credential
        provider and constructs an authenticated UPath. Otherwise, returns a
        simple UPath without authentication.

        Returns:
            UPath object with authentication if `cid` is set

        Raises:
            ValueError: If `cid` is set but credential is not found
        """
        if self._upath is not None:
            return self._upath

        if self.cid:
            # from s2gos_utils.setting.credentials import get_credential

            cred = get_credential(self.cid)
            if not cred:
                raise ValueError(
                    f"Credential '{self.cid}' not found. "
                    f"Set S2GOS_CRED_{self.cid}_* environment variables "
                    f"or add to .secrets.yaml"
                )
            kwargs = cred.upath_kwargs
            self._upath = UPath(self.value, **kwargs)
        else:
            # No credentials needed (local path or public URL)
            self._upath = UPath(self.value)

        return self._upath

    def to_dict(self) -> dict[str, str]:
        """Alias to `model_dump`."""
        return self.model_dump()

    def __truediv__(self, other) -> "PathRef":
        """Returns the joined UPath."""

        if isinstance(other, PathRef):
            if other.cid != self.cid:
                raise ValueError(
                    f"Joining paths with different credential ids! "
                    f"Left: {self.cid}, Right: {other.cid}."
                )
            other_path = other.upath
        else:
            other_path = other

        return PathRef(self.upath / other_path, self.cid)

    def __str__(self) -> str:
        """Return the path value as a string."""
        return self.value

    model_config = {"frozen": True}
