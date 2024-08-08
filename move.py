import shutil
import time


def move_files(exit_flag, move_queue, move_queue_lock):
    while not exit_flag.is_set():
        with move_queue_lock:
            for temp_file, local_path in move_queue:
                shutil.move(temp_file.name, local_path)
                move_queue.remove((temp_file, local_path))
        time.sleep(1)
