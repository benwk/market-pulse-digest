---
name: setup
description: First-time setup of Market Pulse, step by step, from a fresh private copy of the repository to the first digest arriving by email. Use when the user asks to set up, install, configure or get started, or when any secret, variable or the prompt is not set up yet.
---

# Set up Market Pulse

Guide her through the nine checkpoints below, in order. Read `AGENTS.md` first and follow its rules throughout, especially: never ask for or handle API keys, and explain each command before running it.

At the start, tell her in two or three sentences what will happen: you will check her tools, connect to GitHub, she will add two keys on the GitHub website, you will write her prompt together, then run a preview and a real email. It takes about 20 to 30 minutes.

At each checkpoint, run the check. If it passes, say so in one line and move on. If it fails, help her fix it, then run the check again. Do not skip ahead.

## 1. Tools

Check: `git --version` and `gh --version`.

- `git` missing on a Mac: running `git --version` usually opens an installer for Apple's Command Line Tools. Ask her to click Install, wait for it to finish, then check again.
- `gh` missing: if `brew --version` works, run `brew install gh`. Otherwise ask her to download and open the macOS installer (the file ending `macOS_universal.pkg`) from https://github.com/cli/cli/releases/latest, then check again. On Windows, use https://cli.github.com.

## 2. Signed in to GitHub

Check: `gh auth status`.

If she is not signed in, she must do this herself, because it opens her browser. Ask her to open the Terminal app (on a Mac: press Cmd+Space, type Terminal, press Enter), run `gh auth login`, and choose: GitHub.com → HTTPS → Yes (authenticate Git) → Login with a web browser. She copies the one-time code shown, pastes it into the browser page, and approves. Then check again.

## 3. The right repository, and private

Check, from the repository folder:

```bash
gh repo view --json nameWithOwner,visibility,isTemplate --jq '.nameWithOwner + " " + .visibility'
```

- If `nameWithOwner` is `benwk/market-pulse-digest`, she is in the shared template, not her own copy. Stop. Ask her to open https://github.com/benwk/market-pulse-digest, click **Use this template → Create a new repository**, choose **Private**, then open her new repository in Codex and start this skill again.
- If visibility is `PUBLIC`, explain why it must be private (it will name her clients, and every digest would be visible), then run `gh repo edit --visibility private --accept-visibility-change-consequences` after she agrees.

Pass when it shows her own repository and `PRIVATE`.

## 4. OpenAI and Resend accounts

Ask whether she already has both. If not, walk her through them; she does these on the websites herself:

- **OpenAI API** (separate from a ChatGPT subscription): sign in at https://platform.openai.com, add a payment method and a small amount of credit under Billing, then create a key under API keys. Keep the page open; the key is shown once.
- **Resend**: sign up at https://resend.com **with the email address where she wants to receive the digest**. This matters: without a verified domain, Resend can only send to that address. Then create a key under API Keys.

Pass when she confirms she has both keys ready (do not ask to see them).

## 5. Keys added to GitHub (by her, on the website)

Give her the direct link, built from step 3's `nameWithOwner`:

`https://github.com/<owner>/<repo>/settings/secrets/actions/new`

Ask her to add two secrets, one at a time, with these exact names: `OPENAI_API_KEY` and `RESEND_API_KEY`, pasting each key as the value. Remind her: paste keys only on GitHub, never into this chat.

Check: `gh secret list`. Pass when both names appear.

## 6. Where the digest goes

Ask which address should receive it, and remind her it must be the address she used to sign up to Resend. Then:

```bash
gh variable set EMAIL_TO --body "<address>"
gh variable list
```

Pass when `EMAIL_TO` shows her address.

## 7. Her prompt

Open `prompts/market-pulse.md` and show her what it contains in two sentences. Then interview her, one question at a time:

1. Which sectors should it cover? (Usually one per client.)
2. For each sector: the client's name, the topics to watch, and three to six competitors.
3. Should it focus on the UK, or another market?
4. Anything to always include or always leave out?

Replace every square-bracket placeholder in the first section (`[Sector name …]`, `[Client name]`, `[topics to watch …]`, `[Competitor A]` and so on) with her answers. Keep the Rules and Format sections as they are unless she asks to change them; the Format section's brackets (`[Headline]`, `[Source]` and so on) are meant to stay. Show her the finished sector list and ask her to confirm.

Then commit and push: `git add prompts/market-pulse.md && git commit -m "Add my sectors, clients and competitors" && git push`.

Pass when no placeholder from the first section is left and the push succeeded.

## 8. Preview, then the first email

Run a preview as described in `AGENTS.md` ("How to run a preview"). While it runs (a few minutes), explain that this is exactly what will happen every Monday, just without the email.

Show her the digest and go through four checks with her:

- **Fresh:** every item is from the past 7 days.
- **Real:** she opens two or three links and the story is there.
- **Relevant:** she would have wanted to know.
- **Honest:** a quiet sector says so instead of padding.

If she wants changes, follow the `tune` skill, then come back here.

When she is happy, run it again with `-f send_email=true`. Ask her to check her inbox, and her spam or junk folder. If it is in spam, suggest marking it "not spam" so Monday's arrives normally.

Pass when she confirms the email arrived.

## 9. Done

Tell her, briefly:

- It now runs by itself every Monday at 08:00 London time. GitHub sometimes starts scheduled runs a few minutes late.
- To change what it covers or how it reads, open this repository in Codex and use the `tune` skill.
- To see past runs or run it by hand: GitHub → her repository → Actions → Market Pulse.
- Costs: each run uses a small amount of OpenAI credit; she can see usage at platform.openai.com/usage.
- She can check her company's policy on automated emails into a work inbox.
