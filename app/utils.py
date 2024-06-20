# utils
import urllib

def urldecode(encoded_info_hash):
    return urllib.parse.unquote_to_bytes(encoded_info_hash).hex()

def urlencode(info_hash):
    represented_info_hash_as_bytes = bytes.fromhex(info_hash)
    # if bytes are not in the set 0-9, a-z, A-Z, '.', '-', '_' and '~', must be encoded using the "%nn" format, where nn is the hexadecimal value of the byte.
    # (See RFC1738 for details.)
    return str(urllib.parse.quote(represented_info_hash_as_bytes))

def custom_qs_parse(query_string):
    parts = query_string.split('&')
    parsed = {}
    # print(parts)
    for part in parts:
        key, value = part.split('=')
        parsed[key] = value
    return parsed