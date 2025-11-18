from collections.abc import Iterable, Iterator
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
import json
import re
from sys import stderr
from typing import Any, Self, TextIO

from icu import Collator, Locale  # type: ignore

collator_eo = Collator.createInstance(Locale('eo'))


LANGUAGES = {
    'Dut': 'nld',
    'Eng': 'eng',
    'Fre': 'fra',
    'Ger': 'deu',
    'Gre': 'grc',
    'Ita': 'ita',
    'Lat': 'lat',
    'Lit': 'lit',
    'Pol': 'pol',
    'Rus': 'rus',
    'Spa': 'spa',
    'Yid': 'yid',
}
LANGUAGES_REV = dict((v, k) for k, v in LANGUAGES.items())


def unwrap[T](x: T | None) -> T:
    assert x is not None
    return x


# TODO `(pl.)`
@dataclass
class ForeignWord:
    lang: str
    word: str


@dataclass
class SpecialEtymology:
    type: str
    words: list[ForeignWord]


@dataclass
class Row:
    word: str
    etimology: list[ForeignWord]
    special: list[SpecialEtymology]

    def format(self, original_style=False) -> str:
        if self.etimology and self.special:
            raise ValueError('ambaŭ tipoj de etimologioj')

        if self.etimology:
            delim = ' = ' if original_style else ': '
            return f'{self.word}{delim}{self._format_words(self.etimology, original_style)}'

        parts = []
        for sub in self.special:
            parts.append(f'{sub.type} {self._format_words(sub.words, original_style)}')
        delim_word = ' ' if original_style else ': '
        delim_type = ', ' if original_style else '; '
        return f'{self.word}{delim_word}[{delim_type.join(parts)}]'

    @staticmethod
    def _format_words(words: list[ForeignWord], original_style) -> str:
        parts = []
        current_lang = ''
        for item in words:
            if item.lang != current_lang:
                if original_style:
                    lang_str = LANGUAGES_REV[item.lang] + '.'
                else:
                    lang_str = f'<{item.lang}>'
                parts.append(f'{lang_str} {item.word}')
                current_lang = item.lang
            else:
                parts.append(item.word)
        return ', '.join(parts)

    def json_obj(self) -> dict[str, Any]:
        if self.etimology and self.special:
            raise ValueError('ambaŭ tipoj de etimologioj')
        obj: dict[str, Any] = {
            'headword': self.word,
        }
        if self.etimology:
            obj['etimology'] = self._json_list_from_words(self.etimology)
        else:
            special_list: list[dict[str, Any]]
            obj['special'] = special_list = []
            for sub in self.special:
                special_list.append(
                    {
                        'type': sub.type,
                        'words': self._json_list_from_words(sub.words),
                    }
                )
        return obj

    @staticmethod
    def _json_list_from_words(words: list[ForeignWord]) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        for item in words:
            result.append({'lang': item.lang, 'word': item.word})
        return result

    @classmethod
    def from_items(cls, word: str, items: Iterable[str]) -> Self:
        sublists = cls._parse_items(items)
        special_type, sublist = next(sublists)
        if special_type is not None:
            raise ValueError(f'aparta etikedo en ordinara etimologio: {special_type}')
        etimology = sublist
        if (sublists_next := next(sublists, None)) is not None:
            special_type, _ = sublists_next
            raise ValueError(f'aparta etikedo en ordinara etimologio: {special_type}')

        return cls(word=word, etimology=etimology, special=[])

    @classmethod
    def from_special(cls, word: str, items: Iterable[str]) -> Self:
        special: list[SpecialEtymology] = []
        for special_type, sublist in cls._parse_items(items):
            if special_type is None:
                raise ValueError('ordinaraj vortoj en aparta etimologio')
            special.append(SpecialEtymology(type=special_type, words=sublist))
        return cls(word=word, etimology=[], special=special)

    @staticmethod
    def _parse_items(
        items: Iterable[str],
    ) -> Iterator[tuple[str | None, list[ForeignWord]]]:
        current_type: str | None = None
        seen_langs = set()
        current_words = []
        current_lang = ''
        for item in items:
            parts = re.split(r'\s*\b([A-z][a-z]{2})\.\s*', item, maxsplit=1)
            if len(parts) == 1:
                special_type = None
                lang = None
                foreign_word = item
            else:
                special_type, lang, foreign_word = parts
                # korekto
                if lang == 'Fra':
                    lang = 'Fre'
                lang = LANGUAGES[lang]

            if special_type:
                if current_words:
                    yield (current_type, current_words)
                current_type = special_type
                seen_langs = set()
                current_words = []
                current_lang = ''

            if lang:
                if lang in seen_langs:
                    raise ValueError(f'etikedo aperanta plurfoje: {lang}')
                seen_langs.add(lang)
                current_lang = lang
            elif not current_lang:
                raise ValueError('vorto sen lingva etikedo')

            current_words.append(ForeignWord(lang=current_lang, word=foreign_word))

        if current_words:
            yield (current_type, current_words)


def strip_lines(lines: Iterable[str]) -> Iterator[str]:
    is_header = True
    for line in lines:
        line = line.rstrip()

        if is_header:
            if line == 'A':
                is_header = False
            else:
                continue
        if line == 'Notes :':
            break

        if not line:
            continue
        if len(line) == 1 and line.isalpha() and line.isupper():
            continue

        # Korektoj
        if line == 'kripta = Ger. kryptos':
            line = line.replace('Ger.', 'Gre.')
        elif (
            line
            == 'poŝtkarto = Yid. postkort, Ger. Postkarte, Fre. carte postale, Fre. cartolina postale'
        ):
            line = line.replace('Fre. cartolina postale', 'Ita. cartolina postale')
        elif line == 'sciuro = Eng squirrel, Lat. sciurus':
            line = line.replace('Eng', 'Eng.')
        elif line == 'suspekti = Eng. suspecter, Eng. suspect':
            line = line.replace('Eng. suspecter', 'Fre. suspecter')
        elif (
            line
            == 'normo = Rus. нopмa, Lit. norma, Ger. Norm, Lit. norma, Fre. norme, Ita. norma, Eng. norm, Lat. norma'
        ):
            line = line.replace(
                'Lit. norma, Ger. Norm, Lit. norma', 'Lit. norma, Ger. Norm'
            )
        elif (
            line
            == 'raso = Rus. paca, Lit. rase, Pol. rasa, Lit. rase, Ger. Rasse, Eng. race'
        ):
            line = line.replace(
                'Lit. rase, Pol. rasa, Lit. rase', 'Lit. rase, Pol. rasa'
            )

        yield line


def load(input_lines: Iterable[str] | None = None) -> list[Row]:
    context: AbstractContextManager[Iterable[str]]
    if input_lines is None:
        context = open('datumoj/origina.txt')
    else:
        context = nullcontext(input_lines)

    dictionary: list[Row] = []
    with context as lines:
        for line in strip_lines(lines):
            if '=' in line:
                word, rest = unwrap(
                    re.fullmatch(r'([\w -]+?)\s*=\s*(.*)', line)
                ).groups()
                items = re.split(r',\s*', rest)
                assert all(item.strip() == item for item in items), items
                dictionary.append(Row.from_items(word, items))
            else:
                word, rest = unwrap(
                    re.fullmatch(r'([\w -]+?)\s*\[(.*)\]', line)
                ).groups()
                items = re.split(r',\s*', rest)
                assert all(item.strip() == item for item in items), items
                dictionary.append(Row.from_special(word, items))

            for item in items:
                if (match := re.match(r'([A-Z][a-z]{2})(?=\s)', item)) is not None:
                    print(
                        f'Averto: Probabla lingva etikedo: "{match[0]}" en linio: {line}',
                        file=stderr,
                    )

    dictionary.sort(key=lambda x: collator_eo.getSortKey(x.word))
    return dictionary


def save_json(dic: Iterable[Row], file: TextIO):
    is_first = True
    for row in dic:
        if is_first:
            print('[', file=file)
            is_first = False
        else:
            print(',', file=file)
        print(
            json.dumps(row.json_obj(), ensure_ascii=False, separators=(',', ':')),
            end='',
            file=file,
        )
    print('\n]', file=file)
