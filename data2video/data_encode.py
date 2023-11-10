from PIL import ImageDraw, Image
from typing import BinaryIO
import logging
import functools as f
import math as m

import struct as s
import numpy as np

from data2video.ecc import get_ecc_data_symbol_count, get_ecc_metadata_symbol_count, \
    ecc_encode_data, ecc_encode_metadata, ecc_decode_data, ecc_decode_metadata

def encode_color(value: int) -> tuple[int, int, int]:
    """
    Encode color in this format:

    ```
    7        0
    RRR GG BBB
    ```
    
    The RRR, GG and BBB will be extended from 7,3 and 7 to full 255
    """
    b = value & 0x7
    g = (value >> 3) & 0x3
    r = (value >> 5) & 0x7
    
    return (r * 36, g * 85, b * 36)


def calculate_block_count(frame_width: int, frame_height: int,
                          block_width: int, block_height: int) -> tuple[int, int]:
    block_horiz = frame_width // block_width
    block_vert = frame_height // block_height

    return (block_horiz, block_vert)

def initialize_image_from_frame(frame_width: int, frame_height: int):
    return Image.new("RGB", (frame_width, frame_height), (0, 0, 0))


def _generate_frame_filling_list(width: int, height: int):
    return enumerate(((x,y) for y in range(0, height) for x in range(0, width)))

LENGTH_SIZE = 4
METADATA_SIZE = LENGTH_SIZE + get_ecc_metadata_symbol_count()

def encode_message_length(message: bytes) -> bytes:
    return s.pack("I", len(message))


def create_video_frame(block_count: tuple[int, int],
                       block_size: tuple[int, int],
                       image,
                       stream: BinaryIO):
    draw = ImageDraw.Draw(image)
    bhoriz, bvert = block_count
    bw, bh = block_size

    logging.info(f"reading {bhoriz*bvert} bytes for this frame")
    logging.debug(f"bhoriz={bhoriz}, bvert={bvert}")
    logging.debug(f"bw={bw}, bh={bh}")

    ecc_size = get_ecc_data_symbol_count(bhoriz, bvert) * m.ceil(bhoriz*bvert/256)
    logging.info(f"ecc data is {ecc_size} bytes")
    
    data = stream.read((bhoriz * bvert) - METADATA_SIZE - int(ecc_size))
    if len(data) == 0:
        logging.info("no more data to read")
        raise EOFError
    
    logging.debug(f"data=[{repr(data)}]")
    logging.info(f"{len(data)} bytes of data read")
    
    data = ecc_encode_data(bhoriz, bvert, data)    
    metadata = ecc_encode_metadata(encode_message_length(data))

    logging.debug(f"data with ecc=[{repr(data)}]")

    raw_data = metadata + data

    logging.info(f"writing {len(raw_data)} bytes of raw data (of {bhoriz*bvert} available for this frame")
    
    for (index, (x, y)) in _generate_frame_filling_list(bhoriz, bvert):
        try:
            if index >= len(raw_data):
                break
            
            color = encode_color(raw_data[index])
            logging.debug(f"encoded byte {index} as {repr(color)}")
            draw.rectangle([
                x*bw,
                y*bh,
            
                (x+1)*bw-1,
                (y+1)*bh-1,            
            ], color)
        except IndexError:
            logging.error(f"Tried to encode a byte, but there are no bytes left (idx=){index})")
            break
    
    return image


#####


def _determine_correct_color(block: Image.Image) -> tuple[int, int, int]:

    reds = np.array(block.getdata(0), dtype=np.int32)
    greens = np.array(block.getdata(1), dtype=np.int32)
    blues = np.array(block.getdata(2), dtype=np.int32)
    
    #logging.debug(f"list = {repr(reds)}, {repr(greens)}, {repr(blues)}")

    rd = np.std(reds)
    gd = np.std(greens)
    bd = np.std(blues)
    
    return (np.median(reds) + rd,
            np.median(greens) + gd,
            np.median(blues) + bd)
    
    
def decode_block_value(color: tuple[int, int, int]) -> int:
    r, g, b = color
    
    vr = int(r // 36) & 0x7
    vg = int(g // 85) & 0x3
    vb = int(b // 36) & 0x7

    return vb | (vg << 3) | (vr << 5)

def decode_video_data(payload: bytes) -> bytes:
    """
    Decode video data (currently only trim it to the correct length.)
    """
    metadata = payload[:METADATA_SIZE]
    data = payload[METADATA_SIZE:]
    
    (length,) = s.unpack("I", ecc_decode_metadata(metadata))
    logging.info(f"frame length is {length} bytes")

    return data[:length]
    


def decode_video_frame(block_size: tuple[int, int],
                       image: Image.Image) -> bytes:

    bw, bh = block_size
    iwidth, iheight = image.size
    block_count = calculate_block_count(iwidth, iheight,
                                        bw, bh)    
    bhoriz, bvert = block_count

    logging.info(f"frame size is {iwidth}x{iheight}")
    logging.info(f"decoding {bhoriz*bvert} bytes for this frame")
    logging.info(f"bhoriz={bhoriz}, bvert={bvert}")
    logging.info(f"bw={bw}, bh={bh}")

    ret = []
    
    for (i, (x, y)) in _generate_frame_filling_list(bhoriz, bvert):        
        block = image.crop((x * bw, y * bh, (x+1)*bw, (y+1)*bh))

        color = _determine_correct_color(block)
        value = decode_block_value(color)
        logging.debug(f"decoded color for index {i} as {repr(color)} -> {value}")
        ret.append(value)

    logging.debug(f"payload is {repr(bytes(ret))}")
        
    result = ecc_decode_data(bw, bh, decode_video_data(bytes(ret)))    
    
    logging.debug(f"decoded frame into {repr(result)}")
    
    return result
