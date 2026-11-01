# Third-party software

## Impeccable 4.5.2

- Author: Paul Bakaus. Upstream: https://github.com/pbakaus/impeccable, https://impeccable.style
- License: Apache License 2.0. Full text: `plugins/impeccable/LICENSE`. Notices: `plugins/impeccable/NOTICE.md`.
- Copied unmodified from the `plugin/` (Claude build) and `.grok/` (Grok build) folders of Tyler's mirror, `tenlowga-cloud/impeccable` at commit `6b3839c`.
- Where it lives here: `plugins/impeccable/`, `vendor/impeccable-grok/`, and the copies `scripts/build.py` makes in `grok/.grok/` and `dist/impeccable.skill`.
- Its launcher downloads a self-contained binary on first run (see its SKILL.md, "Setup").

To update: copy the new `plugin/` and `.grok/` folders from upstream over `plugins/impeccable/` and `vendor/impeccable-grok/`, keep `LICENSE` and `NOTICE.md`, bump the version in `.claude-plugin/marketplace.json`, run `python3 scripts/build.py`.
