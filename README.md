# Site Crew

Say "build me a website." Site Crew asks the right questions first, sends a four-agent crew (design, tech, words, sales) to build it, takes it live on your domain, and keeps improving it every week.

**Site Crew is licensed.** This repo holds only the loader. It runs with a personal key from the author, and the playbook loads from the author's server while you work. Don't share your key or this repo: every copy is traced to its key.

You need: your **key** and your **connector URL** (from the author), and **Impeccable** (included here, required).

## Claude Code

```bash
/plugin marketplace add tenlowga-cloud/site-crew
```

```bash
/plugin install site-crew@site-crew
```

```bash
/plugin install impeccable@site-crew
```

Restart Claude Code, then say: "log in to Site Crew with key <your key>". After that: "build me a website for ...".

## Claude.ai or Claude Cowork

1. Download `dist/site-crew.skill` and `dist/impeccable.skill`. Settings > Capabilities > Skills > Upload skill, both.
2. Settings > Connectors > Add custom connector: paste your connector URL, name it Site Crew.
3. New chat: "build me a website for ...".

## Grok CLI / Grok Build

```bash
git clone https://github.com/tenlowga-cloud/site-crew
```

```bash
cp -r site-crew/grok/.grok site-crew/grok/AGENTS.md /path/to/your-project/
```

```bash
cd /path/to/your-project && python3 .grok/skills/site-crew/scripts/sitecrew.py login <your key>
```

Then `grok --trust`, pick `grok-4.7` with `/model`, and say "build me a website for ...".

## Grok Bot

One Bot. Follow `grok/BOT-DESCRIPTION.md`, give it the two skill folders, and add your connector URL as an MCP integration.

## First run

The first time, Site Crew explains why it does each step and hands you a field guide at the end. After that it just builds. Say "teach me" or "just do it" to switch.

## Questions or access

Contact the author (github.com/tenlowga-cloud).

## License

Site Crew: proprietary, all rights reserved; use requires an active key (see LICENSE). Impeccable: Apache-2.0, by Paul Bakaus (see THIRD_PARTY.md).
