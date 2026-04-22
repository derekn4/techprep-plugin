# techprep-plugin

A Claude Code plugin that coaches you through technical interview prep. Role-agnostic, level-calibrated (junior / mid / senior / staff), and works for any company.

## What it does

- `/tech-coach` — router. Reads your config, asks what today's session is, routes.
- `/tech-coach:coding` — DSA coaching with level-appropriate difficulty.
- `/tech-coach:sysdesign` — system design walkthroughs calibrated to your target level.
- `/tech-coach:behavioral` — STAR-method coaching on your stories.
- `/tech-coach:mock` — full mock interview with a dedicated interviewer subagent.
- `/tech-coach:config` — view or edit your per-user config.

Every session ends with a prep summary file and a check-in on your current status, so you can see what you covered across days.

## Install

```
/plugin marketplace add derekn4/techprep-plugin
/plugin install tech-coach@derekn4
```

Then run `/tech-coach` in any project. On first run it generates a blank config at `~/.claude/tech-coach/config.md` and asks you to fill it in.

## Configure

Edit `~/.claude/tech-coach/config.md`:

```
current_level: mid
target_level: senior
target_company: (company name)
next_interview: YYYY-MM-DD
preferred_language: python
weak_areas:
  - dynamic programming
  - system design scale estimates
strong_areas:
  - trees and graphs
  - concurrency
```

Every subcommand reads this and adapts.

## Status

Early work in progress. MVP targets role-agnostic coding / system design / behavioral coaching with per-user configuration and level-based calibration.

## License

MIT
