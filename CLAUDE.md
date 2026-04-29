# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository is a data-only collection of Japanese national holidays in CSV format. There is no build system, test suite, or executable code.

## Data Files

- `2025.csv` / `calendar.csv` — identical files; both contain Japanese holidays from 2025 onward
- Format: two columns, `日付` (YYYY-MM-DD) and `祝日名` (holiday name in Japanese)
- Holiday types include: 祝日 (national holidays), 振替休日 (substitute holidays), 休日 (days off), and 大晦日 (New Year's Eve)

## Maintenance

When updating for a new year, append the new year's entries to both `2025.csv` and `calendar.csv` in the same order and format — the files must remain identical.
