#!/usr/bin/env python3
import os, argparse
from .g2p_parser import G2PParser
from .metrics     import phoneme_error_rate, top1_accuracy

LANG_CODES = {'Arabic':'ara', 'Persian':'fas', 'Urdu':'urd'}

def load_gold_refs(path):
    words, refs = [], []
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            w, ipa_seq = ln.split('\t')
            words.append(w)
            refs.append(ipa_seq.split())
    return words, refs

def evaluate(lang, parser, words, refs):
    out = {}
    for mode in ('monolingual','common'):
        hyps = [parser.parse(w, lang, mode) for w in words]
        out[mode] = {
            'PER': phoneme_error_rate(refs, hyps),
            'Acc': top1_accuracy(refs, hyps)
        }
    return out

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--map',     default='common_apu.map')
    p.add_argument('--gold_dir',default='data/gold')
    p.add_argument('--raw_dir', default='data/raw')
    args = p.parse_args()

    parser = G2PParser(args.map)

    for lang in ('Arabic','Persian','Urdu'):
        code = LANG_CODES[lang]

        wiki_path = os.path.join(args.raw_dir, f"{code}_arab_broad.tsv")
        if os.path.exists(wiki_path):
            words_w, refs_w = load_gold_refs(wiki_path)
            res_w = evaluate(lang, parser, words_w, refs_w)
            print(f"\n>> {lang} – WikiTron IPA-broad")
            for mode, v in res_w.items():
                print(f"   {mode:12s} PER {v['PER']:.3f}   Top-1 Acc {v['Acc']:.2%}")

if __name__=='__main__':
    main()
