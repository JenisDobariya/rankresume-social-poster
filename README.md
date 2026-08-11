# Social Auto Poster — RankResume.pro daily content agent

A Python agent that posts daily to LinkedIn and Instagram promoting
RankResume.pro — with a real content strategy behind it, not just "post
something every day." No third-party scheduler, no subscription.

## The strategy

Posting the same pitch daily trains people to scroll past it. This project
rotates through distinct **content pillars** — different angles for why
someone should care about RankResume.pro — so consecutive posts never repeat
the same argument. See `content_pillars.py` for the full list: the ATS
rejection problem, advice for freshers, advice for international job seekers,
before/after resume rewrites, standalone resume tips (product mentioned only
lightly — builds trust/reach), objection handling ("why not just use a free
template"), feature deep-dives, stat-driven hooks, build-in-public updates,
broader career advice, and occasional direct CTAs.

**How repetition is actually prevented** (`history_tracker.py`): every post
is logged with its pillar and format. The picker excludes any pillar used in
the last 14 days, and only reuses one early if every pillar is on cooldown —
in which case it picks whichever was used longest ago. It also tracks the
image/video ratio over the last 10 days and nudges the format choice back
toward ~70% image / 30% video if one drifts too far from that mix.

**How content is generated**: `caption_generator.py` sends the pillar's angle
to Claude along with a fixed set of real product facts (`product_facts.py`)
— audience, features, URL — so it can't invent claims about the product. It
returns both the caption text and a short "media brief": a separate, punchy
headline for the accompanying image, since a caption that just repeats the
image (or vice versa) wastes the space.

**How the visual is made** (`media_generator.py`): a branded template card —
headline, supporting line, RankResume.pro URL, brand colors — rendered with
Pillow. For pillars marked as video, the brief is split into a few slides and
stitched into a short mp4 with moviepy. This is a deliberately realistic
free-to-build tier: no AI image/video generation API is required. See
"Upgrading the visuals" below for how to plug one in when you want variety
beyond the template look.

**Platform-specific link handling** — this matters and is easy to get wrong:
- **LinkedIn** quietly reduces reach on posts with an outbound link in the
  body. The caption prompt is instructed to end with "Link in the first
  comment" instead of the raw URL — you (or a small follow-up script) drop
  the link as the first comment after posting.
- **Instagram** captions never render links as clickable at all, regardless
  of what you do. The caption ends with "Link in bio" — keep your bio link
  pointed at RankResume.pro.

## What it does, end to end

1. Picks today's content pillar, respecting the no-repeat cooldown
2. Decides image or video, keeping the mix balanced
3. Generates a caption + media brief per platform with Claude
4. Renders the branded card (or short video) locally
5. Posts to LinkedIn (official API) and Instagram (instagrapi, personal account)
6. Logs the result so tomorrow's pick avoids repeating today's angle

## 1. Install

```bash
pip install -r requirements.txt
cp .env.example .env
```

## 2. Get your Instagram credentials

This project uses `instagram_poster_unofficial.py` by default — it logs in with
your normal **personal-account** username/password via `instagrapi`, since
Meta's official Graph API only supports Business/Creator accounts.

**Read this before using it:**
- It violates Instagram's Terms of Service — there's no official sanction.
- Automated login + daily auto-posting is exactly the pattern Instagram's abuse
  detection watches for. Outcomes range from a temporary action block to a full
  account restriction, especially on an account you actively use personally.
- No official support — Instagram can break this library at any time.
- Mitigations already built in (they reduce risk, they don't remove it):
  session reuse (`logs/ig_session.json`, avoids logging in fresh every run),
  and a randomized delay before each post.
- Consider warming the account up with normal manual usage for a week or two
  before turning on daily automated posting, and don't run it at the exact
  same second every day (the scheduler's built-in delay already helps here).

Setup: just put your normal login in `.env` as `IG_USERNAME` / `IG_PASSWORD`.
No developer app, no token, no image hosting — `photo_upload()` takes a local
file path directly, unlike the official API.

**If you'd rather use the official, ToS-compliant route instead** (requires
Business/Creator conversion, see the earlier message for why that's often less
disruptive than it sounds — private Facebook Page, no visible profile change
beyond a category label): set `USE_UNOFFICIAL_INSTAGRAM = False` at the top of
`main.py` and follow these steps instead:

1. Convert to Business/Creator (Settings → Account type) and link a Facebook Page.
2. [developers.facebook.com](https://developers.facebook.com) → create an app → add **Instagram Graph API**.
3. Generate a token with `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`.
4. Exchange it for a long-lived token (`InstagramPoster.refresh_long_lived_token()` in `instagram_poster.py`); refresh weekly via cron.
5. Get your Business Account ID: `GET /me/accounts` → `GET /{page-id}?fields=instagram_business_account`.
6. Set `IG_ACCESS_TOKEN` and `IG_BUSINESS_ACCOUNT_ID` in `.env`. Note this route needs a **public image URL**, not a local file — host images on S3/Cloudinary/your own server first.

## 3. Get your LinkedIn credentials

1. Go to [linkedin.com/developers](https://www.linkedin.com/developers) → create an app.
2. Add the **"Share on LinkedIn"** product — this grants `w_member_social` and is
   auto-approved for posting to your own profile (no lengthy review needed).
3. Run LinkedIn's OAuth 2.0 3-legged flow once (any OAuth tool or a small local
   script works) to get an access token. It's valid ~60 days.
4. Call `GET https://api.linkedin.com/v2/userinfo` with that token — the `sub`
   field in the response is your member ID. Your URN is `urn:li:person:{sub}`.
5. Put both in `.env` as `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN`.

**Note:** this scope only lets you post to *your own* profile, not a Company Page
or other members' feeds — which is exactly what "post daily as me" needs.

## 4. Get your AI key

Add `ANTHROPIC_API_KEY` in `.env` (used by `caption_generator.py`). Swap the
provider in that file if you'd rather use OpenAI or Gemini.

## 5. Customize the content pillars

Open `content_pillars.py` and edit the list to match what you actually want to
say about RankResume.pro — add pillars, remove ones that don't fit, adjust the
`angle` text (this is what actually gets sent to the AI, so be specific).
Update `product_facts.py` any time the product's features or positioning change.

## 6. Run it

Test without posting anything live first — this still generates real captions
and renders real image/video files locally, so you can review the output:
```bash
python main.py --dry-run
```

Then run for real:
```bash
python main.py
```

Then automate it — two options:

**Option A — system cron** (simplest, good for a VPS or Raspberry Pi):
```bash
crontab -e
# add this line to run daily at 9am:
0 9 * * * cd /path/to/social-auto-poster && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

**Option B — the built-in scheduler** (keep a process running instead of relying on cron):
```bash
python scheduler.py
```
Run this inside `tmux`/`screen`, or wrap it as a `systemd` service, so it survives
terminal closures and reboots.

## Costs

- Instagram (either route): free.
- LinkedIn Posts API: free.
- Claude API for captions: a few cents/month at 1-2 short generations a day.
- Hosting (VPS for cron): ~$5/mo if you don't already have a server; not needed
  for the unofficial Instagram route since it doesn't require image hosting.

Total: effectively free beyond a few cents of LLM usage, versus $15-30/mo for a
SaaS scheduler doing the same job — though note a SaaS scheduler also can't
auto-post to a personal Instagram account either; that constraint is Meta's,
not this project's.

## Upgrading the visuals

The template card is deliberately the free, zero-dependency starting point.
Two natural upgrades once you want more variety:

- **AI-generated backgrounds**: `media_generator.generate_ai_background()` is
  stubbed out with example code for OpenAI's Images API — wire in a key and
  call it before rendering the card, or composite the AI background behind
  the same headline/URL text for a consistent brand layer on top of varied art.
- **Real AI video**: the current video is a template slideshow. Swapping in
  Runway, Pika, or Kling means generating the raw clip via their API first,
  then skipping `generate_video_card` and posting that file directly — same
  poster functions, different upstream source for `media_path`.

## Extending this

- LinkedIn video posting needs a separate upload flow (register upload →
  upload bytes → attach to post) similar to the image flow already in
  `linkedin_poster.py` — currently the pipeline falls back to a text-only
  LinkedIn post on video days; add a `post_video()` method there when ready.
- Add a small follow-up step that posts the RankResume.pro link as the first
  LinkedIn comment right after `post_image()` succeeds (same API, a comment
  endpoint instead of a post endpoint).
- Add Twitter/X or Threads the same way — one poster module each.
- Pull pillar inspiration from real signals (a GitHub commit, a user testimonial,
  a support ticket theme) instead of only the static list in `content_pillars.py`.
