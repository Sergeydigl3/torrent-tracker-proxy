import socket
import struct
import urllib
from typing import List, Dict

import uvicorn
from bencodepy import encode
from fastapi import FastAPI, Request, HTTPException, Response, Query
from pydantic import BaseModel

app = FastAPI()

from utils import custom_qs_parse, urldecode

from models import Peer, Swarm

swarms: Dict[str, Swarm] = {}


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

    info_hash = urldecode(custom_qs_parse(str(request.url.query))["info_hash"])
    print(info_hash)
    # info_hash = unquote_to_bytes(info_hash).hex().decode('utf-8')

    # print info hash as hex
    # info_hash = info_hash.encode('utf-8')
    if not info_hash or not peer_id or not port:
        raise HTTPException(status_code=400, detail="Missing required parameters")

    if info_hash not in swarms:
        swarms[info_hash] = Swarm()

    swarm = swarms[info_hash]
    peer = Peer(peer_id=peer_id, ip=ip, port=port)

    if event == "started":
        swarm.add_peer(peer)
    elif event == "stopped":
        swarm.remove_peer(peer_id)

    peers = swarm.get_peers(numwant, compact)
    response = {
        "interval": 30,
        "complete": 0,  # This tracker does not currently distinguish complete/incomplete
        "incomplete": len(swarm.peers),
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)