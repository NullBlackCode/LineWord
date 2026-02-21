from __future__ import annotations
import argparse
import gzip
import itertools
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Set
try:
    from tqdm import tqdm
    HAS_TQDM = True
except Exception:
    HAS_TQDM = False
DEFAULT_BASE_WORDS = ["admin", "user", "password", "root", "login", "test", "guest"]
DEFAULT_NUMBERS = ["", "1", "12", "123", "1234", "12345", "123456", "2020", "2021", "2022", "2023", "2024"]
DEFAULT_SYMBOLS = ["", "!", "@", "#", "$", "%", "&", "*", "-", "_", "."]
DEFAULT_SEPARATORS = ["", "", "", "", "-", "_"]
DEFAULT_LEET_MAP = {"a": ["a", "4", "@"], "e": ["e", "3"], "i": ["i", "1", "!"], "o": ["o", "0"], "s": ["s", "5", "$"], "t": ["t", "7"]}
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Advanced wordlist generator (English-only).")
    p.add_argument("-i", "--input", help="Input file with base words (one per line). If omitted, interactive or defaults are used.")
    p.add_argument("-m", "--mode", choices=["basic", "full"], default="basic",
                   help="Generation mode: 'basic' for common combos, 'full' for more permutations.")
    p.add_argument("-o", "--output", default="wordlist.txt", help="Output filename (use .gz to compress)")
    p.add_argument("--min-len", type=int, default=4, help="Minimum length of entries to include")
    p.add_argument("--max-len", type=int, default=64, help="Maximum length of entries to include")
    p.add_argument("--unique", action="store_true", help="Remove duplicates in final output")
    p.add_argument("--shuffle", action="store_true", help="Shuffle output before saving")
    p.add_argument("--leet", action="store_true", help="Include leet (basic) substitutions")
    p.add_argument("--years", nargs=2, type=int, metavar=("START", "END"), help="Append years in range START..END (inclusive)")
    p.add_argument("--numbers", nargs="*", default=None, help="Custom number tokens to append (space separated); default set used if omitted")
    p.add_argument("--symbols", nargs="*", default=None, help="Custom symbol tokens to insert; default set used if omitted")
    p.add_argument("--prefixes", nargs="*", default=["",], help="Prefixes to add")
    p.add_argument("--suffixes", nargs="*", default=["",], help="Suffixes to add")
    p.add_argument("--separators", nargs="*", default=None, help="Separators to use between word and number/symbol")
    p.add_argument("--limit", type=int, default=0, help="Stop after writing LIMIT entries (0 = no limit)")
    p.add_argument("--quiet", action="store_true", help="Minimal console output")
    p.add_argument("--interactive", action="store_true", help="Force interactive prompts to enter base words (overrides --input)")
    return p.parse_args()

def read_base_words(args: argparse.Namespace) -> List[str]:
    if args.interactive:
        print("Enter base words separated by commas, or press Enter to use defaults:")
        s = input("> ").strip()
        if s:
            return [w.strip() for w in s.split(",") if w.strip()]
        return DEFAULT_BASE_WORDS.copy()
    if args.input:
        p = Path(args.input)
        if not p.exists():
            print(f"Input file not found: {p}", file=sys.stderr)
            sys.exit(2)
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip()]
        return words if words else DEFAULT_BASE_WORDS.copy()
    if not sys.stdin.isatty():
        content = sys.stdin.read().strip()
        if content:
            return [line.strip() for line in content.splitlines() if line.strip()]
    return DEFAULT_BASE_WORDS.copy()

def generate_leet_variants(word: str, leet_map: dict = DEFAULT_LEET_MAP, max_variants: int = 32) -> Iterable[str]:
    letters = list(word.lower())
    pools = []
    for ch in letters:
        pool = leet_map.get(ch, [ch])
        pools.append(pool)
    count = 0
    for prod in itertools.product(*pools):
        yield "".join(prod)
        count += 1
        if count >= max_variants:
            return
def case_variants(word: str) -> List[str]:
    variants = {word, word.lower(), word.upper(), word.capitalize()}
    if "-" in word or "_" in word:
        parts = [p for p in re_split(word) if p]
        if parts:
            camel = "".join(p.capitalize() for p in parts)
            variants.add(camel)
    return list(variants)
def re_split(s: str) -> List[str]:
    import re
    return re.split(r"[\-\._\s]+", s)
def build_dates(start: int, end: int) -> List[str]:
    years = [str(y) for y in range(start, end + 1)]
    dates = []
    for y in years:
        dates.append(y)
        dates.append(f"01{y}")
        dates.append(f"{y}01")
        dates.append("0101")
        dates.append("1010")
    seen = set()
    out = []
    for d in dates:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out
def generate_combinations(
    base_words: Iterable[str],
    numbers: List[str],
    symbols: List[str],
    separators: List[str],
    prefixes: List[str],
    suffixes: List[str],
    year_tokens: List[str],
    use_leet: bool,
    mode: str,
    min_len: int,
    max_len: int,
) -> Iterable[str]:
    base_words = list(dict.fromkeys(w.strip() for w in base_words if w.strip()))
    if not base_words:
        return
    for base in base_words:
        variants = {base, base.lower(), base.upper(), base.capitalize()}
        if use_leet:
            for lv in generate_leet_variants(base):
                variants.add(lv)
                variants.add(lv.capitalize())
        for v in list(variants):
            for pre in prefixes:
                for suf in suffixes:
                    core = f"{pre}{v}{suf}"
                    if mode == "basic":
                        if min_len <= len(core) <= max_len:
                            yield core
                        for num in numbers:
                            for sep in separators:
                                c = f"{core}{sep}{num}" if num else core
                                if min_len <= len(c) <= max_len:
                                    yield c
                        for dt in year_tokens:
                            c = f"{core}{dt}"
                            if min_len <= len(c) <= max_len:
                                yield c
                    else:
                        if min_len <= len(core) <= max_len:
                            yield core
                        for sep in separators:
                            for num in numbers:
                                c = f"{core}{sep}{num}" if num else core
                                if min_len <= len(c) <= max_len:
                                    yield c
                                for sym in symbols:
                                    if sym:
                                        c2 = f"{core}{sym}{sep}{num}" if num else f"{core}{sym}"
                                        if min_len <= len(c2) <= max_len:
                                            yield c2
                        for dt in year_tokens:
                            c = f"{core}{dt}"
                            if min_len <= len(c) <= max_len:
                                yield c
                            for sym in symbols:
                                if sym:
                                    c2 = f"{core}{dt}{sym}"
                                    if min_len <= len(c2) <= max_len:
                                        yield c2
def write_output(lines: Iterable[str], out_path: Path, unique: bool, limit: int, quiet: bool) -> int:
    is_gz = out_path.suffix == ".gz"
    open_func = gzip.open if is_gz else open
    mode = "wt"
    seen: Set[str] = set() if unique else set()
    written = 0
    with open_func(out_path, mode, encoding="utf-8", errors="ignore") as f:
        for line in lines:
            if unique:
                if line in seen:
                    continue
                seen.add(line)
            f.write(line + "\n")
            written += 1
            if not quiet and (written % 1000 == 0):
                print(f"Wrote {written} entries...", end="\r", flush=True)
            if limit and written >= limit:
                break
    return written
def estimate_count(base_words: List[str], numbers: List[str], symbols: List[str],
                   prefixes: List[str], suffixes: List[str], yrs: List[str], mode: str) -> int:
    bw = len(base_words)
    n = len(numbers) if numbers else 1
    s = len(symbols) if symbols else 1
    p = len(prefixes) if prefixes else 1
    suf = len(suffixes) if suffixes else 1
    y = max(1, len(yrs))
    if mode == "basic":
        return bw * (p * suf) * (1 + n + y)
    else:
        return bw * (p * suf) * (1 + n * (1 + s) + y * (1 + s))
def main():
    args = parse_args()
    base_words = read_base_words(args)
    numbers = args.numbers if args.numbers is not None else DEFAULT_NUMBERS.copy()
    symbols = args.symbols if args.symbols is not None else DEFAULT_SYMBOLS.copy()
    separators = args.separators if args.separators is not None else DEFAULT_SEPARATORS.copy()
    prefixes = args.prefixes or [""]
    suffixes = args.suffixes or [""]
    if args.years:
        start, end = args.years
        year_tokens = build_dates(start, end)
    else:
        cy = datetime.now().year
        year_tokens = [str(cy), f"01{cy}", "0101", "1010", "2020"]
    min_len = args.min_len
    max_len = args.max_len
    estimate = estimate_count(base_words, numbers, symbols, prefixes, suffixes, year_tokens, args.mode)
    if not args.quiet:
        print("Base words:", len(base_words))
        print("Mode:", args.mode)
        print(f"Estimated output size (rough): ~{estimate:,} entries")
        print("Writing to:", args.output)
        if args.shuffle:
            print("Shuffle enabled (will buffer in memory).")
        if args.leet:
            print("Leet substitutions enabled.")
    gen = generate_combinations(
        base_words=base_words,
        numbers=numbers,
        symbols=symbols,
        separators=separators,
        prefixes=prefixes,
        suffixes=suffixes,
        year_tokens=year_tokens,
        use_leet=args.leet,
        mode=args.mode,
        min_len=min_len,
        max_len=max_len,
    )
    output_path = Path(args.output)
    if args.shuffle or args.unique:
        if not args.quiet:
            print("Collecting generated entries into memory (might be large)...")
        collected = []
        if HAS_TQDM and not args.quiet:
            gen_iter = tqdm(gen, desc="Generating", unit="items")
        else:
            gen_iter = gen
        for item in gen_iter:
            collected.append(item)
            if args.limit and len(collected) >= args.limit * 2:
                break
        if args.unique:
            collected = list(dict.fromkeys(collected))
        if args.shuffle:
            random.shuffle(collected)
        if args.limit:
            collected = collected[: args.limit]
        written = write_output(collected, output_path, unique=False, limit=0, quiet=args.quiet)
    else:
        if HAS_TQDM and not args.quiet:
            gen_iter = tqdm(gen, desc="Generating", unit="items")
        else:
            gen_iter = gen
        written = write_output(gen_iter, output_path, unique=args.unique, limit=args.limit, quiet=args.quiet)
    if not args.quiet:
        print(f"\nDone. Wrote {written} entries to {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
