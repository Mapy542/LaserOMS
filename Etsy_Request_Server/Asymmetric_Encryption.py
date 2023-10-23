import cryptography.hazmat.primitives.serialization as serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

import socket

# USED BY LASER OMS. DO NOT DELETE


def BufferSize():  # return buffer size
    return 2048  # return buffer size
    # 1024 bit ran at 3.4 secs for a 44 order request
    # 2048 bit ran at 2.8 secs for a 44 order request
    # 4096 bit ran at 7.5 secs for a 44 order request whyyyyyy rsa


def MaxStringLen():
    return (int(BufferSize() / 8) - 42) - 30  # additional safety factor


# Used to generate a public/private key pair and communication.
def GenerateKeyPair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=BufferSize(),
    )  # generate private key (BufferSize() bit, the same size as a max length tcp packet)
    public_key = private_key.public_key()  # generate public key
    return private_key, public_key  # return both keys


def EncryptData(data, public_key):  # encrypt data with public key
    return public_key.encrypt(  # return encrypted data
        data,
        padding.OAEP(  # use OAEP padding
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # use SHA256 for MGF1
            algorithm=hashes.SHA256(),  # use SHA256 for OAEP
            label=None,  # no label
        ),
    )


def DecryptData(data, private_key):  # decrypt data with private key
    if data == b"":  # if data is empty (no data to decrypt)
        return b""  # returns blank for other code to handle rather than error
        # chucksendcheck handles this, but regular recv does not
    return private_key.decrypt(  # return decrypted
        data,  # data to decrypt
        padding.OAEP(  # use OAEP padding
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # use SHA256 for MGF1
            algorithm=hashes.SHA256(),  # use SHA256 for OAEP
            label=None,  # no label
        ),
    )


def PublicKeyToBytes(public_key):  # return public key in bytes for transmission
    return public_key.public_bytes(  # return public key in bytes
        encoding=serialization.Encoding.PEM,  # use PEM encoding
        # use SubjectPublicKeyInfo format
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def LoadPublicKey(public_key):  # load public key from bytes into a public key object
    return serialization.load_pem_public_key(  # return public key
        public_key, backend=None  # public key in bytes  # use default backend
    )


def EnsureSend(socket, public_key = None, data):  # ensure data is sent in full
    if public_key == None: # if no public key is provided send data as is
        while True:
            socket.sendall(b"")

class ConnectionRole:  # Role class for server/client roles
    RoleTypes = ["Server", "Client"]

    def __init__(self, Role="Client"):
        if Role in Role.RoleTypes:
            self.Role = Role
        else:
            raise Exception("Role must be either 'Server' or 'Client'")

    def __str__(self):
        return self.Role


def ConnectionThread(TransmissionStack, ReceptionStack, Socket, Role=ConnectionRole("Client")):
    """A secure connection thread for a client or server.

    Args:
        TransmissionStack (List): A list of data to be continuously sent.
            [UID, Response UID, Data]
            Send items are removed from the list after being sent.
        ReceptionStack (List): A list of responses being continuously sent.
            [Status Code, UID, Response UID, Data]
            Follows http status code rules.
        Socket (Python Socket Object): The socket to send and receive data on.
        Role (ConnectionRole Object, optional): Defines the role of the connection thread.
            Defaults to ConnectionRole('Client').
            Servers can only respond to requests, and must provide a Response UID.
    """
    if TransmissionStack.__class__ != list:
        raise Exception("TransmissionStack must be a list")
    if ReceptionStack.__class__ != list:
        raise Exception("ReceptionStack must be a list")
    if Socket.__class__ != socket.socket:
        raise Exception("Socket must be a socket object")
    
    PrivateKey, PublicKey = GenerateKeyPair()  # generate key pair

    while True: #authentication handshake

