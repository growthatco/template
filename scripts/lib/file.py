import fnmatch, hashlib, os, re


def get(path):
    """
    Read & return the contents of the provided `path` with the
    given `content`."""
    with open(path, encoding="utf-8") as file:
        return file.read()


def write(path, content):
    """
    Read & write to the provided `path` with the
    given `content`."""
    with open(path, "a+", encoding="utf-8") as file:
        file.write(content)


def overwrite(path, content):
    """
    Overwrite the contents of the provided `path` with the
    given `content`. Do nothing if there have been no changes to the file."""
    current_hash = get_file_hash(path).hexdigest()
    incoming_hash = hashlib.blake2b(str(content).encode("utf-8")).hexdigest()

    if current_hash != incoming_hash:
        with open(path, "w+", encoding="utf-8") as file:
            file.write(content)


def find(name, path):
    """
    Find all files that match the provided `name` in a given `path`."""
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def find_by_pattern(includes, path, excludes=[]):
    """
    Find all files that match the provided regex patterns in a
    given `path`.

    https://stackoverflow.com/a/5141829
    """

    # Transform glob patterns to regular expressions
    includes = r"|".join([fnmatch.translate(x) for x in includes])
    excludes = r"|".join([fnmatch.translate(x) for x in excludes]) or r"$."

    result = []

    for root, dirs, files in os.walk(path):

        # Exclude ignored directories
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]

        # Exclude ignored files
        files = [f for f in files if not re.match(excludes, f)]

        # Include matching files
        files = [f for f in files if re.match(includes, f)]

        for name in files:
            result.append(os.path.join(root, name))

    return result


def get_file_hash(path):
    """
    Return the cryptographic hash of the contents of the file located
    at the provided `path`.
    """
    hash = hashlib.blake2b()
    with open(path, "rb") as file:
        while chunk := file.read(8192):
            hash.update(chunk)

    return hash
