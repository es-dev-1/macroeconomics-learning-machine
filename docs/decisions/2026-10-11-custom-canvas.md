# Decision: custom-built canvas for the learning board

- **Decision**: build the endless board as a custom pan-and-zoom canvas inside the artifact page
- **Date**: 2026-10-11
- **Context**: Elias wants an unlimited 2D board where content can be moved around, instead of a scrolling page.
- **Reasoning**: the point of the board is interactive graphs computed from the equations and formulas typeset in LaTeX. A custom canvas keeps both and gives full control over cards, frames, notes, and arrows.
- **Alternatives considered**:
  - tldraw or Excalidraw: ready-made whiteboard tools, but live HTML graph cards do not fit them (tldraw needs a license key and build step; Excalidraw embeds rely on iframes the artifact cannot load).
  - Miro: a real endless board, but graphs and formulas become static images without sliders.
