import re
from .data import LETTERS
_ANS = re.compile(r"ANSWER\s*:\s*([A-J]|NS)\b", re.I)
_CONF = re.compile(r"CONFIDENCE\s*:\s*(\d{1,3})", re.I)

def parse_response(text, n_options):
    """Return (answer, confidence) where answer in {'A'.., 'NS', None(unparseable)}; confidence in [0,1] or None."""
    m = _ANS.search(text or "")
    ans = None
    if m:
        a = m.group(1).upper()
        ans = a if (a == "NS" or a in LETTERS[:n_options]) else None
    c = _CONF.search(text or "")
    conf = min(int(c.group(1)), 100) / 100 if c else None
    return ans, conf
