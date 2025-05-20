#!/usr/bin/env python3
# src/run_epitran.py

import os
import argparse
import epitran

from .metrics import phoneme_error_rate, top1_accuracy

# Epitran tags for each language
LANG_TAGS = {
    'Arabic':  'ara-Arab',
    'Persian': 'fas-Arab',
    'Urdu':    'urd-Arab',
}

# file prefix in data/raw: <iso>_arab_broad.tsv
FILE_SUFFIX = '_arab_broad.tsv'

def load_gold(path):
    """
    Load a TSV of word<TAB>space-separated-IPA
    Returns:
      words:   [str,…]
      gold:    [list(codepoints)…]
    """
    words, gold = [], []
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            w, ipa_seq = ln.split('\t')
            words.append(w)
            # collapse the gold tokens into one string, then split into codepoints
            joined = ''.join(ipa_seq.split())
            gold.append(list(joined))
    return words, gold

def evaluate_with_epitran(tag, words, gold):
    """
    tag:   Epitran code e.g. 'ara-Arab'
    words: list of orthographic words
    gold:  list of lists of gold codepoints
    """
    epi = epitran.Epitran(tag)
    hyps = []
    for w in words:
        pred = epi.transliterate(w)
        # split each Unicode char as a token
        hyps.append(list(pred))
    per = phoneme_error_rate(gold, hyps)
    acc = top1_accuracy( gold, hyps)
    return per, acc

def main():
    p = argparse.ArgumentParser()
    p.add_argument(
      '--raw_dir',
      default='data/raw',
      help="Directory holding the WikiTron IPA-broad TSVs"
    )
    args = p.parse_args()

    for lang, tag in LANG_TAGS.items():
        iso = tag.split('-')[0]
        path = os.path.join(args.raw_dir, iso + FILE_SUFFIX)
        if not os.path.exists(path):
            print(f"[!] missing file for {lang}: {path}")
            continue

        words, gold = load_gold(path)
        per, acc = evaluate_with_epitran(tag, words, gold)
        print(f"{lang:7s} → PER: {per:.3f}   Top-1 Acc: {acc:.2%}")

if __name__ == '__main__':
    main()
