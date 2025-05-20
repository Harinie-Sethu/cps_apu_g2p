#!/usr/bin/env python3
import os, argparse
from g2p_parser import G2PParser
from metrics     import phoneme_error_rate, top1_accuracy

def load_gold_refs(path):
    """
    Expects TSV: word<TAB>space-separated-ARPAbet
    Returns: (words, [ [phones...], ... ])
    """
    words, refs = [], []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            w,ph_str = line.split('\t')
            words.append(w)
            refs.append(ph_str.split())
    return words, refs

def evaluate_one(lang, parser, words, refs):
    results = {}
    for mode in ['monolingual','common']:
        hyps = [parser.parse(w,lang,mode) for w in words]
        per = phoneme_error_rate(refs, hyps)
        acc = top1_accuracy(refs, hyps)
        results[mode] = {'PER':per,'Acc':acc}
    return results

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--map',      default='common_apu.map')
    ap.add_argument('--gold_dir', default='data/gold')
    args = ap.parse_args()

    g2p = G2PParser(args.map)
    for lang in ['Arabic','Persian','Urdu']:
        gold_path = os.path.join(args.gold_dir,f"{lang.lower()}_manual.tsv")
        words, refs = load_gold_refs(gold_path)
        res = evaluate_one(lang, g2p, words, refs)
        print(f"\n== {lang} ==")
        for mode, m in res.items():
            print(f"  {mode:12s}  PER: {m['PER']:.3f}  Top-1 Acc: {m['Acc']:.2%}")

if __name__=='__main__':
    main()
