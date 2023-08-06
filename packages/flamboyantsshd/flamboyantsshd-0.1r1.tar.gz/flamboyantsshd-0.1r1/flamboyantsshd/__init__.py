"Flamboyant SSH daemon"
# There's nothing more to it. It's just flamboyant.

from time import sleep

def tail_file(fp, wait_time=1):
    # Seek to end, more or less.
    while True:
        line = fp.readline()
        if not line:
            sleep(wait_time)
        else:
            yield line
