import re

def strip_possessive(s):
    ptrn = r'\b(your|my)\b'
    strip_string = re.sub(ptrn, '', s).strip()
    return strip_string


def extract_relevant_semantic(x):
    try:
        return len(x['object']['text'])
    except:
        return 0
