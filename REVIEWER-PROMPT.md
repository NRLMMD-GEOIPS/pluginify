# Documentation & Code Review Prompt

This document can be used as a prompt to guide an AI assistant through a thorough
documentation and docstring review of a codebase. Customize the bracketed placeholders
at the top, then provide the prompt and any clarifying context.

---

## Usage

Copy this section (everything below the `---`) and paste it into your AI assistant.
Adjust the placeholders and scoping notes before sending.

---

Review all documentation and docstrings in this repository.

### Scoping

- Review **only** the primary package `[PACKAGE_NAME]`. Ignore any nested sub-repositories
  (e.g., vendored deps, forks, submodules).
- If there is an `AGENTS.md` or equivalent developer guide at the repo root, consult it
  for the project's conventions (docstring style, line length, type checker commands).
- Ignore missing Sphinx/ReadTheDocs build machinery unless it is also your concern.

### What to review

Conduct the following passes in order. Do not begin editing until passes 1-5 are
complete and the user has seen the full plan.

#### Pass 1: Inventory docs files

List every documentation file in the project:

- Top-level docs: `README.md`, `CHANGELOG`, `CODE_OF_CONDUCT.md`, `LICENSE`, etc.
- Structured docs: everything under `docs/` (markdown, reST, YAML release notes).
- Module-level docstrings: `__init__.py` files and standalone module headers.

#### Pass 2: Check for unwanted external references

Search all documentation and source-code docstrings for references to other packages
that should **not** be hard dependencies or primary context. For example:

- CLI examples that use another package's flags instead of the project's own.
- Configuration examples, file paths, or URLs that embed another package's name.
- Source code that `import`-s or `files("another_pkg")`-s a package that should be
  optional or decoupled.

Flag each occurrence with file + line + suggested change.

#### Pass 3: Identify missing coverage

Compare what exists against what a newcomer would need:

- **Getting-started / tutorial**: installation, first usage, minimal working example.
- **Conceptual / architectural**: how the system is structured, key abstractions.
- **API reference**: auto-generated or hand-written per-module/per-class docs.
- **Sub-system deep-dives**: configuration, plugin models, class hierarchies, CLI.
- **Release notes**: changelog, version history.

Flag each gap with a suggested new page/section and a one-line summary of what it
should cover. Note any place where the same information is scattered across files
and should be consolidated into a single reference page.

#### Pass 4: Content quality audit of existing docs

- Leftover template placeholders (`@variable@`, `<!-- TODO ... -->`, boilerplate).
- Broken or self-referential links (`{ref}`same page </same page>``).
- Docs that point to another repo's resources when a project-native reference exists.
- Standalone files that don't belong (feature requests, notes-to-self).

#### Pass 5: Review source-code docstrings

Read every Python module, class, method, and function docstring. Check against the
project's declared docstring convention (e.g., numpy style from `.flake8`):

- **Module docstrings**: does every module have at least a one-line summary describing
  what it provides? Are exported symbols mentioned?
- **Class docstrings**: are `Attributes` listed where relevant? Are constructor
  parameters documented (either in the class docstring or `__init__`)?
- **Method/function docstrings**: do they follow the expected section order
  (Summary → Parameters → Returns/Raises → Notes → Examples)?
- **Parameters section**: is each parameter an indented `name : type` line (not a
  bullet list)? Are types specified? Are defaults noted with `, optional`?
- **Returns section**: is the return type always present? Are multi-return values
  named where useful?
- **Raises section**: are non-obvious exceptions documented?
- **Content mismatches**: do any docstrings describe behavior the code does not
  implement (wrong attribute names, wrong return semantics, copy-paste errors)?

Also check for **type-hint gaps** — every function/method signature should have
parameter types and return types annotated (`def foo(x: int) -> str:`).

#### Pass 6: Present a prioritized plan

Combine findings into a tiered plan:

| Priority | Criteria |
|---|---|
| Urgent | Documentation is factually wrong or refers to non-existent behavior |
| High | Missing content a new user would need on day one |
| Medium | Style inconsistencies, sparse but not wrong docstrings |
| Low | Cosmetic issues, template cleanup, re-organization |

Each plan item should specify: target file(s), what to change, and the commit scope
it belongs to. If the project uses release-note tooling (e.g., brassy), include
a release-note entry for the overall documentation changes.

### Work rules

- Wait for the user to approve the plan before making any edits.
- Group changes into logical commits (per file, per module, or per concern).
- Commit messages describe the change factually; do not mention AI assistance.
- When reformatting docstrings, fix content bugs in the same commit — don't leave
  known errors for later.

### User clarifications to scope

The user may provide additional constraints up front:

- "Ignore the build machinery" — don't flag missing Sphinx `conf.py`, Makefile, etc.
- "That paragraph is fine" — some external references are intentional historical
  context; don't flag them.
- "Don't touch [directory]" — exclude a path from review entirely.
- "Use numpy style" / "Use Google style" / "Use Sphinx-rst style" — apply the
  specified docstring convention to all source files.

### Example plan format

```
Group 1: External reference cleanup
  Commit: "docs: replace third-party examples with native ones"
    - file.md:12 — add native --flag example alongside existing

Group 2: Missing docs
  Commit: "docs: add configuration reference page"
    - docs/source/config/index.md (new) — env vars, config file, CLI commands

Group 3: Docstring reformat + type hints
  Commit: "style: update docstrings and type hints in core.py"
    - package/core.py — all 5 functions, indented param style, -> ReturnType
...
```
