import dotenv, os

dotenv.load_dotenv(".env")

announce_url_const = os.environ.get("ANNOUNCE_URL")
peer_id_const = os.environ.get("PEER_ID")
user_agent_tracker = os.environ.get("USER_AGENT_TRACKER")
fake_port = os.environ.get("FAKE_PORT")

use_proxy_trackers = bool(int(os.environ.get("USE_PROXY_TRACKERS", "0")))
http_proxy_trackers = os.environ.get("HTTP_PROXY_TRACKERS")
https_proxy_trackers = os.environ.get("HTTPS_PROXY_TRACKERS")
