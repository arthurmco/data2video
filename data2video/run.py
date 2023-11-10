import logging
from io import BytesIO
from data2video.data_encode import initialize_image_from_frame, create_video_frame, \
    calculate_block_count, decode_video_frame
from PIL import Image
import argparse
import sys

DEFAULT_VIDEO_WIDTH = 1920
DEFAULT_VIDEO_HEIGHT = 1080

BLOCK_HEIGHT = 16
BLOCK_WIDTH = 16

def encode(data: BytesIO | None, video_width: int,
           video_height: int, output):
    if data is None:
        data = sys.stdin.buffer

    block_count = calculate_block_count(video_width, video_height,
                                        BLOCK_WIDTH, BLOCK_HEIGHT)
    frame = initialize_image_from_frame(video_width, video_height)
    frame = create_video_frame(block_count,
                               (BLOCK_WIDTH, BLOCK_HEIGHT),
                               frame,
                               data)

    frame.save(output)

def decode(input) -> bytes:
    with Image.open(input) as im:
        data = decode_video_frame((BLOCK_WIDTH, BLOCK_HEIGHT),
                                  im)
        return data

def main():
    logging.basicConfig(level=logging.INFO)

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
    parser.add_argument("--width", help="The width of the output image (encode only)",
                        default=DEFAULT_VIDEO_WIDTH, type=int)
    parser.add_argument("--height", help="The height of the output image (encode only)",
                        default=DEFAULT_VIDEO_HEIGHT, type=int)
    parser.add_argument("--output", help="The output of the operation. " + \
                        "If encoding, the image; if decoding, the result file",
                        required=True)

    args = parser.parse_args()
    
    if args.input == '-':
        print("opening stdin")
        input_file = None
    else:
        print(f"opening {args.input}")
        input_file = open(args.input, "rb")
        
    if args.encode:
        encode(input_file, args.width, args.height, args.output)
    elif args.decode:
        decoded = decode(args.input)
        with open(args.output, "wb") as out:
            out.write(decoded)
        
        #print(decoded.decode("utf-8"))

    if input_file is not None:
        input_file.close()
    



if __name__ == "__main__":
    main()
