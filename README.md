# Maŝin-legeblaj datumoj de <cite>Etymological Dictionary of the Esperanto Language</cite>

Fonto de la origina bitigita teksto: https://reto.cn/php/hanyu/vortoj/etimologia-vortaro-de-esperanto/

## Dosieroj

- `eligo/`: La datumoj, en kelkaj formoj
- `header-footer.md`: La tekstoj antaŭ kaj post la ĉefa vortlisto, reformigitaj en Markdown
- `datumoj/origina.txt`: Fonta teksto
- `trakti.py`: La ĉefa bloko por trakti la datumojn
- `konverti.py`: Rulebla programo, kiu produktas la datumdosierojn (en `eligo/`-n) en pli facile analizeblaj formoj kun korektoj aplikitaj

## JSON-formo

Vortoj kun ordinara listo de etimologio:

```
{
  "headword": vorto,
  "etimology": [
    {
      "lang": lingvokodo en ISO-639-3,
      "word": fonta vorto en tiu ĉi lingvo
    },
    ...
  ]
}
```

Vortoj kun apartaj komentoj:

```
{
  "headword": vorto,
  "special": [
    {
      "type": tipo de la etimologio (compare, calque of, ktp),
      "words": [
        { "lang": ..., "word": ... (vidu supre) }
      ]
    },
    ...
  ]
}
```

## Korektoj

- Ĉiuj vortoj reordigitaj
  - La aŭtoro ŝajne provis meti derivaĵojn post la radikvorto, sed la rezulto tamen prezentiĝas ne tre bona. Tial, tiu ĉi reordigo estas tute laŭ la literordo.
- Spaceto mankanta post "=": labirinto, laboratorio

Individuaj linioj:

- kripta = Ger. kryptos
  - Ger. → Gre.
- serioza = Rus. cepьëзный, Ger. seriös, Fra. sérieux, Ita. serioso, Eng. serious
  - Fra. → Fre.
- poŝtkarto = Yid. postkort, Ger. Postkarte, Fre. carte postale, Fre. cartolina postale
  - (la dua) Fre. → Ita.
- sciuro = Eng squirrel, Lat. sciurus
  - (mankas punkto) Eng → Eng.
- suspekti = Eng. suspecter, Eng. suspect
  - (la unua) Eng. → Fre.
- Lingv-etikedo, kiu aperas plurfoje por la sama vorto:
  - normo: Lit. norma (2 fojojn)
  - raso: Lit. rase (2 fojojn)

## Pri vortoj latinaj en plurala formo (tiuj kun "(pl.)")

Ekzemple:

- lakto = Lat. (pl.) lactes
- radiko = Ita. radice, Lat. (pl.) radices

Uzo de _nominativa plurala_ formo, kvankam tio ja donas la ĝustajn radikformojn de la vortoj, ĝi tamen estas malbona decido, ĉar tiu formo en Latino ne vere estas bona reprezento por montri la radikon, kaj ne ĉiu vorto estas nombrebla.

Pli bone estus uzi la _akuzativa singulara_ formo, kaj uzi la formon de Mezepoka Latino se necese. Ekz. lakto = Lat. lac, (medieval) lactem; radiko = Lat. radicem ktp.

Alia bona elekto eble estus la _genitiva singulara_ formo, kiun multaj vortaroj de Latino uzas por montri deklinaciojn.
