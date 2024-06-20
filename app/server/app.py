import socket
import struct
import urllib
from typing import Dict
from bencodepy import encode
from fastapi import FastAPI, Request, HTTPException, Response, Query


from utils import custom_qs_parse, urldecode

from models import Peer, Swarm
from contextlib import asynccontextmanager

swarms: Dict[str, Swarm] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    swarms.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/announce")
async def announce(request: Request,
                   ):
    params = request.query_params
    peer_id = params.get("peer_id")
    port = int(params.get("port"))
    ip = request.client.host
    event = params.get("event")
    numwant = int(params.get("numwant", 50))
    compact = int(params.get("compact", 0))
    downloaded = int(params.get("downloaded", 0))
    left = int(params.get("left", 0))

    info_hash = urldecode(custom_qs_parse(str(request.url.query))["info_hash"])
    print(info_hash)


    # print info hash as hex
    # info_hash = info_hash.encode('utf-8')
    if not info_hash or not peer_id or not port:
        raise HTTPException(status_code=400, detail="Missing required parameters")

    if info_hash not in swarms:
        swarms[info_hash] = Swarm(info_hash, True, left-downloaded)

    swarm = swarms[info_hash]
    peer = Peer(peer_id=peer_id, ip=ip, port=port)

    if event == "started":
        swarm.add_peer(peer)
    elif event == "stopped":
        swarm.remove_peer(peer_id)
    complete, incomplete = swarm.get_proxy_complete_incomplete()
    peers = swarm.get_peers(numwant, compact)
    response = {
        "interval": 30,
        "complete": 0+complete,  # This tracker does not currently distinguish complete/incomplete
        "incomplete": len(swarm.peers)+incomplete,
        "peers": peers
    }

    content = encode(response)
    return Response(content=content, media_type="application/octet-stream")


@app.get("/stats")
async def stats():
    stats_html = """
    <html>
    <head>
        <title>Tracker Stats</title>
    </head>
    <body>
        <h1>Tracker Statistics</h1>
        <table border="1">
            <tr>
                <th>Info Hash</th>
                <th>Number of Peers</th>
                <th>Peers</th>
            </tr>
    """

    for info_hash, swarm in swarms.items():
        peers_info = "<br>".join([f"{peer.peer_id} - {peer.ip}:{peer.port}" for peer in swarm.peers.values()])
        stats_html += f"""
            <tr>
                <td>{info_hash}</td>
                <td>{len(swarm.peers)}</td>
                <td>{peers_info}</td>
            </tr>
        """

    stats_html += """
        </table>
    </body>
    </html>
    """

    return Response(content=stats_html, media_type="text/html")


