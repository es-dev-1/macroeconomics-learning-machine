"""Shared reader for a learning board (one HTML file with boards, sections, and cards).

A board file holds, in its page script, a FRAMES array (the sections, each with card columns) and
a SPACES array (the boards, each with rows of sections). The cards are <article class="card">
elements. This module reads all three without running the page.
"""
import html
import json
import re
from html.parser import HTMLParser


# Other names learners and cards use for the boards
ALIASES = {'mathe': 'math', 'mikro': 'micro', 'makroökonomie': 'macro', 'tutorium': 'tut'}


class Board:
    def __init__(self, path):
        self.path = path
        text = open(path, encoding='utf8').read()
        self.frames = {}      # frame id -> {id, num, title, bare, cards: [card ids], board}
        self.boards = []      # [{id, label, hash, frames: [frame ids]}]
        self.cards = {}       # card id -> {id, kind, title, html, frame}
        self._read_frames(text)
        self._read_boards(text)
        self._read_cards(text)

    def _read_frames(self, text):
        m = re.search(r'const FRAMES = \[\n(.*?)\n  \];', text, re.S)
        if not m:
            raise SystemExit('No FRAMES array found: is this a learning board file?')
        line_re = re.compile(
            r"\{ id: '([^']+)',(?: bare: (true),)?(?: num: '([^']*)',)? title: '((?:[^'\\]|\\.)*)', columns: (\[.*\]) \},?\s*$")
        for line in m.group(1).split('\n'):
            fm = line_re.search(line)
            if not fm:
                continue
            fid, bare, num, title, cols = fm.groups()
            columns = json.loads(cols.replace("'", '"'))
            self.frames[fid] = {
                'id': fid, 'num': num or '', 'title': title.replace("\\'", "'"), 'bare': bool(bare),
                'cards': [c for col in columns for c in col], 'board': None,
            }

    def _read_boards(self, text):
        m = re.search(r'const SPACES = \[\n(.*?)\n  \];', text, re.S)
        if not m:
            raise SystemExit('No SPACES array found: is this a learning board file?')
        hashes = {}
        hm = re.search(r'const BOARD_HASH = \{([^}]*)\}', text)
        if hm:
            hashes = dict(re.findall(r"(\w+): '([\w-]+)'", hm.group(1)))
        for bid, label, rows in re.findall(r"\{ id: '(\w+)', label: '([^']+)',.*?rows: (\[\[.*?\]\]) \}", m.group(1), re.S):
            frame_ids = [f for row in json.loads(rows.replace("'", '"')) for f in row]
            self.boards.append({'id': bid, 'label': label, 'hash': hashes.get(bid, bid), 'frames': frame_ids})
            for fid in frame_ids:
                if fid in self.frames:
                    self.frames[fid]['board'] = bid

    def _read_cards(self, text):
        owner = {c: f['id'] for f in self.frames.values() for c in f['cards']}
        for cid, body in re.findall(r'<article class="card" data-id="([^"]+)"[^>]*>(.*?)</article>', text, re.S):
            kind = re.search(r'class="card-kind">([^<]*)<', body)
            title = re.search(r'class="card-title">(.*?)</span>', body, re.S)
            self.cards[cid] = {
                'id': cid, 'kind': html.unescape(kind.group(1)).strip() if kind else '',
                'title': html.unescape(re.sub(r'<[^>]+>', '', title.group(1))).strip() if title else '',
                'html': body, 'frame': owner.get(cid),
            }

    def board(self, bid):
        return next((b for b in self.boards if b['id'] == bid), None)

    def label(self, fid):
        """Readable name of a section: 'Makro 3.5 Das Solow-Wachstumsmodell'."""
        f = self.frames[fid]
        b = self.board(f['board'])
        parts = [b['label'] if b else '', f['num'], f['title']]
        return ' '.join(p for p in parts if p)

    def resolve(self, ref):
        """Turn 'f-ma6', 'ma6-modell', or 'makro:3.5' into ('frame' | 'card', id)."""
        if ref in self.frames:
            return 'frame', ref
        if ref in self.cards:
            return 'card', ref
        if ':' in ref:
            bname, num = ref.split(':', 1)
            bname = ALIASES.get(bname.lower(), bname.lower())
            for b in self.boards:
                if bname in (b['id'].lower(), b['label'].lower(), b['hash'].lower()):
                    for fid in b['frames']:
                        if self.frames[fid]['num'] == num:
                            return 'frame', fid
        return None, None


class _Text(HTMLParser):
    """HTML of a card body to readable plain text. Formulas stay as TeX."""
    SKIP = {'svg', 'script', 'style', 'header'}
    # parts of interactive cards that only make sense on the board (sliders, buttons, chart boxes, live output)
    SKIP_CLASSES = {'controls', 'btn-row', 'chart', 'legend', 'live', 'seg-ctrl', 'rz', 'grip'}
    BLOCK = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'table', 'ul', 'ol', 'details', 'tr', 'label'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        void = tag in ('br', 'input', 'img', 'hr', 'wbr', 'col', 'meta', 'link')
        classes = set((dict(attrs).get('class') or '').split())
        if self.skip or tag in self.SKIP or classes & self.SKIP_CLASSES:
            self.skip += 0 if void else 1
            return
        if 'ro-val' in classes:
            self.out.append(': ')
            return
        if 'ro' in classes:
            self.out.append('\n- ')
            return
        if tag == 'li':
            self.out.append('\n- ')
        elif tag in ('td', 'th'):
            self.out.append(' | ')
        elif tag == 'br' or tag in self.BLOCK:
            self.out.append('\n')
        elif tag == 'summary':
            self.out.append('\n[')

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= 1
            return
        if tag == 'summary':
            self.out.append(']\n')
        elif tag in self.BLOCK:
            self.out.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.out.append(re.sub(r'\s+', ' ', data))


def card_text(card):
    p = _Text()
    p.feed(card['html'])
    lines = [re.sub(r' +', ' ', ln).strip() for ln in ''.join(p.out).split('\n')]
    lines = [ln.lstrip('| ').strip() if ln.startswith('|') else ln for ln in lines]
    out = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    return '\n'.join(out).strip()
