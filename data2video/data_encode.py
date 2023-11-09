from PIL import ImageDraw, Image
from typing import BinaryIO
import logging
import functools as f

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


def create_video_frame(block_count: tuple[int, int],
                       block_size: tuple[int, int],
                       image,
                       stream: BinaryIO):
    draw = ImageDraw.Draw(image)
    bhoriz, bvert = block_count
    bw, bh = block_size

    logging.debug(f"bhoriz={bhoriz}, bvert={bvert}")
    logging.debug(f"bw={bw}, bh={bh}")
    logging.info(f"reading {bw*bh} bytes for this frame")
    data = stream.read(bhoriz * bvert)

    logging.debug(f"data=[{repr(data)}]")

    for (index, (x, y)) in _generate_frame_filling_list(bhoriz, bvert):
        try:
            color = encode_color(data[index])
            logging.debug(f"encoded byte {index} as {repr(color)}")
            draw.rectangle([
                x*bw,
                y*bh,
            
                (x+1)*bw-1,
                (y+1)*bh-1,            
            ], color)
        except IndexError:
            logging.debug(f"no bytes left")
            break
    
    return image


#####


def _determine_correct_color(block: Image.Image) -> tuple[int, int, int]:

    def sum_color(acc, val):
        ar, ag, ab = acc
        vr, vg, vb = val

        return (ar+vr, ag+vg, ab+vb)

    block_data: list[tuple[int, int, int]] = block.getdata()
    logging.debug(f"list = {repr(list((block_data)))}")
    cr, cg, cb = f.reduce(sum_color, block_data, (0, 0, 0))

    return (cr // len(block_data),
            cg // len(block_data),
            cb // len(block_data))
    
    
def decode_block_value(color: tuple[int, int, int]) -> int:
    r, g, b = color
    
    vr = int(r // 36) & 0x7
    vg = int(g // 85) & 0x3
    vb = int(b // 36) & 0x7

    return vb | (vg << 3) | (vr << 5)


def decode_video_frame(block_count: tuple[int, int],
                       block_size: tuple[int, int],
                       byte_count: int,
                       image: Image.Image) -> bytes:
    bhoriz, bvert = block_count
    bw, bh = block_size

    logging.info("decoding frame")
    logging.debug(f"bhoriz={bhoriz}, bvert={bvert}")
    logging.debug(f"bw={bw}, bh={bh}")

    ret = []
    
    for (i, (x, y)) in _generate_frame_filling_list(bhoriz, bvert):
        if i >= byte_count:
            break
        
        block = image.crop((x * bw, y * bh, (x+1)*bw, (y+1)*bh))

        color = _determine_correct_color(block)
        value = decode_block_value(color)
        logging.debug(f"decoded color for index {i} as {repr(color)} -> {value}")
        ret.append(value)

    result = bytes(ret)
    logging.info(f"decoded frame into {repr(result)}")
    
    return result
