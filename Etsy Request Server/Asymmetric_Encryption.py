from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# USED BY LASER OMS. DO NOT DELETE

# Used to generate a public/private key pair and setup handshake


def GenerateKeyPair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024,
    )  # generate private key (1024 bit, the same size as a max length tcp packet)
    public_key = private_key.public_key()  # generate public key
    return private_key, public_key  # return both keys


def EncryptData(data, public_key):  # encrypt data with public key
    return public_key.encrypt(  # return encrypted data
        data,
        padding.OAEP(  # use OAEP padding
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # use SHA256 for MGF1
            algorithm=hashes.SHA256(),  # use SHA256 for OAEP
            label=None  # no label
        )
    )


def DecryptData(data, private_key):  # decrypt data with private key
    return private_key.decrypt(  # return decrypted
        data,  # data to decrypt
        padding.OAEP(  # use OAEP padding
            mgf=padding.MGF1(algorithm=hashes.SHA256()),  # use SHA256 for MGF1
            algorithm=hashes.SHA256(),  # use SHA256 for OAEP
            label=None  # no label
        )
    )
