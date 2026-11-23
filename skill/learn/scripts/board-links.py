#!/usr/bin/env python3
"""Write the connections from knowledge-links.json into the learning board.

The board shows connections in three places: at the foot of each card ("Grundlage" leads to the card
that explains a foundation, "Gebraucht in" back to where it is used), in the focus panel, and in the
knowledge network (key W). It reads them from objects between two marker comments in its page
script. This script regenerates those objects, so the links file stays the one place where
connections are kept:

- LINKS: per section its source, what it builds on, and what it practices. Each connection may carry
  `what` (the knowledge carried over), `how` (how it is used), `here` (cards in this section that use
  it) and `there` (cards in the other section that explain it). A bare section id still works.
- CONCEPTS: the guiding ideas (Leitideen) that run through the course, with their stops.
- PARTS: the columns of the knowledge network: a range of sections on one board (first, last) or a
  list of ids, each with a label; join puts a part under the one before it.

If the board has the markers <!-- CONCEPT-CARDS-START frame=<frame id> --> and <!-- CONCEPT-CARDS-END -->,
the script also writes one card per guiding idea between them and sets that frame's columns.

Usage:
  python3 board-links.py <board.html> <knowledge-links.json>

Run it after every change to the links file, together with board-map.py, then republish the board.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from boardlib import Board  # noqa: E402

START = '/* KNOWLEDGE-LINKS-START'
END = '/* KNOWLEDGE-LINKS-END */'
CARDS_START = re.compile(r'<!-- CONCEPT-CARDS-START frame=([\w-]+) -->\n')
CARDS_END = '<!-- CONCEPT-CARDS-END -->'
QUIZ = {'Frage', 'Question'}
TEXT = {
    True: {'kind': 'Leitidee', 'q': 'Verbindungsfrage', 'answer': 'Antwort zeigen', 'net': 'Im Wissensnetz zeigen'},
    False: {'kind': 'Guiding idea', 'q': 'Connection question', 'answer': 'Show answer', 'net': 'Show in the network'},
}


def esc(s):
    return html.escape(str(s), quote=True)


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    board_path, links_path = sys.argv[1], sys.argv[2]
    board = Board(board_path)
    links = json.load(open(links_path, encoding='utf8'))
    errors = []

    def check_cards(where, ids, fid):
        ok = []
        for c in ids or []:
            if c not in board.cards:
                errors.append(f'{where}: unknown card {c}')
            elif c not in board.frames[fid]['cards']:
                errors.append(f'{where}: card {c} is not in section {fid}')
            else:
                ok.append(c)
        return ok

    out = {}
    for fid, entry in links.get('sections', {}).items():
        if fid not in board.frames:
            errors.append(f'unknown section {fid}')
            continue
        item = {}
        if entry.get('source'):
            item['s'] = entry['source']
        for key, short in (('builds_on', 'b'), ('practices', 'p')):
            edges = []
            for k, e in enumerate(entry.get(key, [])):
                e = {'id': e} if isinstance(e, str) else e
                other, where = e.get('id'), f'{fid}.{key}[{k}]'
                if other not in board.frames:
                    errors.append(f'{where}: unknown section {other}')
                    continue
                edge = {'i': other}
                for src, dst in (('what', 'w'), ('how', 'h')):
                    if e.get(src):
                        edge[dst] = e[src]
                here, there = check_cards(where + '.here', e.get('here'), fid), check_cards(where + '.there', e.get('there'), other)
                if here:
                    edge['a'] = here
                if there:
                    edge['t'] = there
                edges.append(edge if len(edge) > 1 else other)
            if edges:
                item[short] = edges
        if item:
            out[fid] = item

    text = open(board_path, encoding='utf8').read()
    concepts = links.get('concepts', [])
    cm = CARDS_START.search(text)
    concept_frame = cm.group(1) if cm and concepts else None
    cards_out = []
    for k, c in enumerate(concepts):
        where = f'concepts[{k}] {c.get("id")}'
        stops = []
        for s in c.get('stops', []):
            if s.get('section') not in board.frames:
                errors.append(f'{where}: unknown section {s.get("section")}')
                continue
            stops.append({'f': s['section'], 'c': check_cards(where, s.get('cards'), s['section']), 'n': s.get('note', '')})
        item = {'i': c['id'], 'n': c['name'], 'd': c.get('idea', ''), 's': stops,
                'q': [{'q': q['q'], 'a': q.get('a', '')} for q in c.get('questions', [])]}
        if concept_frame:
            item['k'] = 'li-' + c['id']
        cards_out.append(item)
    parts = []
    for p in links.get('parts', []):
        ids = p.get('ids')
        if isinstance(ids, list):
            bad = [i for i in ids if i not in board.frames]
        else:
            bad = [i for i in (p.get('first'), p.get('last')) if i not in board.frames]
        if bad:
            errors.append(f'part {p.get("label")}: unknown sections {bad}')
            continue
        parts.append({k: p[k] for k in ('label', 'first', 'last', 'ids', 'join') if k in p})
    if errors:
        raise SystemExit('Problems in the links file:\n  ' + '\n  '.join(errors))

    def js(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')

    m = re.search(re.escape(START) + r'.*?\*/\n(.*?)' + re.escape(END), text, re.S)
    if not m:
        raise SystemExit('The board has no KNOWLEDGE-LINKS markers: it does not support connections yet.')
    block = f'  const LINKS = {js(out)};\n  const CONCEPTS = {js(cards_out)};\n  const PARTS = {js(parts)};\n  '
    text = text[:m.start(1)] + block + text[m.end(1):]

    if concept_frame:
        if concept_frame not in board.frames:
            raise SystemExit(f'The concept frame {concept_frame} is not in FRAMES.')
        bid = board.frames[concept_frame]['board']
        de = bool(re.search(r"\{ id: '%s', label: '[^']+', de: true" % re.escape(bid or ''), text))
        t = TEXT[de]
        html_cards, heights = [], []
        for c, item in zip(concepts, cards_out):
            lines = [f'<article class="card" data-id="{item["k"]}" data-w="460">',
                     f'  <header class="card-head"><span class="card-kind">{t["kind"]}</span><span class="card-title">{esc(c["name"])}</span><span class="grip" aria-hidden="true"></span></header>',
                     '  <div class="card-body prose">',
                     f'    <p>{esc(c.get("idea", ""))}</p>',
                     '    <ol class="thread">']
            for s in item['s']:
                f = board.frames[s['f']]
                b = board.board(f['board'])
                lab = ' '.join(x for x in (b['label'] if b else '', f['num']) if x)
                lines.append(f'      <li><button type="button" class="goto" data-goto="{s["f"]}" data-cards="{" ".join(s["c"])}" style="--c: var(--bd-{f["board"]})">'
                             f'<span class="bd">{esc(lab)}</span> {esc(f["title"])}</button><span class="stop-note">{esc(s["n"])}</span></li>')
            lines.append('    </ol>')
            for q in item['q']:
                lines.append(f'    <div class="bridge"><p class="q-text">{t["q"]}: {esc(q["q"])}</p><details class="ans"><summary>{t["answer"]}</summary>'
                             f'<div class="a"><p>{esc(q["a"])}</p></div></details></div>')
            lines.append(f'    <div class="btn-row"><button type="button" class="btn quiet" data-net-concept="{esc(c["id"])}">{t["net"]}</button></div>')
            lines += ['  </div>', '  <span class="rz" aria-hidden="true"></span>', '</article>', '']
            html_cards.append('\n'.join(lines))
            heights.append(120 + len(c.get('idea', '')) / 2.2 + 52 * len(item['s']) + 70 * len(item['q']))
        # three columns in reading order, about equally tall
        n_cols = 3 if len(heights) >= 6 else 1
        target, cols, acc = sum(heights) / n_cols, [[]], 0
        for item, hgt in zip(cards_out, heights):
            if acc >= target * len(cols) - hgt / 2 and len(cols) < n_cols and cols[-1]:
                cols.append([])
            cols[-1].append(item['k'])
            acc += hgt
        cm = CARDS_START.search(text)
        end = text.index(CARDS_END, cm.end())
        text = text[:cm.end()] + '\n'.join(html_cards) + text[end:]
        line_re = re.compile(r"^(    \{ id: '%s',.*?columns: )\[.*\]( \},?)$" % re.escape(concept_frame), re.M)
        if not line_re.search(text):
            raise SystemExit(f'Could not find the FRAMES line of {concept_frame}.')
        text = line_re.sub(lambda mm: mm.group(1) + json.dumps(cols).replace('"', "'") + mm.group(2), text, count=1)

    open(board_path, 'w', encoding='utf8').write(text)
    n_edges = sum(len(v.get('b', [])) + len(v.get('p', [])) for v in out.values())
    print(f'wrote {len(out)} sections ({n_edges} connections), {len(cards_out)} guiding ideas, {len(parts)} network parts'
          + (f', {len(cards_out)} cards in {concept_frame}' if concept_frame else '') + f' into {os.path.basename(board_path)}')


if __name__ == '__main__':
    main()
