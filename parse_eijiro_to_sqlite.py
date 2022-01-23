#!/usr/bin/env python3

import re
import sqlite3
from os import path

DB_FILE = "eijiro.db"
SOURCE_FILE = "EIJIRO-1448.TXT"
DESCRIPTION_JOINER = "^^^"


def main() -> None:
    if path.isfile(DB_FILE):
        raise OSError(f"{DB_FILE} is already exist")
    if not path.isfile(SOURCE_FILE):
        raise OSError(f"{SOURCE_FILE} is not found")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """\
        CREATE TABLE word (
          id integer primary key,
          word text,
          meaning text,
          descriptions text
        )
        """
    )
    with open(SOURCE_FILE, "r", encoding="cp932") as f:
        fs = f.readlines()
        len_fs = len(fs)
        for idx, line in enumerate(fs):
            word, rest = line[1:].strip().split(" : ")
            meaning, *descriptions = re.split(r"(?=[■◆])", rest)
            p = (idx + 1) / len_fs * 100.0
            print(f"[{idx+1}/{len_fs}] ({int(p)} %)", end="\r", flush=True)
            cur.execute(
                """\
                INSERT INTO word (
                  word,
                  meaning,
                  descriptions
                )
                VALUES (?, ?, ?)
                """,
                (word, meaning, DESCRIPTION_JOINER.join(descriptions)),
            )
        else:
            conn.commit()
            conn.close()


if __name__ == "__main__":
    main()
