from src.folder.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class FolderNotFound(NotFound):
    DETAIL = ErrorCode.FOLDER_NOT_FOUND


class FolderNameTaken(BadRequest):
    DETAIL = ErrorCode.FOLDER_NAME_TAKEN


class InvalidFolderAttrs(BadRequest):
    DETAIL = ErrorCode.FOLDER_INVALID_ATTRS

class SubfolderParentMismatch(BadRequest):
    DETAIL = ErrorCode.SUBFOLDER_PARENT_MISMATCH