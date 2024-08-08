# Function to display the download status
import curses
import time


def display_status(window, status):
    temp_status = status.copy()
    y, x = 0, 0
    for task_id, (percent_complete, download_speed, local_path) in temp_status.items():
        max_length = max([len(x[2]) for x in temp_status.values()])
        if percent_complete != "FIN":
            try:
                window.addstr(
                    y,
                    x,
                    f"Task {task_id}: {local_path:{max_length}} {percent_complete:.2f}% {download_speed:.2f} KB/s",
                )
                y += 1
            except curses.error:
                with open("error.log", "a") as f:
                    f.write(f"Error displaying status: {task_id}\n")
                pass

# Separate Thread to display the download status
def display_status_thread(stdscr, status, exit_flag, interval=0.25):
    while not exit_flag.is_set():
        stdscr.clear()
        display_status(stdscr, status)
        stdscr.refresh()
        time.sleep(interval)