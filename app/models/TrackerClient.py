from config import announce_url_const, peer_id_const, user_agent_tracker
from config import use_proxy_trackers, http_proxy_trackers, https_proxy_trackers

import copy
import random
import socket
import struct
import threading
import time

import niquests
from bencodepy import decode

from models import Peer
from utils import urlencode


proxy_pack = {
    'http': http_proxy_trackers,
    'https': https_proxy_trackers
}

class TrackerClient:
    def __init__(self, announce_url, info_hash, peer_id, left, port=0, interval=3048, proxies=None):
        # detect needed replacer & or ?
        replacer = '&' if '?' in announce_url else '?'
        self.announce_url = f"{announce_url}{replacer}info_hash={urlencode(info_hash)}"
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.left = left
        self.port = port
        self.interval = interval
        self.peers = []
        self.complete_incomplete = (0, 0)
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

        if use_proxy_trackers:
            self.__session.proxies = proxy_pack

        self.__headers = {
            'User-Agent': user_agent_tracker,
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
        self.__stop_announce()
        self.__disable_event.set()
        self.__thread.join()

    def __thread_loop(self):
        print(f"Starting background thread for {self.announce_url}")
        try:
            self.__announce(event="started")
            if not self.__disable_event.wait(self.interval):
                return
            while True:
                self.__announce()
                if self.__disable_event.wait(self.interval): break
        except Exception as e:
            print(e)

    def __announce(self, event=None):
        try:
            response = self.__session.get(self.announce_url, headers=self.__headers, params=self.__get_qs(event))

            response_bencode = decode(response.content)
            print("RESPONSE: ", response_bencode)
            peers_binary = response_bencode.get(b'peers', [])
            temp_peers = []
            index = 0
            for i in range(0, len(peers_binary), 6):
                ip = socket.inet_ntoa(peers_binary[i:i + 4])
                port = struct.unpack('!H', peers_binary[i + 4:i + 6])[0]

                # if port == self.port:
                #     continue

                peer = Peer(peer_id="proxy"+str(index), ip=ip, port=port)
                index += 1
                temp_peers.append(peer)
            complete = response_bencode.get(b'complete', 0)
            incomplete = response_bencode.get(b'incomplete', 0)
            self.complete_incomplete = (complete, incomplete)
            with self.__lock:
                print("Peers: ", temp_peers)
                self.peers = temp_peers
                self.interval = response_bencode.get(b'interval', 60)
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
        self.__session.close()

    def __get_qs(self, event='started'):
        qs = {
            'peer_id': self.peer_id,
            'port': self.port,
            'uploaded': 0,
            'downloaded': 0,
            'left': self.left,
            'corrupt': 0,
            'numwant': 200,
            'compact': 1,
            'no_peer_id': 1,
            'supportcrypto': 0,
        }
        if event:
            qs['event'] = event
        return qs
