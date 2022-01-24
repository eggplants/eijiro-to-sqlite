#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import sqlite3

from e2s import __version__


class E2SFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def parse(input_txt: str, output_db: str, joiner: str) -> None:
    conn = sqlite3.connect(output_db)
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
    with open(input_txt, "r", encoding="cp932") as f:
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
                (word, meaning, joiner.join(descriptions)),
            )
        else:
            conn.commit()
            conn.close()


def parse_args() -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        prog="e2s",
        formatter_class=(
            lambda prog: E2SFormatter(
                prog,
                **{
                    "width": shutil.get_terminal_size(fallback=(120, 50)).columns,
                    "max_help_position": 30,
                },
            )
        ),
        description="Convert eijiro(英辞郎) text data into sqlite3",
    )

    parser.add_argument(
        "-i",
        "--input",
        metavar="TXT",
        type=str,
        default="EIJIRO-1448.TXT",
        help="Source file",
    )
    parser.add_argument(
        "-o",
        "--out",
        metavar="DB",
        default="eijiro.db",
        type=str,
        help="Output DB file",
    )
    parser.add_argument(
        "-j", "--joiner", type=str, default="^^^", help="Save just target webpage(s)."
    )
    parser.add_argument(
        "-O",
        "--overwrite",
        action="store_true",
        help="Overwrite db",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not os.path.isfile(args.input):
        raise OSError(f"{args.input} is not found")
    elif os.path.isfile(args.out):
        if args.overwrite:
            os.remove(args.out)
        else:
            raise OSError(f"{args.out} is already exist (use `-O`?)")
    parse(args.input, args.out, args.joiner)


if __name__ == "__main__":
    main()
