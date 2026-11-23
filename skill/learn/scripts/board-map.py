#!/usr/bin/env python3
"""Build the knowledge map of a learning board.

The map is a compact Markdown file that lists every board, section, and card title, plus the
connections between sections: what a section builds on, what it leads to, and which practice
tasks belong to it. A tutor reads the map instead of the (very large) board file.

Usage:
  python3 board-map.py <board.html> [--links knowledge-links.json] [--out knowledge-map.md]

The links file holds the curated connections (see references/course-folder.md). The script
checks it against the board: an id that is not a section on the board is an error (exit 1),
a course section without an entry is a warning.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from boardlib import Board  # noqa: E402

QUESTION_KINDS = {'Frage', 'Question'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board')
    ap.add_argument('--links')
    ap.add_argument('--out')
    args = ap.parse_args()

    board = Board(args.board)
    links = json.load(open(args.links, encoding='utf8')) if args.links else {}
    sections = links.get('sections', {})
    course_boards = links.get('course_boards', [])

    errors, warnings = [], []
    builds_on, practices, what = {}, {}, {}
    for fid, entry in sections.items():
        if fid not in board.frames:
            errors.append(f'links file names an unknown section: {fid}')
            continue
        for key, store in (('builds_on', builds_on), ('practices', practices)):
            for e in entry.get(key, []):
                other = e if isinstance(e, str) else e.get('id')
                if isinstance(e, dict) and e.get('what'):
                    what[(fid, other)] = e['what']
                if other not in board.frames:
                    errors.append(f'{fid}.{key} names an unknown section: {other}')
                elif other == fid:
                    errors.append(f'{fid}.{key} points to itself')
                else:
                    store.setdefault(fid, []).append(other)
    leads_to, practiced_by = {}, {}
    for fid, others in builds_on.items():
        for o in others:
            leads_to.setdefault(o, []).append(fid)
    for fid, others in practices.items():
        for o in others:
            practiced_by.setdefault(o, []).append(fid)
    for b in board.boards:
        if b['id'] in course_boards:
            for fid in b['frames']:
                f = board.frames[fid]
                is_quiz = all(board.cards.get(c, {}).get('kind') in QUESTION_KINDS | {'Leitidee', 'Guiding idea'} for c in f['cards'])
                if not f['bare'] and not is_quiz and fid not in sections:
                    warnings.append(f'course section without links: {fid} ({board.label(fid)})')

    def names(ids, owner=None, reverse=False):
        def one(i):
            w = what.get((i, owner) if reverse else (owner, i)) if owner else None
            return f'{board.label(i)} [{i}]' + (f' ({w})' if w else '')
        return '; '.join(one(i) for i in ids)

    out = []
    title = links.get('course', os.path.basename(args.board))
    out.append(f'# Knowledge map: {title}\n')
    out.append(f'Generated {datetime.date.today().isoformat()} from `{os.path.basename(args.board)}` '
               f'({len(board.cards)} cards in {len(board.frames)} sections). '
               'Do not edit by hand: change the board or the links file and run `board-map.py` again.\n')
    out.append('How to read it: each section has an id in [brackets]. "Builds on" lists the foundations a '
               'learner needs first, with what is carried over in (parentheses); "Leads to" what the section is needed for; '
               '"Practice" the tasks that train it, with what they train. Card ids follow each card title in brackets. '
               'To read a section or single cards, run `board-section.py <board.html> <id> [<id> ...]`. For the full '
               'chain of foundations of a section, the exact cards on both ends of each connection, and the guiding '
               'ideas with their connection questions, run `board-path.py <board.html> <links.json> <id>`.\n')
    out.append('| Board | Opens with | Sections | Cards |')
    out.append('|-------|------------|----------|-------|')
    for b in board.boards:
        n_cards = sum(len(board.frames[f]['cards']) for f in b['frames'] if f in board.frames)
        role = ' (course)' if b['id'] in course_boards else ''
        out.append(f"| {b['label']}{role} | button \"{b['label']}\" or link hash #{b['hash']} | {len(b['frames'])} | {n_cards} |")
    out.append('')

    for b in board.boards:
        out.append(f"## Board {b['label']}\n")
        for fid in b['frames']:
            f = board.frames.get(fid)
            if not f:
                continue
            head = ' '.join(p for p in (f['num'], f['title']) if p)
            out.append(f'### {head} [{fid}]')
            entry = sections.get(fid, {})
            if entry.get('source'):
                out.append(f"- Source: {entry['source']}")
            if builds_on.get(fid):
                out.append(f'- Builds on: {names(builds_on[fid], fid)}')
            if leads_to.get(fid):
                out.append(f'- Leads to: {names(leads_to[fid])}')
            if practices.get(fid):
                out.append(f'- Practices: {names(practices[fid], fid)}')
            if practiced_by.get(fid):
                out.append(f'- Practice: {names(practiced_by[fid], fid, reverse=True)}')
            ideas = [c for c in links.get('concepts', []) if any(s.get('section') == fid for s in c.get('stops', []))]
            if ideas:
                out.append('- Guiding ideas: ' + '; '.join(f"{c['name']} [{c['id']}]" for c in ideas))
            cards = [board.cards[c] for c in f['cards'] if c in board.cards]
            questions = [c for c in cards if c['kind'] in QUESTION_KINDS]
            by_kind = {}
            for c in cards:
                if c['kind'] not in QUESTION_KINDS:
                    by_kind.setdefault(c['kind'] or 'Card', []).append((c['title'], c['id']))
            for kind, titles in by_kind.items():
                out.append(f"- {kind}: " + '; '.join(f'"{t}" ({i})' for t, i in titles))
            if questions:
                out.append(f"- Self-test questions: {len(questions)} ({questions[0]['id']} to {questions[-1]['id']})")
            out.append('')

    concepts = links.get('concepts', [])
    if concepts:
        out.append('## Guiding ideas (Leitideen)\n')
        out.append('Ideas that run through several parts of the course. Each lists its stops in course order. '
                   'The connection questions and model answers are in `board-path.py ... <idea id>`.\n')
        for c in concepts:
            stops = '; '.join(f"{board.label(s['section'])} [{s['section']}]" for s in c.get('stops', []) if s.get('section') in board.frames)
            out.append(f"### {c['name']} [{c['id']}]")
            out.append(f"- Idea: {c.get('idea', '')}")
            out.append(f'- Stops: {stops}')
            out.append('')
    text = '\n'.join(out).rstrip() + '\n'
    if args.out:
        open(args.out, 'w', encoding='utf8').write(text)
        print(f'wrote {args.out}: {len(text.splitlines())} lines, {len(text) // 1024} KB')
    else:
        sys.stdout.write(text)
    for w in warnings:
        print('warning:', w, file=sys.stderr)
    for e in errors:
        print('error:', e, file=sys.stderr)
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
