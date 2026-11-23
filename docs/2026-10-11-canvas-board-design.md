# Canvas board design

**Status**: approved by Elias on 2026-10-11
**Last updated**: 2026-10-11

## Summary

The learning board becomes an endless 2D canvas. Content is split into small cards grouped in topic frames. Elias can pan, zoom, move and resize cards and frames, add his own text notes, and draw arrows between anything. His layout, notes, and arrows are saved per user in the artifact's database, so they survive republishes and work across devices.

## Decisions from the brainstorm

| Question | Decision |
|---|---|
| What can Elias do besides arranging? | Own text notes and arrows between cards (no freehand pen, no shapes) |
| Card size | Small cards (explanation, formula, graph, quiz question) grouped in one frame per topic |
| Build approach | Custom canvas in the page, no whiteboard library, not Miro (see `decisions/2026-10-11-custom-canvas.md`) |
| Where layout is saved | Artifact `db` capability, per-user documents |

## The canvas

- Endless dotted surface. Drag empty space to pan, wheel or pinch to zoom, toolbar zoom in/out, "Fit all", and a topic list that flies to a frame.
- Frames: one per topic (1.1 to 1.5, Formula sheet, Self-test) with a label. Dragging the label moves the frame and its cards. Dropping a card into a frame adds it; dragging it out removes it.
- Content cards: explanation, formula, interactive graph (sliders included), one card per quiz question. Each card has a header used as the drag handle so sliders and graph hover keep working. Corner handle resizes; graphs redraw at the new size.
- Notes: text notes in a few colors, created with the Note tool or double-click on empty space, edited in place.
- Arrows: from any card, note, or frame to another, attached to both ends, optional short label.
- Delete key removes selected notes and arrows. Content cards can be moved but not deleted.
- Ctrl+Z undoes moves, resizes, notes, and arrows. "Reset layout" restores the default position of content cards and frames and keeps notes and arrows.

## Saving

- Saved per user: card and frame positions and sizes, notes, arrows.
- Not saved: slider positions (reset on reload).
- New sections added later appear in free space next to existing content; saved positions of existing items are untouched.
- Signed out or database unavailable: the board works and shows that changes are not kept.

## Unchanged from the page version

All section 1 content, Blanchard notation, graphs computed from the model equations, "with your numbers" formula lines, table views, the link between the open market operation buttons and the 1.2 graph.

## Out of scope

Freehand pen, shapes, image upload, multiple boards, live collaboration.

## Testing

Render check before publishing. After publishing, write a test layout through the database and read it back.

## Version 3 changes (approved 2026-10-11)

- Cards resize in width and height from the corner, with the size shown while dragging; double-click the corner to fit the height to the content. A card shorter than its content scrolls inside.
- Frame tool: draw a frame (or click for a default size); title editor with an optional number and a title. Double-click any frame title to rename it. Frames you made can be deleted; their cards and notes stay on the board.
- Frames keep their own size instead of hugging their cards. An item belongs to the frame its center is in when dropped; dropping it partly over the edge grows the frame to fit. Frames resize from their corner and never shrink below their cards; double-click the corner to fit the frame to its cards.
- Saved layouts from version 2 load unchanged; frame sizes are stored on the next change.

