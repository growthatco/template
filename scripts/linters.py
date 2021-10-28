import os, shutil, sys


def generate_linters(rootdir):
    # The absolute path to the project's linter configurations
    lintersdir = os.path.join(rootdir, "linters")

    # A list of a destination directories to copy the linters to
    destdirs = [rootdir, os.path.join(rootdir, ".github", "linters")]

    # # Get all of the files in the linters directory
    files = os.listdir(lintersdir)

    # Copy all of the files to the desired destinations
    for destdir in destdirs:
        for fname in files:
            shutil.copy2(os.path.join(lintersdir, fname), destdir)


if __name__ == "main":
    # The absolute path of the project's root directory
    rootdir = sys.argv[1]

    #
    generate_linters(rootdir)
