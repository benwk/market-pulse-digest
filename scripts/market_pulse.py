#!/usr/bin/env python3
"""Market Pulse: a weekly news digest, written by OpenAI with web search and sent by email.

Environment variables
  OPENAI_API_KEY   required
  OPENAI_MODEL     optional, defaults to DEFAULT_MODEL
  RESEND_API_KEY   required when sending email
  EMAIL_TO         required when sending email; comma-separated addresses
  EMAIL_FROM       optional, defaults to Resend's test sender
  SEND_EMAIL       "false" to skip sending (the digest is still saved and printed)
  SCHEDULE         set by GitHub Actions to the cron line that started the run
  PROMPT_FILE      optional, defaults to prompts/market-pulse.md
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

import markdown

ROOT = Path(__file__).resolve().parent.parent
LONDON = ZoneInfo("Europe/London")
DEFAULT_MODEL = "gpt-5"
DEFAULT_FROM = "Market Pulse <onboarding@resend.dev>"
USER_AGENT = "market-pulse-digest/1.0"


def fail(message: str) -> None:
    print(f"::error::{message}")
    sys.exit(1)


def should_run(schedule: str, now_london: dt.datetime) -> bool:
    """GitHub cron runs in UTC, so the workflow has two Monday triggers.

    07:00 UTC is 08:00 in London during British Summer Time;
    08:00 UTC is 08:00 in London the rest of the year.
    Only the trigger that matches London's current offset goes ahead.
    Manual runs (no schedule) always go ahead.
    """
    if not schedule:
        return True
    is_bst = now_london.utcoffset() == dt.timedelta(hours=1)
    if schedule.startswith("0 7 "):
        return is_bst
    if schedule.startswith("0 8 "):
        return not is_bst
    return True


PLACEHOLDERS = ("[Client name]", "[Sector name", "[Competitor A]", "[Competitor B]", "[Competitor C]", "[topics to watch")


def explain_http_error(url: str, code: int, body: str) -> str:
    """Turn the most common API errors into plain-English next steps."""
    lowered = body.lower()
    if "api.openai.com" in url:
        if code == 401:
            return "OpenAI rejected the API key. Create a new key at platform.openai.com/api-keys and update the OPENAI_API_KEY secret."
        if code == 429:
            return ("OpenAI says the account has no credit or hit a rate limit. Add credit at "
                    "platform.openai.com/settings/organization/billing, wait a minute, then run again.")
        if "model" in lowered and code in (400, 403, 404):
            return ("Your OpenAI account can't use this model. Set the OPENAI_MODEL variable to a model "
                    "listed at platform.openai.com/docs/models and run again.")
    if "api.resend.com" in url:
        if code == 403 and any(s in lowered for s in ("resend.dev", "testing emails", "verify a domain")):
            return ("Resend's test sender can only email the address you signed up to Resend with. "
                    "Set EMAIL_TO to that address, or verify your own domain in Resend and set EMAIL_FROM.")
        if code in (401, 403):
            return "Resend rejected the API key. Create a new key at resend.com/api-keys and update the RESEND_API_KEY secret."
        if code == 422:
            return "Resend could not accept the email addresses. Check EMAIL_TO (and EMAIL_FROM, if you set it)."
    return ""


def post_json(url: str, payload: dict, api_key: str, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        hint = explain_http_error(url, error.code, body)
        if hint:
            print(f"::error::{hint}")
        fail(f"{url} returned HTTP {error.code}: {body[:1000]}")
    except urllib.error.URLError as error:
        fail(f"Could not reach {url}: {error.reason}")
    return {}


def build_prompt(rules: str, today: dt.date) -> str:
    return (
        f"Today is {today:%A %-d %B %Y} (UK time). Using web search, create my "
        f'"Market Pulse" news digest for the 7 days up to and including today.\n\n'
        f"{rules.strip()}\n\n"
        "Return only the digest, in Markdown. No preamble, and no closing offer of further help."
    )


def output_text(response: dict) -> str:
    parts = []
    for item in response.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))
    return "\n".join(parts).strip()


def write_digest(api_key: str, model: str, prompt: str) -> str:
    response = post_json(
        "https://api.openai.com/v1/responses",
        {"model": model, "tools": [{"type": "web_search"}], "input": prompt},
        api_key,
        timeout=900,
    )
    status = response.get("status")
    if status != "completed":
        details = response.get("incomplete_details") or response.get("error")
        fail(f"OpenAI response status was {status!r}: {details}")
    text = output_text(response)
    if not text:
        fail("OpenAI returned no text.")
    return text


def to_html(digest_md: str) -> str:
    body = markdown.markdown(digest_md, extensions=["extra", "sane_lists"])
    return f"""<!doctype html>
<html><body style="margin:0;padding:24px;background:#ECEDF1;">
<div style="max-width:680px;margin:0 auto;background:#FFFFFF;border:1px solid #DADDE4;border-radius:12px;padding:32px;font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#1B1F27;">
{body}
<p style="margin-top:32px;font-size:12px;color:#5D626D;">Generated automatically with web search. Check sources before acting on them.</p>
</div></body></html>"""


def send_email(api_key: str, sender: str, recipients: list[str], subject: str, digest_md: str) -> str:
    response = post_json(
        "https://api.resend.com/emails",
        {
            "from": sender,
            "to": recipients,
            "subject": subject,
            "html": to_html(digest_md),
            "text": digest_md,
        },
        api_key,
        timeout=60,
    )
    return response.get("id", "")


def main() -> None:
    now_london = dt.datetime.now(LONDON)
    schedule = os.environ.get("SCHEDULE", "").strip()
    if not should_run(schedule, now_london):
        print(f"Skipping: trigger '{schedule}' is not 08:00 in London today.")
        return

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not openai_key:
        fail("OPENAI_API_KEY is not set. Add it under Settings > Secrets and variables > Actions > Secrets.")
    model = os.environ.get("OPENAI_MODEL", "").strip() or DEFAULT_MODEL

    send = os.environ.get("SEND_EMAIL", "true").strip().lower() != "false"
    recipients = [a.strip() for a in os.environ.get("EMAIL_TO", "").split(",") if a.strip()]
    resend_key = os.environ.get("RESEND_API_KEY", "").strip()
    if send and not resend_key:
        fail("RESEND_API_KEY is not set. Add it under Settings > Secrets and variables > Actions > Secrets.")
    if send and not recipients:
        fail("EMAIL_TO is not set. Add it under Settings > Secrets and variables > Actions > Variables.")

    prompt_file = ROOT / os.environ.get("PROMPT_FILE", "prompts/market-pulse.md")
    if not prompt_file.exists():
        fail(f"Prompt file not found: {prompt_file}")
    rules = prompt_file.read_text(encoding="utf-8")
    left = [p for p in PLACEHOLDERS if p in rules]
    if left:
        fail(f"The prompt file still has placeholders to fill in: {', '.join(left)}. "
             "Replace them with your own sectors, clients and competitors, then run again.")
    today = now_london.date()
    prompt = build_prompt(rules, today)

    print(f"Writing the digest with {model} and web search. This can take a few minutes.")
    digest = write_digest(openai_key, model, prompt)

    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"market-pulse-{today.isoformat()}.md"
    out_file.write_text(digest + "\n", encoding="utf-8")
    print(f"Saved {out_file.relative_to(ROOT)}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(digest + "\n")

    if not send:
        print("SEND_EMAIL is false, so no email was sent. The digest is in the run summary.")
        return

    subject = f"Market Pulse · {today:%-d %b %Y}"
    sender = os.environ.get("EMAIL_FROM", "").strip() or DEFAULT_FROM
    email_id = send_email(resend_key, sender, recipients, subject, digest)
    print(f"Sent to {', '.join(recipients)} (Resend id {email_id}).")


if __name__ == "__main__":
    main()
