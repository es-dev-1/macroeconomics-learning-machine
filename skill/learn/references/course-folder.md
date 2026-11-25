# The course folder

Everything about one course lives in one project folder. The method (this skill) stays the same for every course. Read this file when you set up a course, when a file is missing, or when you are unsure what goes where.

## Layout

```
projects/<course>/
├── README.md
├── deliverables/<board>.html        the learning board (the knowledge base)
└── data/
    ├── course.md                    facts about the course and where things are
    ├── knowledge-links.json         curated connections between board sections
    ├── knowledge-map.md             generated from board + links, never edited by hand
    ├── learner-profile.md           goal, date, time budget, starting point
    ├── learner-progress.md          status per section, error patterns, session log
    ├── exam-analysis.md             how the examiners ask (once exams are uploaded)
    ├── practice-exams/              practice exams you set, with answers and results
    └── sources/
        ├── lectures/                slides and scripts of the course
        ├── tutorials/               practice sheets and their solutions
        ├── exams/                   old exams and practice exams from the faculty
        └── prerequisites/           material of the courses this one builds on
```

File names: lowercase, hyphens, ISO date first where a date matters (`2026-11-20-practice-exam-1.md`).

## course.md

```markdown
# Course: <name>

Last updated: YYYY-MM-DD

- **Institution and term:**
- **Goal:** <for example: best possible grade in the written exam>
- **Exam date:**
- **Exam format:** <length in minutes, number of tasks, points, allowed aids, language>
- **Exam scope:** <which lectures and topics count>
- **Language of the course:**
- **Board file:** deliverables/<board>.html
- **Board link:** <published URL>
- **Board focus:** <supported or not: can the tutor set the section in focus by writing the `tutor` document?>
- **Board progress:** <supported or not: does the board show the learner's statuses from the `progress` document?>
- **Commands:** <ready-to-copy commands for board-section.py and board-path.py from the course folder>
- **Course boards:** <which boards hold the course itself, which hold foundations>
- **Material:** <where the sources are, what is still missing>
- **Prerequisite courses:** <what the institution assumes>
- **Coverage:** <what is on the board so far and what is not>
```

Mark unknown facts as "open" instead of guessing. An invented exam format produces the wrong practice.

## knowledge-links.json

The one place where connections between sections are recorded. The board (card links, connections panel, knowledge network, Leitideen cards), the knowledge map, and `board-path.py` all take them from here.

```json
{
  "course": "Course name",
  "course_boards": ["macro", "tut"],
  "parts": [
    { "label": "Maths", "ids": ["f-m1", "f-m2"] },
    { "label": "Teil I · Wachstum", "first": "f-ma1", "last": "f-ma11" },
    { "label": "Teil VI · Staatsschulden", "first": "f-ma52", "last": "f-ma56", "join": true }
  ],
  "sections": {
    "f-ma6": { "source": "Folien 3.24 bis 3.32, VL 4", "builds_on": [
      { "id": "f-m6", "what": "Wachstumsrate einer Potenz in stetiger Zeit",
        "how": "Die Bewegungsgleichung für k entsteht aus den Wachstumsraten von K und L.",
        "here": ["ma6-kapital"], "there": ["m6-continuous"] }
    ] },
    "f-tu2": { "source": "Aufgabe 4.4.3", "practices": [
      { "id": "f-ma6", "what": "Bewegungsgleichung des Kapitals und Steady State", "here": ["tu2-aufgabe"], "there": ["ma6-kapital"] }
    ] }
  },
  "concepts": [
    { "id": "steady-state", "name": "Steady State", "idea": "One or two sentences.",
      "stops": [ { "section": "f-ma6", "cards": ["ma6-dynamik"], "note": "How the idea looks here." } ],
      "questions": [ { "q": "A question that needs two stops.", "a": "Model answer." } ] }
  ]
}
```

- `builds_on`: the sections a learner needs first. Direct foundations only, not the foundations of the foundations. Each connection names the other section (`id`) and, ideally, `what` is carried over (a short noun phrase, the concrete tool or idea), `how` this section uses it (one sentence), the cards `here` that use it, and the cards `there` that explain it (content cards, not self-test questions). A bare id still works but shows no label and no card links.
- `practices`: for a block of tasks, the sections it trains, with the same fields (`here` are the task cards, `there` the theory cards).
- `concepts`: the guiding ideas (Leitideen) that run through several parts of the course, each with 3 to 8 stops in course order and two connection questions with model answers. They become cards on the board if it has the `CONCEPT-CARDS` markers, chips in the connections panel, and threads in the knowledge network.
- `parts`: the columns of the knowledge network. A range on one board (`first`, `last`) or a list of `ids`; `join` puts a part under the one before it. Boards without a part get a column each.
- `source`: where the content comes from (slides, lecture number, sheet).
- Write `what`, `how`, and `note` in the language of the board the section is on, as plain text without LaTeX.

After any change, rebuild the tutor's map and the connections shown on the board, then republish the board:

```bash
python3 <skill>/scripts/board-map.py deliverables/<board>.html --links data/knowledge-links.json --out data/knowledge-map.md
python3 <skill>/scripts/board-links.py deliverables/<board>.html data/knowledge-links.json
```

The scripts stop with an error if the links file names a section or card that is not on the board (or a card in the wrong section), and warn about course sections without an entry.

## learner-profile.md

```markdown
# Learner profile

Last updated: YYYY-MM-DD

- **Name:**
- **Course:**
- **Goal:**
- **Date of the exam or event:**
- **Time available:** <hours per week, preferred session length>
- **Language for sessions:**
- **Starting point:** <what is covered, self-assessment>
- **Shaky foundations:** <from the learner and from what the first questions showed>
- **What helps this learner:** <observations: pace, kinds of explanation that worked>

## Study plan
| Phase | Dates | Stage of the ladder | Focus |
|-------|-------|---------------------|-------|
```

## learner-progress.md

```markdown
# Learning progress

Last updated: YYYY-MM-DD

## Where we are
- **Stage of the ladder:** 1 Single questions | 2 Small sets | 3 Exam blocks | 4 Practice exams
- **Days to the date:**
- **Next session:** <what to do first>

## Rotation
- **Focus topic:** <section id and name: the topic being built now>
- **Next topic:** <the one after it, already coming in with a smaller share>
- **Check first next session:** <the topic that just left the focus, if any>
- **Earlier topics due:** <section: date, the next few from the table below>

## Sections
| Section | Status | Shown so far | Open gaps | Last practiced | Interval | Due again |
|---------|--------|--------------|-----------|----------------|----------|-----------|

## Error patterns
- <recurring mistakes, for example: mixes up growth rate and level; forgets the chain rule>

## Connection questions
| Date | Leitidee or connection | Question (short) | Held? |
|------|------------------------|------------------|-------|

## Practice exams
| Date | Exam | Time used | Score | Main gaps |
|------|------|-----------|-------|-----------|

## Session log (newest first)
### YYYY-MM-DD
- Time:
- Practiced:
- Went well:
- To repair:
- Next:
```

Statuses, from weakest to strongest:

| Status | Meaning |
|--------|---------|
| not started | never practiced |
| started | has met the idea, cannot yet explain or calculate it alone |
| known (diagnostic) | answered well in the first-session diagnostic, not yet checked again after other topics; first review in 3 days |
| understood | explains the core idea in own words, solves a standard task alone, and answers one connection question, and still can after questions on other topics. Slips allowed. The focus may move on. |
| solid | reviews held on at least two later days, one of them a connection question: the topic has stuck |
| exam-ready | solves exam-style tasks on it under time pressure |

Foundations the learner turned out not to have get their own rows at the top of the Sections table, with board, number, and id (for example "Maths 0.6 Growth rates and series [f-m6]").

The board's `progress` document uses the short keys `started`, `known`, `understood`, `solid`, and `ready` for these statuses.

Interval: the time until the next review of a topic that has left the focus, roughly 1, 3, 7, 14, then 30 days. The check in the next session after a topic leaves the focus is its first review (interval 1). It grows after a review that holds and drops back to the next session after one that fails.

## exam-analysis.md

Write it from all uploaded exams of the faculty. It is what makes the practice exams feel like the real one.

```markdown
# Exam analysis

Last updated: YYYY-MM-DD. Based on: <list of exams with dates>

## Format
<length, number of tasks, points, allowed aids, choice between tasks or not>

## What gets asked
| Topic (board section) | How often | Typical task | Points |
|-----------------------|-----------|--------------|--------|

## How it is asked
<wording, command words, share of calculation, theory, derivation, and graphs; multi-part tasks; typical traps>

## What the examiner seems to value
<for example: intuition in words after each calculation, clean notation, labeled diagrams>

## Never or rarely asked
<so time is not wasted>
```
