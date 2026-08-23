# import requests
import urllib.request
import json
from .progressBar import ProgressBar

base_url = "https://www.curseforge.com/api/v1"

def get_file_info(mod_id : int, file_id : int):
    url = f"{base_url}/mods/{mod_id}/files/{file_id}"
    with urllib.request.urlopen(url) as response:
        if response.status == 200:
            data = json.loads(response.read())
            return data['data']
        else:
            return None
      
      

def download_mod_file(
        mod_id : int,
        mod_name : str,
        file_id : int,
        destination_path : str,
        progress_bar : ProgressBar | None = None,
    ):
    """
    on_progress: a callback function that takes two arguments: the number of bytes downloaded and the total number of bytes to download. It will be called periodically during the download process.
    """
    
    download_url = f"{base_url}/mods/{mod_id}/files/{file_id}/download"

    try:
        # get the size of the file to be downloaded
        with urllib.request.urlopen(download_url) as response:
            if response.status == 200:
                total_size = int(response.getheader('Content-Length').strip())
                downloaded_size = 0
                sub_pb = progress_bar.set_subbar(total_size, mod_name, True) if progress_bar else None
                with open(destination_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if sub_pb:
                            sub_pb.update(len(chunk))
                progress_bar.remove_subbar() if progress_bar else None
                return True
            else:
                return False
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

