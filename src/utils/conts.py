from enum import IntEnum, StrEnum


class ViewAction(StrEnum):
    LIST = "list"
    CREATE = "create"
    RETRIEVE = "retrieve"
    UPDATE = "update"
    PARTIAL_UPDATE = "partial_update"
    DESTROY = "destroy"


API_VERSION = "v1"

API_CONST = "api"

PREFIX_API_VERSION = f"{API_CONST}/{API_VERSION}"


class NotifcationType(IntEnum):
    POST_LIKED = 1
