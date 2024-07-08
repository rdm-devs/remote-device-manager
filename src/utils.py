from typing import TypeVar
from fastapi_pagination import Page
from fastapi_pagination.customization import CustomizedPage, UseParamsFields


T = TypeVar("T")

BIG_PAGE_SIZE = 1_000_000
CustomBigPage = CustomizedPage[Page[T], UseParamsFields(size=BIG_PAGE_SIZE)]
