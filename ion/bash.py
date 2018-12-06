import os


class colors:
    red = "\033[0;31m"
    reset = "\033[0m"
    green = "\033[0;32m"
    blue = "\033[0;34"
    yellow = "\033[0;33m"
    magenta = "\033[0;35m"
    bblue = "\033[0;94m"


def get_console_size(index=None):
    return os.popen('stty size', 'r').read().split()
