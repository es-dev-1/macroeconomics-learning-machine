// Unit tests for the pure layout model embedded in the board HTML.
// Run: node --test tests/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const html = readFileSync(path.join(here, '..', 'deliverables', 'macro-learning-board.html'), 'utf8');
const block = html.match(/<script id="board-model">([\s\S]*?)<\/script>/);
if (!block) throw new Error('board-model script block not found in the HTML');
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(block[1], sandbox);
const BM = sandbox.BoardModel;
// Objects from the vm realm have a different prototype; compare as plain JSON.
const j = x => JSON.parse(JSON.stringify(x));
const overlap = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

test('bbox spans all rects and is null for none', () => {
  assert.deepEqual(j(BM.bbox([{ x: 0, y: 0, w: 10, h: 10 }, { x: 20, y: 5, w: 5, h: 20 }])), { x: 0, y: 0, w: 25, h: 25 });
  assert.equal(BM.bbox([]), null);
});

test('contains is inclusive at the border', () => {
  const r = { x: 0, y: 0, w: 10, h: 10 };
  assert.equal(BM.contains(r, { x: 10, y: 10 }), true);
  assert.equal(BM.contains(r, { x: 11, y: 5 }), false);
  assert.deepEqual(j(BM.center(r)), { x: 5, y: 5 });
});

test('frameRect adds padding and a head band, falls back when empty', () => {
  assert.deepEqual(j(BM.frameRect([{ x: 100, y: 200, w: 50, h: 50 }])), { x: 76, y: 132, w: 98, h: 142 });
  const fb = { x: 1, y: 2, w: 300, h: 200 };
  assert.deepEqual(j(BM.frameRect([], fb)), fb);
  assert.equal(BM.frameRect([]), null);
});

test('layoutFrame stacks columns without overlap and starts the frame at the origin', () => {
  const sizes = { a: { w: 100, h: 50 }, b: { w: 120, h: 30 }, c: { w: 200, h: 300 } };
  const out = BM.layoutFrame({ id: 'f', columns: [['a', 'b'], ['c']] }, sizes, { x: 0, y: 0 });
  assert.deepEqual(j(out.positions), { a: { x: 24, y: 68 }, b: { x: 24, y: 138 }, c: { x: 164, y: 68 } });
  assert.deepEqual(j(out.rect), { x: 0, y: 0, w: 388, h: 392 });
  const rects = Object.entries(out.positions).map(([id, p]) => ({ x: p.x, y: p.y, w: sizes[id].w, h: sizes[id].h }));
  for (let i = 0; i < rects.length; i++) for (let k = i + 1; k < rects.length; k++) assert.equal(overlap(rects[i], rects[k]), false);
});

test('layoutFrame places a bare spec card exactly at the origin', () => {
  const out = BM.layoutFrame({ id: 't', bare: true, columns: [['t1']] }, { t1: { w: 500, h: 80 } }, { x: 10, y: 20 });
  assert.deepEqual(j(out.positions), { t1: { x: 10, y: 20 } });
  assert.deepEqual(j(out.rect), { x: 10, y: 20, w: 500, h: 80 });
});

test('autoLayout places frames in rows without overlap and maps cards to frames', () => {
  const specs = {
    f1: { id: 'f1', columns: [['a']] },
    f2: { id: 'f2', columns: [['b']] },
    f3: { id: 'f3', columns: [['c', 'd']] },
    t: { id: 't', bare: true, columns: [['title']] }
  };
  const sizes = { a: { w: 100, h: 100 }, b: { w: 100, h: 400 }, c: { w: 300, h: 50 }, d: { w: 300, h: 50 }, title: { w: 600, h: 90 } };
  const out = BM.autoLayout([['t'], ['f1', 'f2'], ['f3']], specs, sizes, { x: 0, y: 0 });
  const fr = out.frames;
  assert.equal(fr.f2.x, fr.f1.x + fr.f1.w + 120);
  assert.equal(fr.f1.y, fr.t.y + fr.t.h + 120);
  assert.equal(fr.f3.y, fr.f1.y + Math.max(fr.f1.h, fr.f2.h) + 120);
  const ids = Object.keys(fr);
  for (let i = 0; i < ids.length; i++) for (let k = i + 1; k < ids.length; k++) assert.equal(overlap(fr[ids[i]], fr[ids[k]]), false, ids[i] + ' vs ' + ids[k]);
  assert.deepEqual(j(out.frameOf), { title: null, a: 'f1', b: 'f2', c: 'f3', d: 'f3' });
  assert.deepEqual(Object.keys(out.positions).sort(), ['a', 'b', 'c', 'd', 'title']);
});

test('membership picks the smallest frame containing the center, or null', () => {
  const frames = { A: { x: 0, y: 0, w: 100, h: 100 }, B: { x: 50, y: 50, w: 30, h: 30 } };
  assert.equal(BM.membership({ x: 55, y: 55, w: 10, h: 10 }, frames), 'B');
  assert.equal(BM.membership({ x: 5, y: 5, w: 10, h: 10 }, frames), 'A');
  assert.equal(BM.membership({ x: 500, y: 5, w: 10, h: 10 }, frames), null);
});

test('arrowPoints clips the center line at both borders', () => {
  const a = { x: 0, y: 0, w: 100, h: 100 };
  assert.deepEqual(j(BM.arrowPoints(a, { x: 300, y: 0, w: 100, h: 100 }, 0)), { x1: 100, y1: 50, x2: 300, y2: 50 });
  assert.deepEqual(j(BM.arrowPoints(a, { x: 0, y: 300, w: 100, h: 100 }, 0)), { x1: 50, y1: 100, x2: 50, y2: 300 });
  assert.deepEqual(j(BM.arrowPoints(a, { x: -300, y: 0, w: 100, h: 100 }, 0)), { x1: 0, y1: 50, x2: -200, y2: 50 });
  assert.deepEqual(j(BM.arrowPoints(a, { x: 200, y: 200, w: 100, h: 100 }, 0)), { x1: 100, y1: 100, x2: 200, y2: 200 });
  const g = BM.arrowPoints(a, { x: 300, y: 0, w: 100, h: 100 }, 6);
  assert.equal(g.x1, 106); assert.equal(g.x2, 294);
  assert.equal(BM.arrowPoints(a, { x: 0, y: 0, w: 100, h: 100 }, 0), null);
});

test('mergeLayout keeps saved geometry, drops unknown ids, and places new frames to the right', () => {
  const defaults = {
    positions: { a: { x: 24, y: 68 }, b: { x: 164, y: 68 }, n: { x: 24, y: 668 } },
    widths: { a: 100, b: 100, n: 100 },
    sizes: { a: { w: 100, h: 50 }, b: { w: 100, h: 50 }, n: { w: 100, h: 50 } },
    frameOf: { a: 'F1', b: 'F1', n: 'F2' },
    frames: { F1: { x: 0, y: 0, w: 288, h: 142 }, F2: { x: 0, y: 600, w: 148, h: 142 } }
  };
  const saved = {
    nodes: { a: { x: 1000, y: 1000, w: 150, frame: 'F1' }, b: { x: 1200, y: 1000, w: 100, frame: 'F1' }, gone: { x: 0, y: 0, w: 10, frame: null } },
    notes: { n1: { x: 1400, y: 900, w: 200, h: 100 } }
  };
  const out = j(BM.mergeLayout(defaults, saved));
  assert.deepEqual(out.nodes.a, { x: 1000, y: 1000, w: 150, frame: 'F1' });
  assert.deepEqual(out.nodes.b, { x: 1200, y: 1000, w: 100, frame: 'F1' });
  assert.equal(out.nodes.gone, undefined);
  // Saved content spans x up to 1600 (the note). New frame F2 chrome starts PAD + 120 to the right.
  const f2x = 1600 + 24 + 120;
  assert.equal(out.nodes.n.x, f2x + (24 - 0));
  assert.equal(out.nodes.n.frame, 'F2');
  // Top of the new frame aligns with the top of the saved content's frame chrome.
  assert.equal(out.nodes.n.y, (900 - 24 - 44) + (668 - 600));
});

test('mergeLayout puts a new card of an existing frame next to that frame\'s saved cards', () => {
  const defaults = {
    positions: { a: { x: 24, y: 68 }, c: { x: 164, y: 68 } },
    widths: { a: 100, c: 120 },
    sizes: { a: { w: 100, h: 50 }, c: { w: 120, h: 70 } },
    frameOf: { a: 'F1', c: 'F1' },
    frames: { F1: { x: 0, y: 0, w: 308, h: 162 } }
  };
  const saved = { nodes: { a: { x: 500, y: 400, w: 100, frame: 'F1' } } };
  const out = j(BM.mergeLayout(defaults, saved));
  assert.deepEqual(out.nodes.c, { x: 620, y: 400, w: 120, frame: 'F1' });
});

test('mergeLayout with no saved state returns the defaults', () => {
  const defaults = {
    positions: { a: { x: 24, y: 68 } }, widths: { a: 100 }, sizes: { a: { w: 100, h: 50 } },
    frameOf: { a: 'F1' }, frames: { F1: { x: 0, y: 0, w: 148, h: 142 } }
  };
  assert.deepEqual(j(BM.mergeLayout(defaults, null).nodes), { a: { x: 24, y: 68, w: 100, frame: 'F1' } });
});

test('history keeps a bounded undo stack and clears redo on push', () => {
  const h = BM.createHistory(3);
  assert.equal(h.canUndo(), false);
  h.push('s1'); h.push('s2'); h.push('s3'); h.push('s4');
  assert.equal(h.undo('cur'), 's4');
  assert.equal(h.undo('s4'), 's3');
  assert.equal(h.undo('s3'), 's2');
  assert.equal(h.undo('s2'), null);
  assert.equal(h.canRedo(), true);
  assert.equal(h.redo('s2'), 's3');
  h.push('x');
  assert.equal(h.canRedo(), false);
  h.clear();
  assert.equal(h.canUndo(), false);
});

test('cleanArrows drops arrows whose ends no longer exist', () => {
  const out = j(BM.cleanArrows({ a1: { from: 'x', to: 'y', label: '' }, a2: { from: 'x', to: 'gone', label: '' } }, ['x', 'y']));
  assert.deepEqual(Object.keys(out), ['a1']);
});

// ---- Frames with their own size (v3) ----

test('frameBounds keeps the stored size and grows to fit members', () => {
  const stored = { x: 0, y: 0, w: 600, h: 400, title: 'T' };
  assert.deepEqual(j(BM.frameBounds(stored, [])), { x: 0, y: 0, w: 600, h: 400 });
  // A member inside the stored space changes nothing
  assert.deepEqual(j(BM.frameBounds(stored, [{ x: 100, y: 100, w: 100, h: 100 }])), { x: 0, y: 0, w: 600, h: 400 });
  // A member past the right edge grows the frame to member edge + PAD
  assert.deepEqual(j(BM.frameBounds(stored, [{ x: 550, y: 100, w: 200, h: 100 }])), { x: 0, y: 0, w: 774, h: 400 });
  // Without a stored size the frame hugs its members (legacy behaviour)
  assert.deepEqual(j(BM.frameBounds(null, [{ x: 100, y: 200, w: 50, h: 50 }])), { x: 76, y: 132, w: 98, h: 142 });
  assert.equal(BM.frameBounds(null, []), null);
});

test('membership keeps a card in a frame with free space next to the other cards', () => {
  // Frame with room on the right; its only other card sits on the left
  const frames = { F: BM.frameBounds({ x: 0, y: 0, w: 900, h: 500 }, [{ x: 24, y: 68, w: 300, h: 200 }]) };
  assert.equal(BM.membership({ x: 500, y: 80, w: 300, h: 200 }, frames), 'F');
  assert.equal(BM.membership({ x: 1000, y: 80, w: 300, h: 200 }, frames), null);
});

test('clampFrameSize never cuts off members and respects a minimum', () => {
  const stored = { x: 100, y: 100, w: 600, h: 400 };
  const members = [{ x: 150, y: 180, w: 300, h: 200 }];
  assert.deepEqual(j(BM.clampFrameSize(stored, 200, 100, members)), { x: 100, y: 100, w: 374, h: 304 });
  assert.deepEqual(j(BM.clampFrameSize(stored, 800, 500, members)), { x: 100, y: 100, w: 800, h: 500 });
  assert.deepEqual(j(BM.clampFrameSize(stored, 50, 50, [])), { x: 100, y: 100, w: 280, h: 160 });
});

test('mergeLayout returns frame rects: defaults when nothing is saved, shifted for new frames', () => {
  const defaults = {
    positions: { a: { x: 24, y: 68 }, n: { x: 24, y: 668 } },
    widths: { a: 100, n: 100 },
    sizes: { a: { w: 100, h: 50 }, n: { w: 100, h: 50 } },
    frameOf: { a: 'F1', n: 'F2' },
    frames: { F1: { x: 0, y: 0, w: 148, h: 142 }, F2: { x: 0, y: 600, w: 148, h: 142 } }
  };
  assert.deepEqual(j(BM.mergeLayout(defaults, null).frames), defaults.frames);
  const saved = {
    nodes: { a: { x: 1000, y: 1000, w: 150, h: 320, frame: 'F1' } },
    frames: { F1: { x: 976, y: 932, w: 500, h: 500, title: 'Mine' }, uX: { x: 0, y: 0, w: 300, h: 200, title: 'U', user: true } }
  };
  const out = j(BM.mergeLayout(defaults, saved));
  assert.deepEqual(out.frames.F1, saved.frames.F1);
  assert.deepEqual(out.frames.uX, saved.frames.uX);
  assert.equal(out.nodes.a.h, 320);
  // Saved content (frames F1 and uX) spans x 0..1476 and starts at y 0: the new frame F2 sits
  // FRAME_GAP to the right of it, aligned with its top, and its card keeps its offset inside the frame
  assert.deepEqual(out.frames.F2, { x: 1476 + 120, y: 0, w: 148, h: 142 });
  assert.deepEqual(out.nodes.n, { x: 1476 + 120 + 24, y: 68, w: 100, frame: 'F2' });
});
