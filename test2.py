import urllib.parse

# Исходный запрос
query = "info_hash=%ceL%eai%5e%ac%eb%be%b3%c9%0c%9ff%a1%dc%a2%95%c6%f9f&peer_id=-qB4640-BVapQU_9a3%2Ar&port=35068&uploaded=0&downloaded=0&left=818119347&corrupt=0&key=3973D051&numwant=200&compact=1&no_peer_id=1&supportcrypto=1&redundant=0"

# Парсинг строки запроса в словарь
parsed_query = urllib.parse.parse_qs(query)

# Корректная декодировка info_hash
info_hash = parsed_query['info_hash'][0]
decoded_info_hash = urllib.parse.unquote_to_bytes(info_hash)

# Обработка остальных параметров
parameters = {key: value[0] for key, value in parsed_query.items()}
parameters['info_hash'] = decoded_info_hash

print(parameters)
