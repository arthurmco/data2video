from reedsolo import RSCodec
import logging

def get_ecc_data_symbol_count(block_width: int, block_height: int):
    return 64 # max(1920//block_width * 1088//block_height // 16, 16)

def get_ecc_metadata_symbol_count():
    return 4

def ecc_encode_data(bw: int, bh: int, data: bytes) -> bytes:
    symcount = min(len(data), get_ecc_data_symbol_count(bw, bh))
    logging.info(f"reed solomon encode symcount is {symcount}")
    
    rsc = RSCodec(symcount)
    return rsc.encode(data)

def ecc_encode_metadata(metadata: bytes) -> bytes:
    rsc = RSCodec(get_ecc_metadata_symbol_count())
    return rsc.encode(metadata)

def ecc_decode_data(bw: int, bh: int, data: bytes) -> bytes:
    datasize = len(data)
    eccsize = get_ecc_data_symbol_count(bw, bh)
    if datasize // 2 <= eccsize:
        symcount = datasize // 2
    else:
        symcount = eccsize

    logging.info(f"reed solomon decode symcount is {symcount}")
    
    rsc = RSCodec(symcount)
    return rsc.decode(data)[0]

def ecc_decode_metadata(metadata: bytes) -> bytes:
    rsc = RSCodec(get_ecc_metadata_symbol_count())
    return rsc.decode(metadata)[0]
