import os
import hashlib
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend


class Cipher:
    def __init__(self, key: str, iv: bytes=None, cipher=Cipher, algorithm=algorithms.AES, mode=modes.CBC, padder=PKCS7, backend=default_backend()):
        self.key = hashlib.sha256(key.encode()).digest()  # string
        self.cipher = cipher
        self.algorithm = algorithm
        self.mode = mode
        self.iv = iv or os.urandom(16)  # bytes
        self.backend = backend
        self.padder = padder
        self.block_size = algorithm.block_size  # in bits
        self.separator = b':==:'

    def get_iv(self):
        return self.pad(self.iv)[:self.block_size // 8]

    def get_mode(self):
        return self.mode(self.get_iv())

    def get_algorithm(self):
        return self.algorithm(self.key)

    def get_backend(self):
        return self.backend

    def get_cipher(self):
        return self.cipher(self.get_algorithm(), self.get_mode(), backend=self.get_backend())

    def encrypt(self, message: str):
        padded_message = self.pad(message.encode())
        encryptor = self.get_cipher().encryptor()
        ct = encryptor.update(padded_message) + encryptor.finalize()
        iv_ct = self.get_iv() + self.separator + ct
        return urlsafe_b64encode(iv_ct).decode()

    def decrypt(self, ctstr: str):
        iv_ct = urlsafe_b64decode(ctstr.encode())
        self.iv, ct = iv_ct.split(self.separator)
        decryptor = self.get_cipher().decryptor()
        padded_message = decryptor.update(ct) + decryptor.finalize()
        message = self.unpad(padded_message)
        return message.decode()

    def pad(self, b):
        # bytes to bytes
        padder = self.padder(self.block_size).padder()
        padded_data = padder.update(b)
        padded_data += padder.finalize()
        return padded_data

    def unpad(self, b):
        # bytes to bytes
        unpadder = self.padder(self.block_size).unpadder()
        data = unpadder.update(b)
        data += unpadder.finalize()
        return data
