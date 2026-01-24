import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from e2s import __version__
from e2s.main import main, parse, parse_args


def test_version() -> None:
    assert __version__ is not None


class TestParse:
    """Test parse function."""

    def test_parse_basic(self, tmp_path: Path) -> None:
        """Test basic parsing functionality."""
        input_file = tmp_path / "test_input.txt"
        output_db = tmp_path / "test_output.db"

        # Create sample data (英辞郎 format)
        sample_data = """■test : テスト◆説明1◆説明2
■hello : こんにちは■例文1■例文2
■world : 世界◆地球
"""
        input_file.write_text(sample_data, encoding="cp932")

        # Run parse
        parse(input_file, output_db, "^^^")

        # Verify database was created
        assert output_db.exists()

        # Verify database contents
        conn = sqlite3.connect(output_db)
        cur = conn.cursor()

        # Check table structure
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='word'")
        assert cur.fetchone() is not None

        # Check data
        cur.execute("SELECT word, meaning, descriptions FROM word ORDER BY id")
        rows = cur.fetchall()

        assert len(rows) == 3  # noqa: PLR2004
        assert rows[0][0] == "test"
        assert rows[0][1] == "テスト"
        assert rows[0][2] == "◆説明1^^^◆説明2"

        assert rows[1][0] == "hello"
        assert rows[1][1] == "こんにちは"
        assert rows[1][2] == "■例文1^^^■例文2"

        assert rows[2][0] == "world"
        assert rows[2][1] == "世界"
        assert rows[2][2] == "◆地球"

        conn.close()

    def test_parse_with_custom_joiner(self, tmp_path: Path) -> None:
        """Test parsing with custom joiner."""
        input_file = tmp_path / "test_input.txt"
        output_db = tmp_path / "test_output.db"

        sample_data = """■test : テスト◆説明1◆説明2
"""
        input_file.write_text(sample_data, encoding="cp932")

        # Use custom joiner
        parse(input_file, output_db, " | ")

        conn = sqlite3.connect(str(output_db))
        cur = conn.cursor()
        cur.execute("SELECT descriptions FROM word")
        descriptions = cur.fetchone()[0]
        conn.close()

        assert descriptions == "◆説明1 | ◆説明2"

    def test_parse_no_descriptions(self, tmp_path: Path) -> None:
        """Test parsing entry without descriptions."""
        input_file = tmp_path / "test_input.txt"
        output_db = tmp_path / "test_output.db"

        sample_data = """■test : テスト
"""
        input_file.write_text(sample_data, encoding="cp932")

        parse(input_file, output_db, "^^^")

        conn = sqlite3.connect(str(output_db))
        cur = conn.cursor()
        cur.execute("SELECT word, meaning, descriptions FROM word")
        row = cur.fetchone()
        conn.close()

        assert row[0] == "test"
        assert row[1] == "テスト"
        assert row[2] == ""


class TestParseArgs:
    """Test command-line argument parsing."""

    def test_parse_args_defaults(self) -> None:
        """Test default argument values."""
        with patch("sys.argv", ["e2s"]):
            args = parse_args()
            assert args.input == "EIJIRO-1448.TXT"
            assert args.out == "eijiro.db"
            assert args.joiner == "^^^"
            assert args.overwrite is False

    def test_parse_args_custom_input(self) -> None:
        """Test custom input file."""
        with patch("sys.argv", ["e2s", "-i", "custom.txt"]):
            args = parse_args()
            assert args.input == "custom.txt"

    def test_parse_args_custom_output(self) -> None:
        """Test custom output file."""
        with patch("sys.argv", ["e2s", "-o", "custom.db"]):
            args = parse_args()
            assert args.out == "custom.db"

    def test_parse_args_custom_joiner(self) -> None:
        """Test custom joiner."""
        with patch("sys.argv", ["e2s", "-j", "|||"]):
            args = parse_args()
            assert args.joiner == "|||"

    def test_parse_args_overwrite(self) -> None:
        """Test overwrite flag."""
        with patch("sys.argv", ["e2s", "-O"]):
            args = parse_args()
            assert args.overwrite is True

    def test_parse_args_all_options(self) -> None:
        """Test all options combined."""
        with patch("sys.argv", ["e2s", "-i", "input.txt", "-o", "output.db", "-j", "~~~", "-O"]):
            args = parse_args()
            assert args.input == "input.txt"
            assert args.out == "output.db"
            assert args.joiner == "~~~"
            assert args.overwrite is True

    def test_parse_args_long_options(self) -> None:
        """Test long option names."""
        with patch("sys.argv", ["e2s", "--input", "test.txt", "--out", "test.db", "--joiner", ":::", "--overwrite"]):
            args = parse_args()
            assert args.input == "test.txt"
            assert args.out == "test.db"
            assert args.joiner == ":::"
            assert args.overwrite is True

    def test_parse_args_version(self) -> None:
        """Test version flag."""
        with patch("sys.argv", ["e2s", "-V"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 0

    def test_parse_args_help(self) -> None:
        """Test help flag."""
        with patch("sys.argv", ["e2s", "-h"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 0


class TestMain:
    """Test main function."""

    def test_main_success(self, tmp_path: Path) -> None:
        """Test successful execution."""
        input_file = tmp_path / "input.txt"
        output_db = tmp_path / "output.db"

        sample_data = """■test : テスト◆説明
"""
        input_file.write_text(sample_data, encoding="cp932")

        with patch("sys.argv", ["e2s", "-i", str(input_file), "-o", str(output_db)]):
            main()

        assert output_db.exists()

        conn = sqlite3.connect(str(output_db))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM word")
        count = cur.fetchone()[0]
        conn.close()

        assert count == 1

    def test_main_input_not_found(self, tmp_path: Path) -> None:
        """Test error when input file doesn't exist."""
        output_db = tmp_path / "output.db"

        with (
            patch("sys.argv", ["e2s", "-i", "nonexistent.txt", "-o", str(output_db)]),
            pytest.raises(OSError, match=r"nonexistent.txt is not found"),
        ):
            main()

    def test_main_output_exists_without_overwrite(self, tmp_path: Path) -> None:
        """Test error when output file exists without overwrite flag."""
        input_file = tmp_path / "input.txt"
        output_db = tmp_path / "output.db"

        sample_data = """■test : テスト
"""
        input_file.write_text(sample_data, encoding="cp932")
        output_db.touch()  # Create empty output file

        with (
            patch("sys.argv", ["e2s", "-i", str(input_file), "-o", str(output_db)]),
            pytest.raises(OSError, match=r".*is already exist.*"),
        ):
            main()

    def test_main_output_exists_with_overwrite(self, tmp_path: Path) -> None:
        """Test successful overwrite when output file exists with overwrite flag."""
        input_file = tmp_path / "input.txt"
        output_db = tmp_path / "output.db"

        sample_data = """■test : テスト
"""
        input_file.write_text(sample_data, encoding="cp932")

        # Create initial output file with different data
        conn = sqlite3.connect(str(output_db))
        conn.execute("CREATE TABLE dummy (id INTEGER)")
        conn.commit()
        conn.close()

        with patch("sys.argv", ["e2s", "-i", str(input_file), "-o", str(output_db), "-O"]):
            main()

        # Verify new database was created (with word table, not dummy)
        conn = sqlite3.connect(str(output_db))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()

        assert "word" in tables
        assert "dummy" not in tables

    def test_main_with_custom_joiner(self, tmp_path: Path) -> None:
        """Test main function with custom joiner."""
        input_file = tmp_path / "input.txt"
        output_db = tmp_path / "output.db"

        sample_data = """■test : テスト◆説明1◆説明2
"""
        input_file.write_text(sample_data, encoding="cp932")

        with patch("sys.argv", ["e2s", "-i", str(input_file), "-o", str(output_db), "-j", " || "]):
            main()

        conn = sqlite3.connect(str(output_db))
        cur = conn.cursor()
        cur.execute("SELECT descriptions FROM word")
        descriptions = cur.fetchone()[0]
        conn.close()

        assert descriptions == "◆説明1 || ◆説明2"


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow from input to output."""
        input_file = tmp_path / "EIJIRO-1448.TXT"
        output_db = tmp_path / "eijiro.db"

        # Create realistic sample data
        sample_data = """■apple : リンゴ、アップル◆果物の一種■例：I like apples.◆私はリンゴが好きです。
■banana : バナナ◆黄色い果物
■cat : 猫、ネコ■動物
■dog : 犬、イヌ◆ペット◆家畜■例：Dogs are loyal.
■egg : 卵、たまご
"""
        input_file.write_text(sample_data, encoding="cp932")

        with patch("sys.argv", ["e2s", "-i", str(input_file), "-o", str(output_db)]):
            main()

        # Verify results
        conn = sqlite3.connect(str(output_db))
        cur = conn.cursor()

        # Check row count
        cur.execute("SELECT COUNT(*) FROM word")
        assert cur.fetchone()[0] == 5  # noqa: PLR2004

        # Check specific entries
        cur.execute("SELECT word, meaning FROM word WHERE word = 'apple'")
        row = cur.fetchone()
        assert row[0] == "apple"
        assert "リンゴ" in row[1]

        cur.execute("SELECT word FROM word ORDER BY id")
        words = [row[0] for row in cur.fetchall()]
        assert words == ["apple", "banana", "cat", "dog", "egg"]

        conn.close()
