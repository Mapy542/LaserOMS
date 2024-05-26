import cryptography.hazmat.primitives.serialization as serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# USED BY LASER OMS. DO NOT DELETE


def BufferSize():  # return buffer size
    """Static RSA buffer size for encryption and decryption.

    Returns:
        int: The buffer size for RSA encryption and decryption.
    """
    return 2048  # return buffer size
    # 1024 bit ran at 3.4 secs for a 44 order request
    # 2048 bit ran at 2.8 secs for a 44 order request happy medium
    # 4096 bit ran at 7.5 secs for a 44 order request


def MaxStringLen():
    """Calculate the maximum string length that can be sent in a single packet.

    Returns:
        int: The maximum string length that can be sent in a single packet.
    """
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


def SendablePublicKey(public_key):  # return public key in bytes for transmission
    return public_key.public_bytes(  # return public key in bytes
        encoding=serialization.Encoding.PEM,  # use PEM encoding
        # use SubjectPublicKeyInfo format
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def LoadPublicKey(public_key):  # load public key from bytes into a public key object
    return serialization.load_pem_public_key(  # return public key
        public_key, backend=None  # public key in bytes  # use default backend
    )


def ClientHandshake(socket, PublicKey, PrivateKey):
    try:
        socket.sendall(b"InitiateHandshake")  # send handshake request
        data = socket.recv(BufferSize())  # receive public key

        ServerKey = LoadPublicKey(data)  # load public key from received bytes
        socket.sendall(SendablePublicKey(PublicKey))  # send public key

        test = socket.recv(BufferSize())  # receive handshake complete
        if not DecryptData(test, PrivateKey) == b"HandshakeComplete":
            # if handshake failed or server is not listening
            socket.sendall(EncryptData(b"CANCEL", ServerKey))
            return False, None
        else:
            socket.sendall(EncryptData(b"HandshakeCompleteAcknowledged", ServerKey))

        data = socket.recv(BufferSize())  # receive data
        # if handshake failed or server is not listening
        if not DecryptData(data, PrivateKey) == b"Listening":
            socket.sendall(EncryptData(b"CANCEL", ServerKey))
            return False, None

        else:
            return True, ServerKey

    except:
        return False, None


def StringToBytes(string):  # convert string to bytes for transmission
    return string.encode("utf-8")


def BytesToString(bytes):  # convert bytes to string for use
    return bytes.decode("utf-8")


def ChopSendCheck(string, socket, ClientKey, PrivateKey):
    """ChopSendCheck for the client, sends an arbitrary length string to the server in chunks.

    Args:
        string (String): The string to send to the server.
        socket (TCP Socket Connection): The socket connection to the server.
        ClientKey (RSA Public Key): The public key of the server.
        PrivateKey (RSA Private Key): The private key of the client.

    Returns:
        bool: True if the ChopSendCheck was successful, False otherwise.
    """
    # chop string into MaxStringLen() byte chunks and send to client (86 is the theoretical max length of a tcp packet with encryption and padding)
    chunks = [string[i : i + MaxStringLen()] for i in range(0, len(string), MaxStringLen())]

    socket.sendall(EncryptData(b"ChopSendCheckStart", ClientKey))  # send chop send check start

    # receive chop send check start
    data = DecryptData(socket.recv(BufferSize()), PrivateKey)

    if not data == b"ChopSendCheckAcknowledged":
        return False  # chop send check failed

    for i in range(len(chunks)):
        socket.sendall(EncryptData(StringToBytes(chunks[i]), ClientKey))

    socket.sendall(EncryptData(b"ChopSendCheckComplete", ClientKey))
    data = DecryptData(socket.recv(BufferSize()), PrivateKey)
    if not data == b"ChopSendCheckCompleteAcknowledged":
        return False  # chop send check failed

    return True  # chop send check complete


def ChopReceiveCheck(socket, ClientKey, PrivateKey):
    """ChopReceiveCheck for the client, receives an arbitrary length string from the server in chunks.

    Args:
        socket (TCP Socket Connection): The socket connection to the server.
        ClientKey (RSA Public Key): The public key of the server.
        PrivateKey (RSA Private Key): The private key of the client.

    Returns:
        String: The string received from the server. May be empty if no data was received, or if the ChopReceiveCheck failed.
    """
    # receive chop send check start
    data = DecryptData(socket.recv(BufferSize()), PrivateKey)
    if not data == b"ChopSendCheckStart":  # check if chop send check start was received correctly
        return False
    socket.sendall(
        EncryptData(b"ChopSendCheckAcknowledged", ClientKey)  # send chop send check acknowledged
    )
    chunks = []
    while True:  # receive chunks
        RawData = socket.recv(BufferSize())
        data = DecryptData(RawData, PrivateKey)

        if (
            data == b"ChopSendCheckComplete"
        ):  # check if chop send check complete was received correctly
            socket.sendall(
                EncryptData(  # send chop send check complete acknowledged
                    b"ChopSendCheckCompleteAcknowledged", ClientKey
                )
            )
            break  # chop send check complete
    return "".join(chunks)
