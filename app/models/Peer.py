from pydantic import BaseModel


class Peer(BaseModel):
    peer_id: str
    ip: str
    port: int
