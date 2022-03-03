from collections import defaultdict
from itertools import chain


def get_freq(s):
    '''
    >>> get_freq('2')
    2.0
    >>> get_freq('2%')
    0.02
    '''
    if s[-1] == '%':
        return float(s[:-1]) * 0.01
    else:
        return float(s)

# Traditional Chinese to Simplified Chinese


with open('TSCharacters.txt') as f:
    d_t2s = {a: bx.split(' ')
             for line in f for a, bx in (line.rstrip().split('\t'),)}

# rime-cantonese dictionary data

d_trad = defaultdict(list)
d_simp = defaultdict(list)

with open('jyut6ping3.dict.yaml') as f:
    # skip the yaml header
    for line in f:
        if line == '...\n':
            break
    next(f)

    # dictionary data
    for line in f:
        if line[0] != '#':  # skip comments
            parts = line.rstrip().split('\t')
            char = parts[0]
            if len(char) == 1:  # restrict to single character
                # remove pronunciation with low frequency
                if len(parts) == 2 or get_freq(parts[2]) > 0.07:
                    # replace if a character has two syllables
                    jyutping = parts[1].replace(' ', '')

                    # the original Traditional Chinese character
                    d_trad[char].append(jyutping)

                    try:
                        for ch in d_t2s[char]:
                            # Simplified Chinese character
                            d_simp[ch].append(jyutping)
                    except KeyError:
                        pass

# override

with open('override.txt') as f1, open('radicals.txt') as f2:
    d_override = {a: bx.split(' ') for line in chain(f1, f2)
                  for a, bx in (line.rstrip().split('\t'),)}

# combine dictionaries

d = {**d_simp, **d_trad, **d_override}

res = []
error_keys = set()

with open('liangfen.txt') as f:
    for line in f:
        ch = line[0]

        try:
            if len(line) == 5:
                word_l = line[2]
                word_r = line[3]
                for jyutping_l in d[word_l]:
                    for jyutping_r in d[word_r]:
                        res.append((ch, jyutping_l + jyutping_r))
            else:  # len(line) == 4
                word = line[2]
                for jyutping in d[word]:
                    res.append((ch, jyutping))
        except KeyError as e:
            cause = e.args[0]
            error_keys.add(cause)

if error_keys:
    with open('missing.log', 'w') as f:
        for k in error_keys:
            print(k, file=f)

with open('../loengfan.dict.yaml', 'w') as f:
    for l, r in res:
        print(l, r, sep='\t', file=f)
