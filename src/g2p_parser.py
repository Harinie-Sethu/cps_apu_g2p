# # src/g2p_parser.py

# class G2PParser:
#     """
#     Loads an IPA‐centric common_apu.map and builds:
#       - self.monolingual_map[lang]: grapheme→IPA rules for that language
#       - self.common_map:      grapheme→IPA rules merged across all languages
#     """

#     def __init__(self, map_path):
#         self.languages = ['Arabic','Persian','Urdu']
#         self._load_mappings(map_path)

#     def _load_mappings(self, map_path):
#         # initialize containers
#         self.monolingual_map = {lang: {} for lang in self.languages}
#         self.common_map      = {}

#         with open(map_path, encoding='utf-8') as f:
#             # read and parse header (strip leading '#' if present)
#             header = f.readline().lstrip('#').strip().split('\t')
#             # locate columns
#             idx_ipa   = header.index('ipa')
#             lang_cols = {lang: header.index(lang.lower()) for lang in self.languages}
#             max_col   = max(lang_cols.values())

#             for line in f:
#                 line = line.strip()
#                 # skip blank or comment lines
#                 if not line or line.startswith('#'):
#                     continue

#                 parts = line.split('\t')
#                 # if row too short to contain ipa or all language columns, skip
#                 if len(parts) <= idx_ipa or len(parts) <= max_col:
#                     continue

#                 ipa = parts[idx_ipa].strip()
#                 # skip if no ipa or placeholder
#                 if not ipa or ipa == '-':
#                     continue

#                 # for each language, split comma-lists of graphemes
#                 for lang, col in lang_cols.items():
#                     cell = parts[col].strip()
#                     if not cell or cell == '-':
#                         continue

#                     for grapheme in cell.split(','):
#                         g = grapheme.strip()
#                         if not g:
#                             continue
#                         # assign rule
#                         self.monolingual_map[lang][g] = ipa
#                         self.common_map[g]            = ipa

#         # build maximal-munch lists
#         self._mono_keys = {
#             lang: sorted(self.monolingual_map[lang].keys(), key=lambda x: -len(x))
#             for lang in self.languages
#         }
#         self._common_keys = sorted(self.common_map.keys(), key=lambda x: -len(x))

#     def parse(self, word, lang, mode='common'):
#         """
#         word: Unicode string of graphemes+diacritics
#         lang: 'Arabic'|'Persian'|'Urdu'
#         mode: 'monolingual' or 'common'
#         returns: list of IPA tokens
#         """
#         if mode == 'monolingual':
#             mapping = self.monolingual_map[lang]
#             keys    = self._mono_keys[lang]
#         else:
#             mapping = self.common_map
#             keys    = self._common_keys

#         tokens = []
#         i = 0
#         while i < len(word):
#             matched = False
#             for g in keys:
#                 if word.startswith(g, i):
#                     tokens.append(mapping[g])
#                     i += len(g)
#                     matched = True
#                     break
#             if not matched:
#                 tokens.append('UNK')
#                 i += 1
#         return tokens


## stage B
# src/g2p_parser.py

class G2PParser:
    """
    IPA-based CPS–APU parser.
    Builds:
      - monolingual_map[lang]: grapheme → IPA
      - common_map:            grapheme → IPA (all langs merged)
    """

    def __init__(self, map_path):
        self.languages = ['Arabic','Persian','Urdu']
        self._load_mappings(map_path)

    def _load_mappings(self, map_path):
        self.monolingual_map = {lang: {} for lang in self.languages}
        self.common_map      = {}

        with open(map_path, encoding='utf-8') as f:
            header = f.readline().lstrip('#').strip().split('\t')
            idx_ipa   = header.index('ipa')
            lang_cols = {lang: header.index(lang.lower()) for lang in self.languages}
            max_col   = max(lang_cols.values())

            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) <= max(idx_ipa, max_col):
                    continue
                ipa = parts[idx_ipa].strip()
                if ipa == '-' or not ipa:
                    continue

                # a cell may contain multiple comma-separated graphemes
                for lang, col in lang_cols.items():
                    cell = parts[col].strip()
                    if cell == '-' or not cell:
                        continue
                    for g in cell.split(','):
                        g = g.strip()
                        if not g:
                            continue
                        self.monolingual_map[lang][g] = ipa
                        self.common_map[g]            = ipa

        # maximal-munch order for segmentation + parsing
        self._mono_keys   = {
            lang: sorted(self.monolingual_map[lang], key=lambda x: -len(x))
            for lang in self.languages
        }
        self._common_keys = sorted(self.common_map, key=lambda x: -len(x))

    def segment(self, word, lang, mode='common'):
        """
        Returns the list of grapheme segments for `word`.
        """
        keys = self._mono_keys[lang] if mode=='monolingual' else self._common_keys
        segs = []
        i = 0
        while i < len(word):
            for g in keys:
                if word.startswith(g, i):
                    segs.append(g)
                    i += len(g)
                    break
            else:
                segs.append(word[i])
                i += 1
        return segs

    def parse(self, word, lang, mode='common'):
        """
        Segments + maps to IPA tokens.
        Returns: list of IPA strings, one per segment.
        """
        mapping = (self.monolingual_map[lang]
                   if mode=='monolingual' else
                   self.common_map)
        keys    = (self._mono_keys[lang]
                   if mode=='monolingual' else
                   self._common_keys)

        toks = []
        i = 0
        while i < len(word):
            for g in keys:
                if word.startswith(g, i):
                    toks.append(mapping[g])
                    i += len(g)
                    break
            else:
                toks.append('UNK')
                i += 1
        return toks
