#!/usr/bin/env python

from pathlib import Path

from trakti import load, save_json

if __name__ == '__main__':
    dic = load()
    path_eligo = Path('eligo')
    path_eligo.mkdir(exist_ok=True)
    with open(path_eligo / 'datumoj.json', 'w', newline='') as fout:
        save_json(dic, fout)
    for original_style, suffix in ((True, 'origina'), (False, 'nova')):
        with open(path_eligo / f'stilo-{suffix}.txt', 'w', newline='\r\n') as fout:
            for row in dic:
                print(row.format(original_style), file=fout)
