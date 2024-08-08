import os
import random
import tempfile
import time
from urllib.parse import unquote, urlparse
import requests
import concurrent.futures

from data import Data

class Download:
    def download_file(url, local_path, task_id, status, move_queue, move_queue_lock):
        raise NotImplementedError()
    
    def download_recursive(
        base_url,
        current_url,
        base_path,
        status,
        move_queue,
        move_queue_lock,
        executor: concurrent.futures.Executor,
        type="archive",
    ):
        raise NotImplementedError()


class DownloadImpl(Download):
    # Function to download a file from a URL and save it locally
    def download_file(url, local_path, task_id, status, move_queue, move_queue_lock):
        session = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=0)
        session.mount("http://", a)
        session.mount("https://", a)
        try:
            response = session.get(url, stream=True)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            with open("error.log", "a") as f:
                f.write(f"Error downloading file: {e}\n")
            return
        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))
            chunk_size = 8 * 1024  # You can adjust this chunk size

            # Create a temporary file in the system's temp directory
            temp_file = tempfile.NamedTemporaryFile(delete=True, delete_on_close=False)
            bytes_written = 0
            start_time = time.time()

            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    temp_file.write(chunk)
                    bytes_written += len(chunk)

                    # Calculate download speed and time elapsed
                    elapsed_time = time.time() - start_time
                    download_speed = bytes_written / (
                        1024 * elapsed_time + 0.000001
                    )  # Speed in KB/s

                    percent_complete = (bytes_written / total_size) * 100
                    status[task_id] = (percent_complete, download_speed, local_path)

            temp_file.close()

            # Add the file to the move queue
            with move_queue_lock:
                move_queue.append((temp_file, local_path))

            status[task_id] = ("FIN", download_speed, local_path)
        else:
            print(f"Error downloading file: {response.status_code}")
            with open("error.log", "a") as f:
                f.write(f"Error downloading file: {e}\n")


    # Recursively download the entire directory
    def download_recursive(
        base_url,
        current_url,
        base_path,
        status,
        move_queue,
        move_queue_lock,
        executor: concurrent.futures.Executor,
        type="archive",
    ):
        session = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=0)
        session.mount("http://", a)
        session.mount("https://", a)
        futures = []
        response = session.get(
            base_url + current_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
            },
        )
        page_source = response.text
        links = Data(type, page_source)
        # limit = 0 if type == "archive" else 1
        for i, href in enumerate(links):
            if href[0] in ["?", "#"]:
                continue
            if href == "/":
                continue
            if href and href[-1] == "/":
                if "blog" in href:
                    continue
                futures.extend(
                    DownloadImpl.download_recursive(
                        base_url,
                        current_url + href,
                        base_path,
                        status,
                        move_queue,
                        move_queue_lock,
                        executor,
                        type,
                    )
                )
            elif href:
                local_path = (
                    os.path.join(
                        base_path, unquote(urlparse(current_url + href).path.lstrip("/"))
                    )
                    .replace(" /", "/")
                    .replace("/", os.sep)
                )

                # Remove forbidden characters for Windows filenames
                forbidden_chars = ["<", ">", ":", '"', "|", "?", "*"]
                for char in forbidden_chars:
                    local_path = local_path.replace(char, "")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                download_url = base_url + "/" + current_url + "/" + href
                futures.append(
                    executor.submit(
                        DownloadImpl.download_file,
                        download_url,
                        local_path,
                        random.randint(10**6, 10**7),
                        status,
                        move_queue,
                        move_queue_lock,
                    )
                )
        return futures
