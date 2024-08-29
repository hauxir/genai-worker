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
