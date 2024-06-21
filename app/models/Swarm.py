import socket
import struct
from typing import List, Dict

from config import announce_url_const, peer_id_const
from models.Peer import Peer
from models.TrackerClient import TrackerClient


class Swarm:
    def __init__(self, info_hash: str, enable_proxy_peers: bool = False, total_left_count: int = 0):
        self.peers: Dict[str, Peer] = {}

        self.proxy_client = None

        if enable_proxy_peers:
            self.proxy_client = TrackerClient(announce_url_const, info_hash, peer_id_const, left=total_left_count)
            self.proxy_client.start_background_update()

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

    def get_proxy_complete_incomplete(self):
        if self.proxy_client:
            return self.proxy_client.complete_incomplete
        else:
            return (0, 0)

    def __del__(self):
        if self.proxy_client:
            self.proxy_client.close()