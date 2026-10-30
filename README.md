# Market Pulse digest

A weekly news digest for agency planners. Every Monday at 08:00 (London time) it searches the web for the past week's news in the sectors you choose, writes a short source-linked summary of each item with why it matters to your client, and emails it to you.

It runs on GitHub Actions, uses the OpenAI API (with web search) to write the digest, and [Resend](https://resend.com) to send the email. You don't write any code: what the digest covers lives in one text file, `prompts/market-pulse.md`, and Codex can set everything up and tune it with you.

## Start here

1. **Make your own private copy.** Click **Use this template → Create a new repository**, give it a name, and choose **Private**. Keep it private: it will name your clients, and every digest appears in its run history.
2. **Open it in Codex.** In the Codex app, start a new chat and ask: *"Clone github.com/YOUR-NAME/YOUR-REPO to my computer and open it."* Approve the commands Codex asks to run.
3. **Type `@setup`** and follow along. Codex checks your tools, connects to GitHub, helps you add your keys, writes your prompt with you, runs a preview and sends your first email. Allow 20 to 30 minutes.

Before you start, have these ready (or create them during setup):

- a GitHub account
- an **OpenAI API** account with a payment method and some credit, at [platform.openai.com](https://platform.openai.com). This is billed separately from ChatGPT Plus.
- a **Resend** account, at [resend.com](https://resend.com), created **with the email address where you want to receive the digest**

## Keep improving it

Open the repository in Codex and type `@tune`, then say what you want: *"more about new product launches"*, *"add Oatly as a competitor"*, *"the healthcare section is too thin"*, *"send it on Tuesdays at 9 instead"*. Codex changes the prompt, runs a preview, shows you the difference, and saves it when you're happy.

Things to check on each digest:

- **Fresh:** every item is dated within the past 7 days.
- **Real:** open a few links; the story is there.
- **Relevant:** you would have wanted to know.
- **Honest:** a quiet week says so, rather than padding.

## How it works

| Part | Where it lives |
|---|---|
| **Trigger:** every Monday, 08:00 London time | `.github/workflows/market-pulse.yml` |
| **Data:** web search over the past 7 days | OpenAI's web search tool |
| **Judgement:** your sectors, clients, competitors and rules | `prompts/market-pulse.md` |
| **Action:** an email to you | Resend |
| **Instructions for Codex** | `AGENTS.md`, `.agents/skills/` |

## Good to know

- **Who it can email.** Without a verified domain, Resend's test sender (`onboarding@resend.dev`) can only send to the address you signed up to Resend with. To send to colleagues, verify a domain you own in Resend and set the `EMAIL_FROM` variable.
- **Timing.** GitHub schedules run in UTC, so the workflow has two Monday triggers (07:00 and 08:00 UTC) and only the one that is 08:00 in London goes ahead. GitHub can start scheduled runs a few minutes late.
- **Costs.** Each run uses a small amount of OpenAI credit (the model plus its web searches); see platform.openai.com/usage. Resend's free plan and GitHub's free Actions minutes cover a weekly email.
- **What it can't see.** It searches the open web. It doesn't read paywalled sites, social media comments or your company's internal data.
- **Company policy.** Check your company's rules before sending automated emails into a work inbox or using client names with external AI services.

## Setting it up without Codex

1. Make a private copy (step 1 above).
2. In your copy: **Settings → Secrets and variables → Actions**.
   - **Secrets:** `OPENAI_API_KEY`, `RESEND_API_KEY`
   - **Variables:** `EMAIL_TO` (required); `EMAIL_FROM` and `OPENAI_MODEL` (optional; the model defaults to `gpt-5`)
3. Edit `prompts/market-pulse.md` on GitHub (pencil icon) and replace the square-bracket placeholders in the first section with your sectors, clients and competitors.
4. **Actions → Market Pulse → Run workflow.** Untick *Send the email* to preview the digest on the run's summary page; leave it ticked to send it.

### Running it on your own computer (optional)

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=... RESEND_API_KEY=... EMAIL_TO=you@example.com
SEND_EMAIL=false python scripts/market_pulse.py
```

`SEND_EMAIL=false` writes the digest to `out/` without sending it.
