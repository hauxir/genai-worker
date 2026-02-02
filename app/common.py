import io
from PIL import Image, ImageChops

import hashlib


def hash_parameters_md5(*args):
    # Convert all arguments to strings and concatenate them
    concatenated_string = "".join(map(str, args))

    # Create an MD5 hash object
    md5_hash = hashlib.md5()

    # Update the hash object with the concatenated string (encoded to bytes)
    md5_hash.update(concatenated_string.encode("utf-8"))

    # Get the hexadecimal representation of the hash
    hash_hex = md5_hash.hexdigest()

    return hash_hex


def crop_transparent_image(image_bytes, fuzz=20):
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGBA")
        bbox = img.getbbox()
        bg_color = img.getpixel((0, 0))
        bg = Image.new(img.mode, img.size, bg_color)
        diff = ImageChops.difference(img, bg)

        if fuzz > 0:
            diff = diff.point(lambda p: p > fuzz and 255)

        bbox = diff.getbbox()
        if bbox:
            img = img.crop(bbox)

        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
        output_buffer.seek(0)
        return output_buffer.read()
