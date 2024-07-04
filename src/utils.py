from typing import TypeVar
from fastapi_pagination import Page
from fastapi_pagination.customization import CustomizedPage, UseParamsFields

T = TypeVar("T")

CustomBigPage = CustomizedPage[Page[T], UseParamsFields(size=1_000_000)]
