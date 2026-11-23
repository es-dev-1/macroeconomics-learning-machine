# Canvas board implementation plan

**Goal:** turn the scrolling section 1 page into an endless pan-and-zoom canvas with movable cards in topic frames, user notes, and arrows, saved per user.

**Architecture:** one HTML file. A pure layout model (`<script id="board-model">`, global `BoardModel`) holds geometry, layout, merge, membership, arrow, and history logic and is unit-tested in Node. The canvas engine (DOM) renders a transformed world layer with frames, an SVG arrow layer, and cards/notes, and handles pan, zoom, drag, resize, tools, and persistence. The existing economics model, chart toolkit, and section 1 content move into cards largely unchanged.

**Tech stack:** vanilla JS, MathJax 3.2.2 SVG (cdnjs), artifact capabilities `db` + `user`, Node `node:test` for the model.

**Spec:** `docs/2026-10-11-canvas-board-design.md`

## Global constraints

- Single file: `deliverables/macro-learning-board.html`, published to the existing artifact URL.
- Copy rules: no em dashes, no emojis, Oxford commas.
- Persistence: one document per viewer at `data/users/<id>/board`, body `{v, nodes, frames, notes, arrows}`, under 256 KiB; writes debounced and sequential; pan/zoom view kept in localStorage only.
- Charts must map pointer coordinates through the canvas zoom (divide by `rect.width / offsetWidth`).

## Persisted state shape

```json
{
  "v": 1,
  "nodes":  { "<cardId>": { "x": 0, "y": 0, "w": 380, "frame": "f-11" } },
  "frames": { "<frameId>": { "x": 0, "y": 0, "w": 0, "h": 0 } },
  "notes":  { "<noteId>": { "x": 0, "y": 0, "w": 220, "h": 140, "text": "", "color": "yellow", "frame": null } },
  "arrows": { "<arrowId>": { "from": "<id>", "to": "<id>", "label": "" } }
}
```

## Tasks

### Task 1: Layout model with tests
**Files:** create `tests/board-model.test.mjs`; the model lives in the HTML `<script id="board-model">`.
**Produces (BoardModel):**
- `bbox(rects) -> rect|null`, `center(rect) -> {x,y}`, `contains(rect, pt) -> bool`
- `frameRect(memberRects, fallback) -> rect|null` (padding 24, head 44)
- `layoutFrame(spec, sizes, origin) -> {positions, rect}` with `spec = {id, columns: [[cardId]], bare?}`
- `autoLayout(rows, specsById, sizes, origin) -> {positions, frames, frameOf}`
- `mergeLayout(defaults, saved) -> {nodes}` (known ids keep saved geometry; unknown content ids shift as a group to the right of the saved bounding box; unknown saved ids dropped)
- `membership(rect, frameRects) -> frameId|null` (center inside, smallest frame wins)
- `arrowPoints(rectA, rectB, gap) -> {x1,y1,x2,y2}` (center line clipped at both borders)
- `createHistory(limit) -> {push, undo, redo, canUndo, canRedo, clear}`
- `cleanArrows(arrows, existingIds) -> arrows`
**Tests:** each function above, including no-overlap of auto layout, merge placement of a new frame, membership edge cases, arrow clipping on all four sides, history limit and redo invalidation.

### Task 2: Canvas shell
Top bar (tools, topics menu, zoom, fit, undo/redo, reset, save status), viewport with dot grid, world transform, pan (drag background, wheel), zoom (ctrl/cmd + wheel, pinch, buttons, keys), fit all, fly to frame, view saved in localStorage.
**Check:** render in headless Chrome; pan/zoom math covered by `screenToWorld`/`zoomAt` used consistently.

### Task 3: Content cards and frames
Move section 1 into about 25 cards (`article.card[data-id]` with `.card-head` drag handle and `.rz` resize handle), frame specs and rows, default layout from measured sizes, re-layout after MathJax and fonts while pristine, chart pointer fix for zoom.

### Task 4: Moving, resizing, frames
Drag cards and notes by header, drag frames by label (moves members), membership on drop, resize width (cards) and width/height (notes), arrow keys nudge selection, live frame and arrow updates via ResizeObserver.

### Task 5: Notes and arrows
Note tool and double-click to create, in-place edit with LaTeX support, four colors, delete. Arrow tool (drag from item to item), SVG arrows with labels, label editing, delete.

### Task 6: History, reset, persistence
Undo/redo snapshots on every committed change, Reset layout (keeps notes and arrows) with undo toast, `db`/`user` load and debounced save with status, graceful offline mode.

### Task 7: Verify and publish
Node tests green, one headless render check, publish with `capabilities: {db: {}, user: {}}` to the existing URL, one `ArtifactData` read of the saved document.
