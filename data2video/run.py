import logging
from io import BytesIO
from data2video.data_encode import initialize_image_from_frame, create_video_frame, \
    calculate_block_count, decode_video_frame
from PIL import Image

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
BLOCK_HEIGHT = 16
BLOCK_WIDTH = 16

def encode(message, output):
    data = BytesIO(message.encode("utf-8"))

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
    
    message = "Hello world! I would like to be seem from the thumbnail, please."
    encode(message, "helloworld.png")
    decoded = decode("helloworld.png", len(message.encode("utf-8")))

    print("\n")
    print(f"Encoded: '{message}'")
    print(f"Decoded: '{decoded}'")

    

if __name__ == "__main__":
    main()
    
