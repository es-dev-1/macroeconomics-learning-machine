#!/usr/bin/env python3
"""Show how one section (or one guiding idea) connects to the rest of the course.

For a section: what it builds on and why (with the card where it is used and the card that explains
it), the whole chain of foundations further back, what it leads to, the practice tasks that train it,
and the guiding ideas (Leitideen) that run through it, with their connection questions and answers.
For a guiding idea: its stops in course order and its connection questions.

A tutor runs this before teaching a topic: to step down to the exact foundation when an answer
shows a gap, to ask connection questions, and to pick earlier topics that the current one rests on.

Usage (from the course folder):
  python3 ../../.claude/skills/learn/scripts/board-path.py deliverables/<board>.html data/knowledge-links.json <section id or guiding idea id> [--depth N]

A section can also be named by board and number, as in board-section.py (makro:3.6, maths:0.5).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from boardlib import ALIASES, Board  # noqa: E402


def edges(entry, key):
    out = []
    for e in entry.get(key, []):
        out.append({'id': e} if isinstance(e, str) else e)
    return out


def resolve(board, name):
    if name in board.frames:
        return name
    if ':' in name:
        bname, num = name.split(':', 1)
        bname = ALIASES.get(bname.lower(), bname.lower())
        for b in board.boards:
            if bname in (b['id'], b['label'].lower(), b['hash']):
                for fid in b['frames']:
                    if board.frames[fid]['num'] == num:
                        return fid
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board')
    ap.add_argument('links')
    ap.add_argument('target')
    ap.add_argument('--depth', type=int, default=3, help='how far back the chain of foundations goes (default 3)')
    args = ap.parse_args()
    board = Board(args.board)
    links = json.load(open(args.links, encoding='utf8'))
    sections = links.get('sections', {})
    concepts = {c['id']: c for c in links.get('concepts', [])}

    def card(cid):
        c = board.cards.get(cid)
        return f'"{c["title"]}" ({cid})' if c else cid

    def cards(ids):
        return '; '.join(card(c) for c in ids or [])

    def label(fid):
        return f'{board.label(fid)} [{fid}]'

    def print_concept(c, here=None):
        print(f'### {c["name"]} [{c["id"]}]')
        print(c.get('idea', ''))
        for k, s in enumerate(c.get('stops', []), 1):
            mark = '  <- this section' if s['section'] == here else ''
            print(f'{k}. {label(s["section"])}: {s.get("note", "")} Cards: {cards(s.get("cards"))}{mark}')
        for q in c.get('questions', []):
            print(f'- Connection question: {q["q"]}')
            print(f'  Model answer: {q.get("a", "")}')
        print()

    if args.target in concepts:
        print('# Guiding idea (Leitidee)\n')
        print_concept(concepts[args.target])
        return
    fid = resolve(board, args.target)
    if not fid:
        raise SystemExit(f'Unknown section or guiding idea: {args.target}')
    entry = sections.get(fid, {})
    print(f'# {label(fid)}')
    if entry.get('source'):
        print(f'Source: {entry["source"]}')
    print('Cards: ' + cards(board.frames[fid]['cards']))
    print()

    direct = edges(entry, 'builds_on')
    if direct:
        print('## Builds on')
        for e in direct:
            print(f'- {label(e["id"])}: {e.get("what", "")}')
            if e.get('how'):
                print(f'  How: {e["how"]}')
            if e.get('here') or e.get('there'):
                print(f'  Used on: {cards(e.get("here"))}. Explained on: {cards(e.get("there"))}.')
        print()

    # the chain further back, breadth first, each section once
    seen, frontier, chain = {fid} | {e['id'] for e in direct}, [e['id'] for e in direct], []
    for depth in range(2, args.depth + 1):
        nxt = []
        for f in frontier:
            for e in edges(sections.get(f, {}), 'builds_on'):
                if e['id'] not in seen:
                    seen.add(e['id'])
                    nxt.append(e['id'])
                    chain.append((depth, e, f))
        frontier = nxt
    if chain:
        print(f'## Further back (up to {args.depth} steps)')
        for depth, e, via in chain:
            print(f'- {label(e["id"])}: {e.get("what", "")} (needed by {via}; step {depth})')
        print()

    leads = [(f, e) for f, v in sections.items() for e in edges(v, 'builds_on') if e['id'] == fid]
    if leads:
        print('## Leads to')
        for f, e in leads:
            print(f'- {label(f)}: {e.get("what", "")}. Used on: {cards(e.get("here"))}')
        print()

    practice = [(f, e) for f, v in sections.items() for e in edges(v, 'practices') if e['id'] == fid]
    if practice:
        print('## Practice')
        for f, e in practice:
            print(f'- {label(f)}: {e.get("what", "")}. Task: {cards(e.get("here"))}')
        print()
    trains = edges(entry, 'practices')
    if trains:
        print('## This task block practices')
        for e in trains:
            print(f'- {label(e["id"])}: {e.get("what", "")}. Theory on: {cards(e.get("there"))}')
        print()

    through = [c for c in concepts.values() if any(s['section'] == fid for s in c.get('stops', []))]
    if through:
        print('## Guiding ideas through this section')
        for c in through:
            print_concept(c, here=fid)


if __name__ == '__main__':
    main()
