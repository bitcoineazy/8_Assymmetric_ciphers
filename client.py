import socket
import random
import pickle


def caesar_encryption(mes, k):
    return [chr((ord(i) + k) % 65536) for i in mes]


def caesar_decryption(mes, k):
    return [chr((65536 + (ord(i) - k) % 65536) % 65536) for i in mes]


class Cryptographer:
    def __init__(self, g=11, p=50, rmin=1, rmax=10):
        self.g = g
        self.p = p
        self.secret_key = random.randint(rmin, rmax)

    def create_open_key(self):
        """Создает открытый ключ"""
        self.open_key = (self.g ** self.secret_key) % self.p
        return self.open_key, self.g, self.p

    def decrypt(self, B):
        """Получает общий секретный ключ K"""
        return B ** self.secret_key % self.p

    def create_shared_key(self, A, g, p):
        """Получает внешний открытый ключ, создает свой открытый ключ, а также обший секретный
        :return B, K
        """
        return g ** self.secret_key % p, A ** self.secret_key % p


cryptographer = Cryptographer()

ip = 'localhost'
port = 9090
sock = socket.socket()
sock.connect((ip, port))
print(f'---\nConnect to server\nip: {ip}\nport: {port}')

sock.send(pickle.dumps(["open_key", cryptographer.create_open_key()]))
print(f'Send open key: {cryptographer.create_open_key()}')

data = sock.recv(1024)
data = pickle.loads(data)
print(f'Get Server open key: {data[1]}')

if data[0] == 'open_key':
    open_key = data[1]
    shared_key_client = cryptographer.decrypt(data[2])
print(f'Create SharedKeyClient: {cryptographer.decrypt(data[2])}\n---')

while True:

    mesout = input('>')

    (B, K) = cryptographer.create_shared_key(*open_key)
    data = ["", caesar_encryption(caesar_encryption(mesout, shared_key_client), K), B]
    print(f'Send cipher: {data[1]}')
    sock.send(pickle.dumps(data))
    print(f'---')

    if "exit" in mesout.lower():
        sock.close()
        exit()

    data = sock.recv(1024)
    data = pickle.loads(data)
    mesin = data[1]
    print(f'Get message: {mesin}')
    print(f'Encryption')
    mesin = 'Server: ' + ''.join(caesar_encryption(caesar_encryption(mesin, shared_key_client), K))
    print(mesin)
    print(f'---')
    if "exit" in mesin.lower():
        sock.close()
        exit()
