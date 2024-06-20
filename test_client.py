import time

from config import announce_url_const, peer_id_const, fake_port
from models import TrackerClient

info_hash = "26ee74d6aafcc563458c56457a38844cfe5b95f1"
trackerClient = TrackerClient(
    announce_url_const,
    info_hash,
    peer_id_const,
    left=818119347,
    port=fake_port
)

trackerClient.start_background_update()
time.sleep(5)
peers = trackerClient.get_peers()
print(peers)
trackerClient.stop_background_update()
time.sleep(2)