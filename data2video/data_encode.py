from PIL import ImageDraw, Image
from typing import BinaryIO
import logging

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
        logging.debug(f"encoding byte {index} to {x},{y}")

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
    
