import copy
import socket
import struct
import threading
import time
import random
import urllib.parse

import niquests

from utils import urlencode
from models import Peer

from bencodepy import decode, encode


class TrackerClient:
    def __init__(self, announce_url, info_hash, peer_id, left, port=0, interval=3048, proxies={}):
        self.announce_url = f"{announce_url}?info_hash={urlencode(info_hash)}"
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.left = left
        self.port = port
        self.interval = interval
        self.peers = []
        self.__lock = threading.Lock()
        self.__thread = None
        self.__disable_event = threading.Event()

        self.__disable_event.set()

        if port == 0:
            self.port = random.randint(10000, 60000)

        self.__session = niquests.Session(resolver="doh+google://", disable_http3=True, disable_ipv6=True,
                                          disable_http2=True)

        if proxies:
            self.__session.proxies = proxies

        self.__headers = {
            'User-Agent': 'qBittorrent/4.6.4',
            'Accept-Encoding': 'gzip',
            'Connection': 'close',
        }

    def start_background_update(self):
        if not self.__disable_event.is_set(): return
        self.__disable_event.clear()

        self.__thread = threading.Thread(target=self.__thread_loop)
        self.__thread.start()

    def stop_background_update(self):
        if self.__disable_event.is_set():
            return

        self.__disable_event.set()
        self.__thread.join()

    def __thread_loop(self):
        try:
            while not self.__disable_event.is_set():
                self.__announce()
                if self.__disable_event.wait(self.interval): break
        except Exception as e:
            print(e)
        self.__enabled_loop = False

    def __announce(self):
        try:
            response = self.__session.get(self.announce_url, headers=self.__headers, params=self.__get_qs())

            response_bencode = decode(response.content)
            print(response_bencode)
            peers_binary = response_bencode.get(b'peers', [])
            temp_peers = []
            for i in range(0, len(peers_binary), 6):
                ip = socket.inet_ntoa(peers_binary[i:i + 4])
                port = struct.unpack('!H', peers_binary[i + 4:i + 6])[0]
                peer = Peer(peer_id="proxy", ip=ip, port=port)
                temp_peers.append(peer)

            with self.__lock:
                self.peers = temp_peers
                self.interval = response_bencode.get(b'interval', 0)
        except Exception as e:
            print(e)

    def __stop_announce(self):
        try:
            self.__session.get(self.announce_url, headers=self.__headers, params=self.__get_qs('stopped'))
        except Exception as e:
            print(e)

    def get_peers(self):
        with self.__lock:
            response = copy.deepcopy(self.peers)
        return response

    def close(self):
        self.stop_background_update()
        self.__stop_announce()
        self.__session.close()

    def __get_qs(self, event='started'):
        return {
            'peer_id': self.peer_id,
            'port': self.port,
            'uploaded': 0,
            'downloaded': 0,
            'left': self.left,
            'corrupt': 0,
            'event': event,
            'numwant': 200,
            'compact': 1,
            'no_peer_id': 1,
            'supportcrypto': 0,
        }


if __name__ == '__main__':
    announce_url = "http://127.0.0.1:8000/announce"
    info_hash = "ce4cea695eacebbeb3c90c9f66a1dca295c6f966"
    peer_id = "-qB4640-BVapQU_4a62Ar"
    trackerClient = TrackerClient(
        announce_url,
        info_hash,
        peer_id,
        left=818119347,
    )

    trackerClient.announce()
    time.sleep(5)
    trackerClient.close()
    time.sleep(2)
