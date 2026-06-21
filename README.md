### LineWord for wordlist.txt
Wordlist creation script for all kinds of cyber cracks and strong brute forces.
``

This script is a single file and is very strong, fast and very simple.

> It is written in Python and is not encrypted.
You can give it `the keyword file to create the wordlist` yourself or enter it manually or use the default.

``


> usage: lineword.py [-h] [-i INPUT] [-m {basic,full}] [-o OUTPUT] [--min-len MIN_LEN]
                   [--max-len MAX_LEN] [--unique] [--shuffle] [--leet] [--years START END]
                   [--numbers [NUMBERS ...]] [--symbols [SYMBOLS ...]]
                   [--prefixes [PREFIXES ...]] [--suffixes [SUFFIXES ...]]
                   [--separators [SEPARATORS ...]] [--limit LIMIT] [--quiet] [--interactive]

Advanced wordlist generator (English-only).

 options:
  -h, --help            show this help message and exit
  -i, --input INPUT     Input file with base words (one per line). If omitted, interactive or
                        defaults are used.
  -m, --mode {basic,full}
                        Generation mode: 'basic' for common combos, 'full' for more
                        permutations.
  -o, --output OUTPUT   Output filename (use .gz to compress)
  --min-len MIN_LEN     Minimum length of entries to include
  --max-len MAX_LEN     Maximum length of entries to include
  --unique              Remove duplicates in final output
  --shuffle             Shuffle output before saving
  --leet                Include leet (basic) substitutions
  --years START END     Append years in range START..END (inclusive)
  --numbers [NUMBERS ...]
                        Custom number tokens to append (space separated); default set used if
                        omitted
  --symbols [SYMBOLS ...]
                        Custom symbol tokens to insert; default set used if omitted
  --prefixes [PREFIXES ...]
                        Prefixes to add
  --suffixes [SUFFIXES ...]
                        Suffixes to add
  --separators [SEPARATORS ...]
                        Separators to use between word and number/symbol
  --limit LIMIT         Stop after writing LIMIT entries (0 = no limit)
  --quiet               Minimal console output
  --interactive         Force interactive prompts to enter base words (overrides --input)


![Shot 0001](https://github.com/user-attachments/assets/428e3503-a471-4c5d-8265-1b384aafe4c7)
