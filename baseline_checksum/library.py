import sha3

def keccak_256(input: bytearray):
    k = sha3.keccak_256()
    k.update(input)
    return bytearray.fromhex(k.hexdigest())

