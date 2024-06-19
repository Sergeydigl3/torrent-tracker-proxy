import urllib



info_hash = "ce4cea695eacebbeb3c90c9f66a1dca295c6f966"

# Note that all binary data in the URL (particularly info_hash and peer_id) must be properly escaped. This means any byte not in the set 0-9, a-z, A-Z, '.', '-', '_' and '~', must be encoded using the "%nn" format, where nn is the hexadecimal value of the byte. (See RFC1738 for details.)
#
# For a 20-byte hash of \x12\x34\x56\x78\x9a\xbc\xde\xf1\x23\x45\x67\x89\xab\xcd\xef\x12\x34\x56\x78\x9a,
# The right encoded form is %124Vx%9A%BC%DE%F1%23Eg%89%AB%CD%EF%124Vx%9A

def urlencode(info_hash):
    represented_info_hash_as_bytes = bytes.fromhex(info_hash)
    # if bytes are not in the set 0-9, a-z, A-Z, '.', '-', '_' and '~', must be encoded using the "%nn" format, where nn is the hexadecimal value of the byte.
    # (See RFC1738 for details.)
    return str(urllib.parse.quote(represented_info_hash_as_bytes))


print(urlencode(info_hash))

def urldecode(encoded_info_hash):
    return urllib.parse.unquote_to_bytes(encoded_info_hash).hex()
def custom_qs_parse(query_string):
    parts = query_string.split('&')
    parsed = {}
    print(parts)
    for part in parts:
        key, value = part.split('=')
        parsed[key] = value
    return parsed

# %ceL%eai%5e%ac%eb%be%b3%c9%0c%9ff%a1%dc%a2%95%c6%f9f
# %cel%eai%5e%ac%eb%be%b3%c9%0c%9ff%a1%dc%a2%95%c6%f9f


test_hash = "ce4cea695eacebbeb3c90c9f66a1dca295c6f966"
enc = urlencode(test_hash)
print(enc)

# %25CEL%25EAi%255E%25AC%25EB%25BE%25B3%25C9%250C%259Ff%25A1%25DC%25A2%2595%25C6%25F9f
# %CEL%EAi%5E%AC%EB%BE%B3%C9%0C%9Ff%A1%DC%A2%95%C6%F9f