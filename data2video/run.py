import logging
from io import BytesIO
from data2video.data_encode import initialize_image_from_frame, create_video_frame, \
    calculate_block_count

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
BLOCK_HEIGHT = 16
BLOCK_WIDTH = 16

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    message = "Hello world!"
    
    data = BytesIO(message.encode("utf-8"))

    block_count = calculate_block_count(VIDEO_WIDTH, VIDEO_HEIGHT,
                                        BLOCK_WIDTH, BLOCK_HEIGHT)
    frame = initialize_image_from_frame(VIDEO_WIDTH, VIDEO_HEIGHT)
    frame = create_video_frame(block_count,
                               (BLOCK_WIDTH, BLOCK_HEIGHT),
                               frame,
                               data)

    frame.save("helloworld.png")

if __name__ == "__main__":
    main()
    
