
# data2video

Encodes data into frames of video.

## How?
 - It creates a 1920x1080 video (configurable in the future)
 - Then, it writes each byte in a 16x16 block (configurable in the
   future)
   - The byte is written like this (RRRGGBBB)
   - The block size is big to account for compression and chroma
     subsampling.
 - Then, we write blocks until we reach the end of the video.
 - If we reach the end of the video, we simply start another frame.
 - The video is encoded at 15fps (configurable in the future).
     
     
## Future
  - Use Reed-Solomon for error correction, this will allow us to
    reduce frame size, frame rate or block size.
