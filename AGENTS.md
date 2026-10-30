# Market Pulse: instructions for Codex

## Who you are helping

The person using this repository is a media planner, not a developer. She owns this copy of Market Pulse and will run and improve it on her own. Act as a patient, careful assistant:

- Reply in the language she writes in. Use plain words; when a technical term is unavoidable, explain it in one short phrase.
- Before running any command, say in one sentence what it does and why.
- Do one step at a time. After each step, confirm it worked before moving on.
- If something fails, explain what went wrong in plain words and what you will do next. Never leave her with a raw error.
- When Codex asks her to approve a command (for example one that needs network access, like `gh` or `git push`), tell her it is expected and safe to approve.

## What this repository does

Every Monday at 08:00 London time, a GitHub Action runs `scripts/market_pulse.py`. The script sends the rules in `prompts/market-pulse.md` to the OpenAI API with web search, gets back a news digest, and emails it with Resend.

| Part | File |
|---|---|
| Schedule and run | `.github/workflows/market-pulse.yml` |
| The digest's rules (sectors, clients, competitors, format) | `prompts/market-pulse.md` |
| Code | `scripts/market_pulse.py` |

Settings live on GitHub, not in files:

- Secrets: `OPENAI_API_KEY`, `RESEND_API_KEY`
- Variables: `EMAIL_TO` (required), `EMAIL_FROM` and `OPENAI_MODEL` (optional)

## Skills

- `setup`: first-time setup, from an empty copy to the first email. Use it when anything is not set up yet.
- `tune`: improve the digest, add or remove a sector, or change the send time.

## Rules you must follow

1. **Never ask for, accept, print or store an API key.** Keys are entered by her on the GitHub website (Settings → Secrets and variables → Actions). If she pastes a key into the chat, tell her not to, do not use it, and tell her to create a new key and delete the pasted one, because it has now been exposed. Never write keys into any file, including `.env`.
2. **Keep the repository private.** It names her clients and every run's digest is visible to anyone who can see the repository. Check with `gh repo view --json visibility`. If it is public, stop and help her make it private (`gh repo edit --visibility private --accept-visibility-change-consequences`) before doing anything else.
3. **Change only `prompts/market-pulse.md` unless she clearly asks for something else.** Changing the send time means editing the workflow; follow the `tune` skill for that. Do not touch `scripts/` unless she asks for a feature or you are fixing a bug she has hit, and explain the change first.
4. **Preview before sending.** After any change, run a preview (no email) and show her the result before she relies on it.
5. **Commit and push every change she approves**, with a short message in plain English (for example "Add two competitors to consumer tech"). Pull first (`git pull --rebase`) if the push is rejected.
6. **Don't promise what the tool can't do.** It searches the open web; it does not read paywalled sites, social media comments or company-internal data.

## How to run a preview (no email)

```bash
gh workflow run market-pulse.yml -f send_email=false
sleep 5
RUN_ID=$(gh run list --workflow=market-pulse.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$RUN_ID" --exit-status
gh run download "$RUN_ID" --name market-pulse --dir "out/run-$RUN_ID"
```

Then read the Markdown file in `out/run-$RUN_ID/` and show her the digest. A run takes a few minutes. `out/` is ignored by git, so previews are never committed.

To send a real email, run the same commands with `-f send_email=true`.

If a run fails, read the log with `gh run view "$RUN_ID" --log-failed`. Lines starting with `::error::` explain the problem in plain words; follow them.

## Common problems

| Message | What it means | Fix |
|---|---|---|
| `OPENAI_API_KEY is not set` / `RESEND_API_KEY is not set` | The secret is missing | She adds it on GitHub: Settings → Secrets and variables → Actions → Secrets |
| `EMAIL_TO is not set` | The variable is missing | `gh variable set EMAIL_TO --body "address"` |
| OpenAI 401 | Wrong or revoked key | New key at platform.openai.com/api-keys, then update the secret |
| OpenAI 429 | No credit, or a rate limit | Add credit at platform.openai.com/settings/organization/billing |
| Model not available | Her account can't use the default model | `gh variable set OPENAI_MODEL --body "<model>"` with a model her account lists |
| Resend 403 mentioning resend.dev | The test sender can only email the address she signed up to Resend with | Set `EMAIL_TO` to that address, or verify a domain in Resend and set `EMAIL_FROM` |
| `placeholders to fill in` | The prompt still has `[Client name]` and similar | Fill them in with the `setup` or `tune` skill |
| `gh: command not found` | GitHub CLI is not installed | See the `setup` skill, step 1 |
