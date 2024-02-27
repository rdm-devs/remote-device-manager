from src.folder.constants import ErrorCode
from src.exceptions import NotFound, BadRequest


class FolderNotFoundError(NotFound):
    DETAIL = ErrorCode.FOLDER_NOT_FOUND


class FolderNameTakenError(BadRequest):
    DETAIL = ErrorCode.FOLDER_NAME_TAKEN


class InvalidFolderAttrsError(BadRequest):
    DETAIL = ErrorCode.FOLDER_INVALID_ATTRS

class SubfolderParentMismatchError(BadRequest):
    DETAIL = ErrorCode.SUBFOLDER_PARENT_MISMATCH