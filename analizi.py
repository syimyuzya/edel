#!/usr/bin/env python

from collections import Counter
from collections.abc import Iterable, Iterator
from itertools import combinations, groupby

from trakti import Row, load

dic = load()

all_special_types = Counter(sub.type for row in dic for sub in row.special)

all_langs = Counter[str]()
for row in dic:
    all_langs.update(item.lang for item in row.etimology)
    for sub in row.special:
        all_langs.update(item.lang for item in sub.words)


def langs_of(row: Row) -> set[str]:
    langs = set(item.lang for item in row.etimology)
    for sub in row.special:
        langs.update(item.lang for item in sub.words)
    return langs


all_yid = [
    row
    for row, langs in ((row, langs_of(row)) for row in dic)
    if 'yid' in langs and 'deu' not in langs
]


def uniq[T](xs: Iterable[T]) -> Iterator[T]:
    return (k for k, _ in groupby(xs))


lang_orders = Counter[tuple[str, str]]()
for row in dic:
    lang_orders.update(
        (x.lang, y.lang) for x, y in combinations(uniq(row.etimology), 2)
    )
    for sub in row.special:
        lang_orders.update(
            (x.lang, y.lang) for x, y in combinations(uniq(sub.words), 2)
        )
