

from Crypto.Hash import CMAC
from Crypto.Cipher import AES
import base64
import time


from base58 import b58decode, b58encode


cmac_read = False
cmac_secret = b''
def get_serect():
    global cmac_read;
    global cmac_secret;
    if not cmac_read:
        cmac_read = True
        with open("cmac_secret.txt", "r") as f:
            cmac_secret = f.read().strip('\n').encode()
    return cmac_secret



def encrypt_token(ts,qq_num,cmac_secret):
    """
    :param ts: current timestamp
    :param qq_num: QQ Number
    :param cmac_secret:
    :return: encoded token in string format
    """
    qq_byte = int.to_bytes(int(qq_num), 8, 'little')
    ts_byte = int.to_bytes(int(ts), 4, 'little')
    ts_qq_join = b''.join([ts_byte,qq_byte])
    cobj = CMAC.new(cmac_secret, ciphermod=AES)
    cobj.update(ts_qq_join)
    print(cobj.digest())
    encode_byte = b''.join([ts_byte,cobj.digest()])
    return b58encode(encode_byte).decode("utf-8")

def decode_and_verify(token,ts,ts_tolerance,qq_num,cmac_secret):
    """
    :param token: received token
    :param ts: current timestamp
    :param ts_tolerance: tolerance of timestamp in second
    :param qq_num: QQ number
    :param cmac_secret:
    :return: if true -> verified; if false -> unverified
    """
    decode_byte = b58decode(token)
    token_ts = int.from_bytes(decode_byte[0:4],'little')
    if int(ts) - token_ts < ts_tolerance:
        token_mac = decode_byte[4:20]
        qq_byte = int.to_bytes(int(qq_num), 8, 'little')
        token_ts_byte = int.to_bytes(int(token_ts), 4, 'little')
        ts_qq_join = b''.join([token_ts_byte,qq_byte])
        cobj = CMAC.new(cmac_secret, ciphermod=AES)
        cobj.update(ts_qq_join)
        if token_mac == cobj.digest():
            return True
    else:
        return False


def verify(Token, qqid):
    return decode_and_verify(Token, time.time(), 3600, qqid, get_serect())
