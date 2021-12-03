#!/usr/bin/env python3
from urllib import request
from pathlib import Path

if __name__ == '__main__':

    with request.urlopen('https://diviexchange.blob.core.windows.net/%24web/bundesland-zeitreihe.csv') as resp:
        parent_dir = Path('data/divi')
        parent_dir.mkdir(parents=True, exist_ok=True)
        with (parent_dir / 'bundesland-zeitreihe.csv').open('w') as f:
            f.write(resp.read().decode('utf-8'))
