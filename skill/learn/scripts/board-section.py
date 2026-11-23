#!/usr/bin/env python3
"""Print the text of sections or cards of a learning board.

Lets a tutor read exactly the topic in focus without loading the whole board file.

Usage:
  python3 board-section.py <board.html> <ref> [<ref> ...]

A <ref> is a section id (f-ma6), a card id (ma6-modell), or board:number (makro:3.5).
Formulas are printed as TeX. Answers of question and solution cards follow a line in [brackets].
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from boardlib import Board, card_text  # noqa: E402


def print_card(board, cid):
    c = board.cards[cid]
    head = ' '.join(p for p in (f"[{c['kind']}]" if c['kind'] else '', c['title']) if p)
    print(f'## {head} ({cid})\n')
    print(card_text(c) + '\n')


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    board = Board(sys.argv[1])
    for ref in sys.argv[2:]:
        kind, rid = board.resolve(ref)
        if kind == 'frame':
            f = board.frames[rid]
            print(f'# {board.label(rid)} [{rid}]\n')
            for cid in f['cards']:
                if cid in board.cards:
                    print_card(board, cid)
        elif kind == 'card':
            print_card(board, rid)
        else:
            print(f'Not found on the board: {ref}', file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
