# src/run_stageB.py
#!/usr/bin/env python3

import os, argparse, collections
from .g2p_parser import G2PParser
from .metrics     import levenshtein, phoneme_error_rate, top1_accuracy
from .run_stageA  import load_gold_refs, evaluate, LANG_CODES

def mine_rules(parser, raw_dir, min_freq):
    """
    Align each raw-word against the parser output, and collect (lang, grapheme, gold_IPA)
    whenever parser was off by edit-distance ≤2 and rule is unseen.
    Keep only pairs with frequency ≥ min_freq.
    """
    cand = collections.Counter()
    for lang, code in LANG_CODES.items():
        raw_p = os.path.join(raw_dir, f"{code}_arab_broad.tsv")
        if not os.path.exists(raw_p):
            continue

        words, refs = load_gold_refs(raw_p)
        for w, gold in zip(words, refs):
            pred = parser.parse(w, lang, mode='common')
            segs = parser.segment(w, lang, mode='common')
            # ensure same segmentation and token count
            if len(pred) != len(gold) or len(segs) != len(pred):
                continue

            for g, p, r in zip(segs, pred, gold):
                if p == r:
                    continue
                # single-token edit distance ≤ 2
                if levenshtein([p], [r]) <= 2:
                    # skip if already in map
                    if parser.common_map.get(g) != r:
                        cand[(lang, g, r)] += 1

    # filter out low-frequency
    return [(lang, g, r, cnt) for (lang, g, r), cnt in cand.items() if cnt >= min_freq]


def write_stageB_map(base_map, new_rules, out_map):
    """
    Append new rules to base_map, filling other language columns with '-'.
    """
    with open(base_map, encoding='utf-8') as f:
        header = f.readline()
        data   = f.readlines()

    # find current max index
    max_idx = 0
    for L in data:
        if L.strip() and not L.startswith('#'):
            parts = L.split('\t')
            try:
                max_idx = max(max_idx, int(parts[0]))
            except:
                pass
    idx = max_idx + 1

    appended = []
    for lang, g, ipa, cnt in new_rules:
        # build row: index,label,ipa,arabic,persian,urdu
        # label and ipa both get the IPA string
        row = [str(idx), ipa, ipa, '-', '-', '-']
        col_map = {'Arabic':3, 'Persian':4, 'Urdu':5}
        row[col_map[lang]] = g
        appended.append('\t'.join(row) + '\n')
        idx += 1

    with open(out_map, 'w', encoding='utf-8') as f:
        f.write(header)
        f.writelines(data)
        f.writelines(appended)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base_map', default='common_apu.map')
    p.add_argument('--raw_dir',  default='data/raw')
    p.add_argument('--gold_dir', default='data/gold')
    p.add_argument('--min_freq', type=int, default=5)
    p.add_argument('--out_map',  default='common_apu_stageB.map')
    args = p.parse_args()

    # 1) load base parser
    parser = G2PParser(args.base_map)

    # 2) mine new rules
    new_rules = mine_rules(parser, args.raw_dir, args.min_freq)
    print(f"Mined {len(new_rules)} rules (freq ≥{args.min_freq})")

    # 3) write enriched map
    write_stageB_map(args.base_map, new_rules, args.out_map)
    print(f"→ Written enriched map to {args.out_map}")

    # 4) re-evaluate with Stage B map
    print("\n=== Stage B Evaluation ===")
    for lang in ('Arabic','Persian','Urdu'):
        code = LANG_CODES[lang]
        # # manual set
        # man_p = os.path.join(args.gold_dir, f"{lang.lower()}_manual.tsv")
        # w_m, r_m = load_gold_refs(man_p)
        # res_m = evaluate(lang, G2PParser(args.out_map), w_m, r_m)
        # print(f"\n>> {lang} – manual set")
        # for mode, v in res_m.items():
        #     print(f"   {mode:12s} PER {v['PER']:.3f}   Top-1 Acc {v['Acc']:.2%}")

        # WikiTron IPA-broad
        raw_p = os.path.join(args.raw_dir, f"{code}_arab_broad.tsv")
        if os.path.exists(raw_p):
            w_w, r_w = load_gold_refs(raw_p)
            res_w = evaluate(lang, G2PParser(args.out_map), w_w, r_w)
            print(f"\n>> {lang} – WikiTron IPA-broad")
            for mode, v in res_w.items():
                print(f"   {mode:12s} PER {v['PER']:.3f}   Top-1 Acc {v['Acc']:.2%}")

if __name__ == '__main__':
    main()
