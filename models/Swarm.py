import struct
import socket
from typing import List, Dict
from models.Peer import Peer
from models.TrackerClient import TrackerClient
class Swarm:
    def __init__(self, enable_proxy_peers: bool = False):
        self.peers: Dict[str, Peer] = {}

        self.proxy_client = None

        if enable_proxy_peers:
            self.proxy_client = TrackerClient()

    def add_peer(self, peer: Peer):
        self.peers[peer.peer_id] = peer

    def remove_peer(self, peer_id: str):
        if peer_id in self.peers:
            del self.peers[peer_id]

    def get_peers(self, numwant: int = 50, compact: int = 0) -> List[Dict]:
        peers = list(self.peers.values())
        if self.proxy_client:
            peers.extend(self.proxy_client.peers)
        if compact:
            return b''.join([socket.inet_aton(p.ip) + struct.pack('!H', p.port) for p in peers[:numwant]])
        else:
            return [{'peer id': peer.peer_id, 'ip': peer.ip, 'port': peer.port} for peer in peers[:numwant]]