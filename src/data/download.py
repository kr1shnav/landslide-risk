from pathlib import Path
import requests
def download_file(url: str, destination: str | Path, timeout: int=30) -> Path:
    dest=Path(destination); dest.parent.mkdir(parents=True,exist_ok=True)
    with requests.get(url,stream=True,timeout=timeout) as r:
        r.raise_for_status()
        with dest.open('wb') as f:
            for chunk in r.iter_content(1024*1024): f.write(chunk)
    return dest
