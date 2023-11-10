from reedsolo import RSCodec

def get_ecc_data_symbol_count(block_width: int, block_height: int):
    return max(block_width * block_height // 16, 16)

def get_ecc_metadata_symbol_count():
    return 4

def ecc_encode_data(bw: int, bh: int, data: bytes) -> bytes:
    rsc = RSCodec(get_ecc_data_symbol_count(bw, bh))
    return rsc.encode(data)

def ecc_encode_metadata(metadata: bytes) -> bytes:
    rsc = RSCodec(get_ecc_metadata_symbol_count())
    return rsc.encode(metadata)

def ecc_decode_data(bw: int, bh: int, data: bytes) -> bytes:
    rsc = RSCodec(get_ecc_data_symbol_count(bw, bh))
    return rsc.decode(data)[0]

def ecc_decode_metadata(metadata: bytes) -> bytes:
    rsc = RSCodec(get_ecc_metadata_symbol_count())
    return rsc.decode(metadata)[0]
