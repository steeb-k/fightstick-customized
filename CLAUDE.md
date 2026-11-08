# Claude notes for the fight stick project

@AGENTS.md

Everything about the design, the build commands, the verification steps and the change recipes is in `AGENTS.md`.
The notes below are the parts that only apply to Claude Code with the owner's connectors.

## Change log

The owner keeps the running record of every change since the original STEP files as a Claude Doc:
https://claude.ai/artifact/1KqTeC5zyNJNUDioWJTysZ (container `{"kind":"project","id":"02a14082-0807-4ec3-803d-a86195bc2894"}`,
prose node `c727b8b7-31cf`). It has one section per round with a Change / Before / After / Why table, a
"before printing" checklist, and a files table. After any design change:

1. Add a row to the current round's table, or a new round section if the change starts one.
2. Update the files table when files are added, renamed or re-versioned.
3. Add to the checklist anything the owner must measure or confirm before printing, and mark resolved items.

Use the `update` tool with `engine: "prose"` and `payload: {ops: [...]}` (`insert` with a target block id and
side `after` or `end`; `replace` with a `find` target). The `batch` tool's ops use `verb`, not `op`.

## Working with the owner

- Ask before deciding anything about placement, proportions or clearance they can judge by hand. Offer concrete
  options with the numbers; they will pick.
- When they say "don't change the model", change only the diagram or render scripts.
- One commit per logical change, with a message that says what changed and why, like the existing history.
  Do not push.
- American English everywhere (their global preference).
- Memory notes for this project live in the auto-memory directory; `freecad-flatpak-headless.md` there has the
  Flatpak and mesh pitfalls in more detail than `AGENTS.md`.
