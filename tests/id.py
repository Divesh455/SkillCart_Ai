from nanoid import generate
from pydantic import BaseModel, Field

def make_nano_id() -> str:
    # Generates an extremely secure 8-character string ID
    return generate(size=8)

class User(BaseModel):
    id: str = Field(default_factory=make_nano_id)
    username: str

print(User(username="Sam").id)  # Output: 'V1StGpx8'
