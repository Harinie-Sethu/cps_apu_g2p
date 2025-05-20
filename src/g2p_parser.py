# src/g2p_parser.py

class G2PParser:
    """
    Loads common_apu.map and builds:
      - self.monolingual_map[lang]: only that language's grapheme→phone rules
      - self.common_map: all grapheme→phone rules merged across the 3 langs
    """
    def __init__(self, map_path):
        self.languages = ['Arabic','Persian','Urdu']
        self._load_mappings(map_path)

    def _load_mappings(self, map_path):
        # initialize
        self.monolingual_map = {lang:{} for lang in self.languages}
        self.common_map = {}

        with open(map_path, encoding='utf-8') as f:
            header = f.readline().strip().split('\t')
            langs = header[1:]  # ['Arabic','Persian','Urdu']
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) < 4: continue
                phone = parts[0]
                for i,lang in enumerate(langs):
                    grapheme = parts[i+1]
                    if grapheme and grapheme!='-':
                        self.monolingual_map[lang][grapheme] = phone
                        self.common_map[grapheme] = phone

        # prepare sorted lists for maximal‐munch
        self._mono_keys = {
            lang: sorted(self.monolingual_map[lang].keys(), key=lambda x: -len(x))
            for lang in self.languages
        }
        self._common_keys = sorted(self.common_map.keys(), key=lambda x: -len(x))

    def parse(self, word, lang, mode='common'):
        """
        word: a Unicode string of graphemes + diacritics
        lang: one of 'Arabic','Persian','Urdu'
        mode: 'monolingual' or 'common'
        returns: list of ARPAbet phones (strings)
        """
        if mode=='monolingual':
            mapping = self.monolingual_map[lang]
            keys = self._mono_keys[lang]
        else:
            mapping = self.common_map
            keys = self._common_keys

        phones = []
        i = 0
        while i < len(word):
            matched = False
            for g in keys:
                if word.startswith(g, i):
                    phones.append(mapping[g])
                    i += len(g)
                    matched = True
                    break
            if not matched:
                # unknown grapheme → UNK
                phones.append('UNK')
                i += 1
        return phones
