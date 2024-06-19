import struct
import socket
from typing import List, Dict
from pydantic import BaseModel


class Peer(BaseModel):
    peer_id: str
    ip: str
    port: int
