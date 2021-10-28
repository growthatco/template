import os, sys

from scripts.lib import file as xfile


def has_file_changed(rootdir, file):
    file = os.path.join(rootdir, file)

    # Does the file exist?
    if not os.path.exists(file):
        return False

    # Get the hash from the current file.
    file_hash = xfile.get_file_hash(file).hexdigest()
    file_name = file.split("/").pop()

    # Create the hash from the file to check.
    fingerprint_file = os.path.join(rootdir, f"./tmp/fingerprint/{file_name}.hash")

    # If a fingerprint is not already saved, create one.
    if not os.path.exists(fingerprint_file):
        xfile.write(fingerprint_file, file_hash)
        return True

    # Get the hash from our saved fingerprint.
    fingerprint_file_hash = xfile.get(fingerprint_file)

    if file_hash == fingerprint_file_hash:
        return False

    xfile.overwrite(fingerprint_file, file_hash)
    return True


if __name__ == "__main__":
    # The full path of the project's root directory
    rootdir = sys.argv[1]

    # File to create a md5 fingerprint hash
    file = sys.argv[2]

    has_file_changed(rootdir, file)
