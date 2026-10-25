# Market Pulse digest

A weekly news digest for agency planners. Every Monday at 08:00 (London time) it searches the web for the past week's news in the sectors you choose, writes a short source-linked summary for each item, and emails it to you.

It runs on GitHub Actions, uses the OpenAI API (with web search) to write the digest and [Resend](https://resend.com) to send the email. You don't need to write any code: everything you change lives in one text file, `prompts/market-pulse.md`.

## How it works

| Part | Where it lives |
|---|---|
| **Trigger:** every Monday, 08:00 London time | `.github/workflows/market-pulse.yml` |
| **Data:** web search over the past 7 days | OpenAI's web search tool |
| **Judgement:** your sectors, clients, competitors and rules | `prompts/market-pulse.md` |
| **Action:** an HTML email to you | Resend |

## Set it up (about 20 minutes)

### 1. Make your own private copy

Click **Use this template → Create a new repository**, and choose **Private**.

Keep it private: your prompt names your clients and competitors.

### 2. Get an OpenAI API key

1. Sign in at [platform.openai.com](https://platform.openai.com).
2. Add a payment method under **Billing**. The API is billed separately from ChatGPT Plus.
3. Create a key under **API keys** and copy it.

### 3. Get a Resend API key

1. Sign up at [resend.com](https://resend.com) with the email address that should receive the digest.
2. Create a key under **API Keys** and copy it.

Without a verified domain, Resend's test sender (`onboarding@resend.dev`) can only send to the address you signed up with. To send to colleagues, verify a domain in Resend and set `EMAIL_FROM` (step 4).

### 4. Add the keys and settings to your repository

In your copy on GitHub: **Settings → Secrets and variables → Actions**.

Under **Secrets**, add:

| Name | Value |
|---|---|
| `OPENAI_API_KEY` | your OpenAI key |
| `RESEND_API_KEY` | your Resend key |

Under **Variables**, add:

| Name | Value |
|---|---|
| `EMAIL_TO` | where to send the digest; separate several addresses with commas |
| `EMAIL_FROM` | optional; e.g. `Market Pulse <digest@yourdomain.com>` once your domain is verified |
| `OPENAI_MODEL` | optional; defaults to `gpt-5` |

### 5. Write your prompt

Open `prompts/market-pulse.md` on GitHub, click the pencil icon, and replace everything in square brackets with your own sectors, clients and competitors. Commit the change.

The date and the "use web search" instruction are added automatically, so the prompt only needs your sectors, rules and format.

### 6. Run it once

Go to **Actions → Market Pulse → Run workflow**.

- Leave **Send the email** ticked to receive it now.
- Untick it to preview the digest on the run's summary page without sending anything.

A run usually takes a few minutes. After that it runs by itself every Monday.

## Tuning it

The digest is only as good as the rules in `prompts/market-pulse.md`. If it misses something, or includes things you don't need, change the rules and run it again. That is how you tune an agent.

Things to check on each digest:

- **Fresh:** every item is dated within the past 7 days.
- **Real:** open a few links; the story is there.
- **Relevant:** you would have wanted to know.
- **Honest:** a quiet week says so, rather than padding.

## Good to know

- **Timing.** GitHub schedules run in UTC, so the workflow has two Monday triggers (07:00 and 08:00 UTC) and only the one that is 08:00 in London goes ahead. GitHub can start scheduled runs a few minutes late.
- **Costs.** One run a week uses a small amount of OpenAI API credit (model use plus web searches). Resend's free plan and GitHub's free Actions minutes cover a weekly email.
- **Copies.** Each run's digest is attached to the run as a download, and shown on its summary page.
- **Company policy.** Check your company's rules before sending automated emails into a work inbox or using client names with external AI services.

## Run it on your own computer (optional)

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=... RESEND_API_KEY=... EMAIL_TO=you@example.com
python scripts/market_pulse.py
```

Set `SEND_EMAIL=false` to write the digest to `out/` without sending it.
