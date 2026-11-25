# Learning machine: project charter

Last updated: 2026-11-25. Source: Elias's brief of 2026-11-15 and his addition of 2026-11-16 on the topic rhythm. This is the main task of the whole project. Everything else in the project serves it.

## Mission

Build a learning machine that lets a person learn any topic deeply, in a way that sticks and can be applied when it counts: a university exam, a presentation, a real problem. The learner hands over the topic and the material (for a student: lectures, practice tasks, old exams, practice exams, and the prerequisite courses), then follows the lead of the AI. Macroeconomics (Makroökonomik I) is the first test case: Elias wants to write his best possible exam with it.

Success for a student means the best possible grade in the time left until the exam.

## The two parts

| Part | Role | Where the learner is |
|------|------|----------------------|
| The session (AI tutor in Claude Code) | Teaches by asking questions and setting tasks. Plans, tracks progress, and builds up to practice exams. | Most of the time |
| The dashboard (the board, read chapter by chapter since version 24) | Intelligent knowledge base. Holds the knowledge, shows how it connects, and lets the learner focus on what matters now. | When reading up after a question or task |

The material (lectures, practice sheets, old exams, prerequisite courses) feeds both: it becomes board content, and it shows the tutor how the professor thinks and asks.

## How the tutor teaches

1. **Questions and tasks, not lectures.** The tutor asks, the learner recalls, explains, and calculates. Theory questions and calculations both.
2. **Wrong answer or "I don't know":** explain kindly and briefly, connect to the prerequisite knowledge the learner already has, then let the learner try again.
3. **Always point to the board** at the end: where to read up on this topic, and which foundation it builds on.
4. **Refresh the foundations.** The tutor knows the prerequisite courses, reminds the learner of what they already know, and builds the new material on top.
5. **Knowledge that sticks comes first** (added by Elias on 2026-11-16). Topics are woven together, not taught in blocks: questions jump between the topic being built, the next topic (introduced early with a smaller share), and earlier topics. The focus moves to a new topic only when the current one has stuck: the learner explains it and solves a standard task alone, also after coming back to it from other topics. Earlier topics keep coming back on a widening schedule, because people forget.
6. **A ladder toward the exam:**
   - Foundations: single questions and tasks, one concept at a time.
   - Mixed sets: several tasks and questions from different topics at once. The learner is pushed here early, as soon as there is some basic understanding, not only after perfect answers. The tutor believes the learner can do more than they have proven so far.
   - More and more questions at once as the learner improves.
   - Full practice exams, closely modeled on the faculty's old exams and practice exams, with the same time limit, so the learner learns to allocate time.
7. **Works with the time that is left.** The tutor recommends a sensible study plan. If the learner started late, it builds up faster and moves to exam practice sooner.
8. **Other goals too.** For a presentation, the tutor builds the knowledge the same way, then listens to the rehearsal and gives feedback.

## Tone

- Understanding and patient. Learning takes time. No blame for mistakes.
- Point out what the learner has shown they learned: one thing, three at most, and only when it is real.
- The feeling should be joy: the fun of learning something new and the moment of "I really got this".

## What the dashboard must do

1. **Connect, not just list.** Knowledge is not linear. Higher-level knowledge (macro) is linked to the foundations it needs (micro, maths), and related topics are linked to each other.
2. **Focus.** Show what the learner needs right now to reach the next level, with only the connections that matter right now. Everything else on the board is valuable, but at this moment it is noise.
3. **Stay intuitive.** Never so packed that it overloads the learner.

## Built to be general

The tool must not be tied to macroeconomics. The design keeps three things apart:

| Layer | What it is | Where it lives now |
|-------|------------|--------------------|
| Method | How to teach, the ladder, tone, session routine | Skill `learn` (`ea-personal/.claude/skills/learn/`) |
| Course | Material, board, links between topics, exam style | This project folder (`deliverables/`, `data/`) |
| Learner | Goal, deadline, progress, error patterns | `data/learner-profile.md`, `data/learner-progress.md` |

A new topic means a new course folder. The method stays the same.

## Where the project stands (2026-11-19)

| Vision | Status |
|--------|--------|
| Board content for the course | Done for the slides: the whole Makro course (VL 1 to 26, 56 sections, 29 graphs), Tutorium tasks reconstructed from the slide references, Micro and Maths foundations on their own boards, every section connected |
| Tutor that teaches by questions | `learn` skill with the teaching rhythm. One trial run with a simulated learner (2026-11-16), skill improved from it. Not yet used by Elias |
| Tutor can find and cite board content | Done: `data/knowledge-map.md` plus a section reader script |
| Links from macro to its foundations | Done, card to card (version 20): 382 connections say what is carried over and how, and link the card where it is used to the card that explains it. Shown at the foot of each card, in the focus panel, in the knowledge map, and in the tutor's `board-path.py` |
| Related topics linked to each other | Done (version 20): 21 Leitideen trace the ideas that run through the course (steady state, Euler equation, neutrality, present value, market failure, and others), each with its stops and two connection questions. A frame on the Makro board and threads in the knowledge network |
| Seeing the connections at a glance | Done (version 20): knowledge network (key W) with every section in columns; a click shows a section's whole chain of foundations and what it leads to |
| Focus on what matters now | Done (version 16, reworked in version 24): the board is read chapter by chapter, one page per chapter of the course (version 25: Makro 1 to 22, with a chapter menu on every board button); the tutor's pick opens the chapter at the section that matters now and rings the cards to read first, and the panel next to it shows that section's connections. The canvas of versions 1 to 23 was too slow and is archived. Version 20: the board shows the learner's progress (statuses and due reviews) written by the tutor, and the network's start view names the sections most of the course rests on |
| Old exams, practice exams, original Tutorium sheets | Not uploaded yet |
| Exam date and study plan | Open, asked in the first study session |
| Presentation rehearsal | Described in the skill, not tried |
| Usable by other people | Started: since 2026-11-23 the board, course data, and tutor skill are in a public GitHub repository, and the board is online on GitHub Pages (notes saved in the browser). Learner files stay private |

## Roadmap

1. **Foundation (done 2026-11-15):** charter, `learn` skill, knowledge map, course and learner files.
2. **Board: connections and focus (done 2026-11-15, version 16; deepened 2026-11-19, version 20).** Each section shows what it builds on and what it leads to, as clickable links across boards. A focus mode shows one section with its foundations and dims the rest. The tutor can set the focus from the session. Version 20: labelled card-to-card links, Leitideen, the knowledge network, and the learner's progress on the board; the tutor asks connection questions and interleaves by connection.
3. **Content (lectures done 2026-11-17; Tutorium sheets and exams still missing):** VL 10 to 26, original Tutorium sheets, old exams and practice exams, then an exam analysis (task types, points, timing, the professor's style).
4. **Practice exam engine:** timed mock exams built from the exam analysis, with grading and time review.
5. **Generalize:** a "new course" routine that turns uploaded material into a board, a knowledge map, and a plan. Then move the tool out of the private workspace so others can use it.

## Open decisions

- Exam date, exam length, and allowed aids for Makroökonomik I.
- Where the tool lives once other people use it. It cannot be shared from ea-personal. Moving it into a shareable place is Elias's call.
- How the material is stored: the slides currently sit in `~/Downloads/MAKRO LECTURE SLIDES`, which is not a safe long-term home.
