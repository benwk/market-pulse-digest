---
name: tune
description: Improve the Market Pulse digest after setup - change what it covers or how it reads, add or remove a sector or competitor, or change the send day and time. Use when the user wants different or better results from the digest.
---

# Tune Market Pulse

Read `AGENTS.md` first and follow its rules. If setup is not finished (no secrets, no `EMAIL_TO`, or placeholders left in the prompt), use the `setup` skill instead.

## Changing what the digest covers or how it reads

1. **Understand the request.** Ask what she wants more of, less of, or different. If she has a recent digest, ask what was wrong with it: missing stories, irrelevant ones, too long, wrong market, too many from one competitor. If she is vague, ask one clarifying question.
2. **Show the change before making it.** Say which lines of `prompts/market-pulse.md` you will change and how, in plain words. Change the smallest thing that will do it. Typical changes:
   - Missing stories about a company → add it by name to that sector's competitors, or add the topic.
   - Too much about one competitor → lower the per-competitor limit in Rules.
   - Not UK-focused enough, or too much → adjust the first paragraph.
   - Too long → fewer items per sector, or a shorter summary.
   - A new kind of item (for example events, regulation) → add it to the topics.
3. **Preview.** Run a preview as described in `AGENTS.md`. Keep the previous preview if there is one, and compare: tell her in two or three bullets what changed in the result.
4. **Decide.** If she is happy, commit and push with a message describing the change. If not, revert with `git checkout prompts/market-pulse.md` or try another change.

Each preview takes a few minutes and uses a little OpenAI credit, so make one meaningful change per preview rather than many small ones.

## Adding or removing a sector

Add or remove a numbered item in the first section of `prompts/market-pulse.md`, following the same pattern as the others: sector name, client, topics, competitors. Then preview as above.

## Changing the send day or time

The schedule is in `.github/workflows/market-pulse.yml`. GitHub runs schedules in UTC, so the workflow has two triggers, one for British Summer Time and one for the rest of the year, and `scripts/market_pulse.py` (`should_run`) only lets the one that matches London time go ahead.

To change the time to H:00 London time on a given day:

1. In the workflow, set the two cron lines to `0 <H-1> * * <day>` (summer) and `0 <H> * * <day>` (winter), where day is 0 for Sunday to 6 for Saturday. Update the comments.
2. In `should_run`, change the two `schedule.startswith("0 7 ")` and `("0 8 ")` checks to the new summer and winter hours.
3. Explain the change to her, commit and push.

Example: Tuesday 09:00 London → `0 8 * * 2` (summer) and `0 9 * * 2` (winter), checks `"0 8 "` and `"0 9 "`.

Note that the schedule only runs from the repository's default branch, and GitHub can start scheduled runs a few minutes late.

## Sending to more people

Without a verified domain, Resend can only send to the address she signed up with. To send to colleagues she needs to verify a domain she controls in Resend (resend.com/domains), then:

```bash
gh variable set EMAIL_FROM --body "Market Pulse <digest@her-domain.com>"
gh variable set EMAIL_TO --body "first@example.com, second@example.com"
```

Suggest she checks her company's policy before sending automated emails to colleagues.
