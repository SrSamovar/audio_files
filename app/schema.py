from pydantic import BaseModel


class ItemResponse(BaseModel):
    id: int


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: str | None = None


class UserUpdateResponse(ItemResponse):
    pass

class GetUserResponse(BaseModel):
    id: int
    name: str
    email: str


class GetAudioFileResponse(BaseModel):
    id: int
    filename: str
    file_path: str
