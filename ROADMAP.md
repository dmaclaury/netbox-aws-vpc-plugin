# Roadmap

Informal backlog for maintainers and agents. Not a commitment schedule.

## Build / developer experience

- **`Makefile` `test` target:** [`Makefile`](Makefile) defines `test: format lint unittest`, but there is no `unittest` recipe. Decide whether to add a target that runs NetBox’s `manage.py test` (with documented cwd/context), or to redefine `test` to match what developers actually run (see [`AGENTS.md`](AGENTS.md) commands).
- **Scoped `AGENTS.md`:** Consider adding directory-scoped agent docs (for example under [`extras/`](extras/) or [`.devcontainer/`](.devcontainer/)) once conventions for extras vs core plugin work stabilize.
