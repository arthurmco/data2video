import logging
from io import BytesIO
from data2video.data_encode import initialize_image_from_frame, create_video_frame, \
    calculate_block_count, decode_video_frame
from PIL import Image
import argparse
import sys

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
BLOCK_HEIGHT = 16
BLOCK_WIDTH = 16

def encode(data: BytesIO | None, output):
    if data is None:
        data = sys.stdin.buffer

    block_count = calculate_block_count(VIDEO_WIDTH, VIDEO_HEIGHT,
                                        BLOCK_WIDTH, BLOCK_HEIGHT)
    frame = initialize_image_from_frame(VIDEO_WIDTH, VIDEO_HEIGHT)
    frame = create_video_frame(block_count,
                               (BLOCK_WIDTH, BLOCK_HEIGHT),
                               frame,
                               data)

    frame.save(output)

def decode(input, msglen: int) -> str:
    with Image.open(input) as im:
        block_count = calculate_block_count(VIDEO_WIDTH, VIDEO_HEIGHT,
                                            BLOCK_WIDTH, BLOCK_HEIGHT)
        data = decode_video_frame(block_count,
                                  (BLOCK_WIDTH, BLOCK_HEIGHT),
                                  msglen,
                                  im)
        return data.decode("utf-8")

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        prog='data2video',
        description="""Decodes and encodes binary data in a series of video frames.
        Useful for 'backing up' some data in a platform that only accepts video,
like a private Youtube video """,
        epilog="(currently only a single image is supported)"
    )

    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--encode", action='store_true')
    operation.add_argument("--decode", action='store_true')
    
    parser.add_argument("--input", help="The input of the operation. " + \
                        "If encoding, the binary file; if decoding, the image.\n" + \
                        "Pass '-' to get it from stdin", required=True)
    parser.add_argument("--output", help="The output of the operation. " + \
                        "If encoding, the image; if decoding, the result file")

    args = parser.parse_args()
    message = \
        "Hello world! I would like to be seem from the thumbnail, please.".encode("utf-8")
    input_file = BytesIO(message)

    if args.encode:
        print(repr(message))
        encode(input_file, args.output)
    elif args.decode:
        decoded = decode(args.input, len(message))
        print(decoded)




if __name__ == "__main__":
    main()
