import curses
import os
import threading
import concurrent.futures
import time

from display import display_status_thread
from download import Download, DownloadImpl
from move import move_files


def main(download: Download):
    base_url = ""
    base_path = "./archive"
    type = ""

    move_queue = []
    move_queue_lock = threading.Lock()
    status = {}
    exit_flag = threading.Event()

    user_path = input("Enter download directory [./archive]: ")
    while base_url == "":
        base_url = input("Enter URL: ")
    if user_path:
        base_path = user_path

    if "archive.org" in base_url:
        # remove header if present
        base_url = base_url.replace("https://archive.org/details/", "")
        base_url = base_url.replace("https://archive.org/", "")
        base_directory = base_url.split("/")[0]
        base_url = "https://archive.org/download/" + base_directory
        type = "archive"

    # remove tailing slash
    base_url = base_url.rstrip("/")

    # create download directory
    os.makedirs(base_path, exist_ok=True)
    stdscr = curses.initscr()
    stdscr.nodelay(False)
    curses.curs_set(0)
    stdscr.clear()

    exit_flag = threading.Event()
    status_thread = threading.Thread(
        target=display_status_thread, args=(stdscr, status, exit_flag, 0.1)
    )
    status_thread.daemon = True
    status_thread.start()

    move_files_thread = threading.Thread(
        target=move_files, args=(exit_flag, move_queue, move_queue_lock)
    )
    move_files_thread.daemon = True
    move_files_thread.start()
    download_recursive = download.download_recursive

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = download_recursive(
                base_url,
                "/",
                base_path,
                status,
                move_queue,
                move_queue_lock,
                executor,
                type,
            )
        concurrent.futures.wait(futures)
        print("--------------All downloads complete!--------------")
    except KeyboardInterrupt:
        print("--------------Download interrupted!--------------")
    except Exception as e:
        print(f"Error: {e}")

    while move_queue:
        time.sleep(1)
    exit_flag.set()
    curses.endwin()

if __name__ == "__main__":
    main(DownloadImpl)
