#!/usr/bin/env python

"A simple file indexer."

import codecs

class Dict:
    def __init__(self, dict_location, encoding=None):
        self.dict_location = dict_location
        self.encoding = encoding

        # Initialisation.

        self.index = self.get_index()

    def get_index(self):

        "Return a dictionary containing an index structure for the dict."

        if self.encoding is None:
            f = open(self.dict_location)
        else:
            f = codecs.open(self.dict_location, encoding=self.encoding)
        s = f.read()
        f.close()

        tokens = s.split()
        index = {}

        for token in tokens:
            slot = index
            for c in token:
                if not slot.has_key(c):
                    slot[c] = {}, []
                slot, words = slot[c]

            if token not in words:
                words.append(token)

        return index

    def find(self, pattern):

        "Find words beginning with the given 'pattern'."

        slot = self.index
        words = []

        for c in pattern:
            if not slot.has_key(c):
                return []
            slot, words = slot[c]

        results = []
        results += words
        results += self.get_all_words(slot)
        return results

    def get_all_words(self, slot):

        "Get all words under the given index 'slot'."

        all_words = []
        keys = slot.keys()
        keys.sort()
        for c in keys:
            this_slot, words = slot[c]
            all_words += words
            all_words += self.get_all_words(this_slot)
        return all_words

# vim: tabstop=4 expandtab shiftwidth=4
