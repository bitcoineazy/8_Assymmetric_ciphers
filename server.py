import random
import pickle
import socket
import time


def caesar_encryption(mes, k):
    return [chr((ord(i) + k) % 65536) for i in mes]


def caesar_decryption(mes, k):
    return [chr((65536 + (ord(i) - k) % 65536) % 65536) for i in mes]


class Cryptographer:
    def __init__(self, g=12, p=80, rmin=1, rmax=10):
        self.g = g
        self.p = p
        self.secret_key = random.randint(rmin, rmax)

    def create_open_key(self):
        """Создает секретный ключ"""
        self.open_key = self.g ** self.secret_key % self.p
        return self.open_key, self.g, self.p

    def decrypt(self, B):
        """Получает общий секретный ключ K"""
        return B ** self.secret_key % self.p

    def create_shared_key(self, A, g, p):
        """Получает внешний открытый ключ, создает свой открытый ключ, а также обший секретный"""
        return g ** self.secret_key % p, A ** self.secret_key % p


cryptographer = Cryptographer()
sock = socket.socket()
print(f'---\nStart Server')
ip = ''
port = 9090
sock.bind((ip, port))
print(f'Open socket\nip: {ip}\nport: {port}')

sock.listen(1)
print(f'Listening socket')

conn, addr = sock.accept()
print(f'Accept new connection\nconn: {conn}\naddress: {addr}')

data = conn.recv(1024)
data = pickle.loads(data)
if data[0] == 'open_key':
    open_key = data[1]
print(f'Get Client open key: {open_key}')

(B, K) = cryptographer.create_shared_key(*open_key)
shared_key_client = K
conn.send(pickle.dumps(["open_key", cryptographer.create_open_key(), B]))
print(f'Send Server open key: {cryptographer.create_open_key()}\n---')

while True:
    data = conn.recv(1024)
    get_time = time.localtime()
    data = pickle.loads(data)
    K = cryptographer.decrypt(data[2])
    mesin = data[1]
    print(f'Получено: {mesin}')
    print(f'Encryption')
    mesin = ''.join(caesar_decryption(caesar_decryption(mesin, K), shared_key_client))
    print(mesin)
    print(f'---')
    if "exit" in mesin.lower():
        conn.close()
        exit()

    mesout = f'{time.strftime("%d %m %Y %H:%M:%S", get_time)} :: Client {addr} send message :: {mesin}'
    data = ["message", caesar_encryption(caesar_encryption(mesout, K), shared_key_client)]

    conn.send(pickle.dumps(data))
    print(f"Send message {mesout}\n---")
    if "exit" in mesout.lower():
        conn.close()
        exit()
