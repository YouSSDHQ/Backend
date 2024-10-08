from typing import Dict, List, Union

from pydantic import BaseModel, Field
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


# Create a base class for declarative class definitions
class Base(DeclarativeBase, AsyncAttrs):
    pass


class BaseResponse(BaseModel):
    """
    Base response model for API responses.
    """

    # Message to return
    message: str = Field(
        ...,
        description="Message to return in the response",
        examples=["Data logged successfully!", "Error logging data!"],
    )


class ErrorResponse(BaseModel):
    """
    Model for errors, contained in `detail`
    """

    detail: str = Field(
        ...,
        description="Message explaining the error or containing the error code for support intervention",
    )
