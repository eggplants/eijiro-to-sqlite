"""Convert Eijiro text data into sqlite3 database."""

import argparse
import re
import shutil
import sqlite3
from pathlib import Path

from e2s import __version__


class E2SFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Custom formatter for argparse."""


def parse(input_txt: Path, output_db: Path, joiner: str) -> None:
    """Parse eijiro text file and create sqlite3 database.

    Args:
        input_txt (Path): Path to eijiro text file.
        output_db (Path): Path to output sqlite3 database file.
        joiner (str): Joiner for descriptions.
    """
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
    with input_txt.open(encoding="cp932") as f:
        fs = f.readlines()
        len_fs = len(fs)
        for idx, line in enumerate(fs):
            word, rest = line[1:].strip().split(" : ")
            meaning, *descriptions = re.split(r"(?=[■◆])", rest)
            p = (idx + 1) / len_fs * 100.0
            print(f"[{idx + 1}/{len_fs}] ({int(p)} %)", end="\r", flush=True)  # noqa: T201
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
        conn.commit()
        conn.close()


def parse_args() -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        prog="e2s",
        formatter_class=(
            lambda prog: E2SFormatter(
                prog,
                width=shutil.get_terminal_size(fallback=(120, 50)).columns,
                max_help_position=30,
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
    parser.add_argument("-j", "--joiner", type=str, default="^^^", help="Joiner for descriptions")
    parser.add_argument(
        "-O",
        "--overwrite",
        action="store_true",
        help="Overwrite db",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.out)
    if not input_path.is_file():
        msg = f"{args.input} is not found"
        raise FileNotFoundError(msg)
    if output_path.is_file():
        if args.overwrite:
            output_path.unlink()
        else:
            msg = f"{args.out} is already exist (use `-O`?)"
            raise OSError(msg)
    parse(input_path, output_path, args.joiner)


if __name__ == "__main__":
    main()
