# eijiro-to-sqlite

[![PyPI version](
  https://badge.fury.io/py/e2s.svg)](
  https://pypi.org/project/e2s/
) [![Maintainability](
  https://api.codeclimate.com/v1/badges/ba54d622e0a91a567bb1/maintainability)](
  https://codeclimate.com/github/eggplants/eijiro-to-sqlite/maintainability
)

[![Style Check](
  https://github.com/eggplants/eijiro-to-sqlite/actions/workflows/style-check.yml/badge.svg)](
  https://github.com/eggplants/eijiro-to-sqlite/actions/workflows/style-check.yml
) [![Release Package](
  https://github.com/eggplants/eijiro-to-sqlite/actions/workflows/release.yml/badge.svg)](
  https://github.com/eggplants/eijiro-to-sqlite/actions/workflows/release.yml) [
![black](
  https://img.shields.io/badge/code%20style-black-000000.svg)](
  https://github.com/psf/black
)

- [英辞郎](https://booth.pm/ja/items/777563) -> sqlite3
  - [Sample data](http://www.eijiro.jp/eijiro-sample-1448.zip): 0 JPY
  - [英辞郎 Ver.144.8](https://booth.pm/ja/items/777563): 495 JPY

## Screenshot

![img](https://user-images.githubusercontent.com/42153744/150694352-5f0af040-a79b-4e12-bd21-40ed67068a57.png)


## Install

```bash
pip install e2s
```

## Run

```bash
wget 'https://www.eijiro.jp/eijiro-sample-1448.zip' # sample data
unzip eijiro-sample-1448.zip
e2s -i EIJIRO-SAMPLE-1448.TXT # `eijiro.db` will be created
```

## Help

```shellsession
$ e2s -h
usage: e2s [-h] [-i TXT] [-o DB] [-j JOINER] [-O] [-V]

Convert eijiro(英辞郎) text data into sqlite3

optional arguments:
  -h, --help                  show this help message and exit
  -i TXT, --input TXT         Source file (default: EIJIRO-1448.TXT)
  -o DB, --out DB             Output DB file (default: eijiro.db)
  -j JOINER, --joiner JOINER  Save just target webpage(s). (default: ^^^)
  -O, --overwrite             Overwrite db (default: False)
  -V, --version               show program's version number and exit
```

## Schema

```sql
CREATE TABLE word (
    id integer primary key,
    word text,
    meaning text,
    descriptions text
)
```
