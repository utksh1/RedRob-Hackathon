# 🏆 OFFICIAL PROBLEM STATEMENTS — Full Detail (Plain English)

> **What is this document?**
> Every **official topic** the hackathon gave, explained in plain English with full depth.
>
> **Everything here is OFFICIAL** (from the hackathon website + the intro session). My own *ideas* are in separate files (`02_REDROB_DEEP_DIVE_AND_IDEAS.md` and `04_CUSTOM_WINNING_IDEAS.md`).

---

## 📊 ALL TOPICS AT A GLANCE (how many are there?)

| Track | Topic | Coding needed? | What to submit |
|---|---|---|---|
| **Track 1** | Intelligent Candidate Discovery | Yes | Code + output file + doc |
| **Track 2 — PS1** | AI Systems Architect | No | PDF deck |
| **Track 2 — PS2** | AI Growth Strategist | No | PDF deck |
| **Track 2 — PS3** | Everyday AI Innovator | No | PDF deck |
| **Track 3** | Create the Buzz (social media) | No | One public post |

> **Total = 5 official topics** (1 + 3 + 1). **There are no more than these.** I confirmed this from both the official page and the intro session.

> **One confusion cleared:** the website mentions "Problem statement 22" and "Problem statement 3" in places. That's just internal numbering —
> - "Problem statement 22" = Track 2's **PS2** (the MBA/business one)
> - "Problem statement 3" = Track 2's **PS3** (the beginners one)
> There is no new/extra topic.

---
---

# 🥇 TRACK 1 — THE DATA & AI CHALLENGE
## Topic: "Intelligent Candidate Discovery"
## Prize: ₹10 Lakh

### 🔴 The problem (in plain English)

Imagine a company posts a job. **Thousands of people** apply for that single role. How does the company figure out **who's the best** among them?

Today, computers mostly just **match words** — this is called a "keyword filter." Its flaw:

- The job says: *"Must know JavaScript"*
- The computer only shows resumes that contain the exact word "JavaScript"
- **But** if someone wrote "JS" (which *is* JavaScript), the computer **rejects** them — even if they're perfect!

This means **great people get dropped** simply because they didn't use the "right word." The problem statement calls these **"hidden gems."**

### 🟢 What you have to build

A **smart AI system** that:
1. Understands the **meaning** behind words (not just the words)
2. Gives each candidate a **rank** — from best (#1) down to less-fit (#100)
3. Also gives a **reason** for each rank (so a human can understand it)

The official description: *"An AI brain for modern hiring"* — one that goes beyond keywords to understand context, predict relevance, and turn a massive talent pool into one precise, ranked shortlist.

### 📥 What you get (input / dataset)

The hackathon gives you a **dataset** containing:
- **Professional profiles** — people's resumes/profiles (LinkedIn-style)
- **Career metadata** — past job titles, companies, years worked, seniority
- **Activity / behavioral signals** — what people do on the platform (how active they are, whether they reply, whether their profile is complete). **👉 This is the most important hidden thing — it's how you'll get ahead of other teams.**
- **Job descriptions (JD)** — the full detail of the role (required skills, experience)

> ⚠️ **The truth:** This dataset isn't public yet. Registered participants get it on the Hack2skill dashboard ("next week," per the intro session). When you have it, give it to me — I'll tailor the plan to it exactly.

### 📤 What to output

A **ranked list file** — for each job, the best candidates in rank order (1, 2, 3...). The format is provided by the hackathon ("predefined format") — follow it **exactly**.

### 📦 What to submit (3 required things)

1. **GitHub repository** — your full code (clean, organized)
2. **Methodology document / README** — a written explanation: what approach you used, why, and how the system works
3. **Ranked output file** — the final answer file (in the correct format)

### ⚖️ What judges look at (judging criteria — OFFICIAL)

1. **Ranking quality** — how accurate your list is (most important)
2. **Methodology clarity** — how clear your document is
3. **Explainability** — *can a human understand why the system made each decision?*

> **👉 The biggest tip (from Felix, Redrob's CEO, in the intro session):**
> *"Spend time with the dataset before you start building. The signals in the data will tell you more than any architecture decision."*
> Meaning — don't rush to code. First study the data closely.

### 🏅 Track 1 prizes (full list)

| Award | Prize | Winners |
|---|---|---|
| Grand Champion | ₹2 Lakh | 1 |
| Elite Builders | ₹5 Lakh | 5 |
| Special Tech Awards | ₹2 Lakh | 50+ (flexible) |
| Strong Performers | ₹1 Lakh | 10 |

> **Note:** The detailed step-by-step build plan is in `06_TRACK1_EXECUTION_PLAN.md`. This file just explains the topic.

---
---

# 🥈 TRACK 2 — THE IDEATHON
## Topic: "Creating the Future of AI"
## Prize: ₹30 Lakh (the biggest pool!)

### What is this track? (in plain English)
**No coding here.** You have to think of an **idea** and explain it in a **PDF presentation (deck)** — up to **10 slides** (no more).

This track has **3 separate topics** (PS1, PS2, PS3). **You pick just one** — whichever fits you best.

### Every deck must have these 5 things:
1. **Problem** — what's wrong (start from a **specific** person/situation)
2. **Solution** — what your idea is and how it works
3. **User journey** — how a person uses it (step by step)
4. **Visuals** — drawings/mockups/screenshots (optional, but they help a lot)
5. **Impact** — what good it does in India

> **Felix's tip:** *"Keep the deck under 10 slides. Clarity always beats quantity. The best pitch starts with one specific problem — one person, one moment, one thing harder than it should be — then shows the fix."*

---

## 📌 PS1 — THE AI SYSTEMS ARCHITECT: "Reimagining Work"

**Who it's for:** Developers, engineers, system architects — people who are technical but want to **think/design** here, not write code.

**The topic (in plain English):** Design a **groundbreaking technical AI system** that changes the way work gets done. For example:
- **Autonomous agents** — AI that does work on its own (like a robot-assistant that makes its own decisions)
- **Super-smart search** — a much better search system
- **AI orchestration** — multiple AIs working together
- **AI co-pilots** — AI that works alongside a human and makes them far more productive

**Submit:** A PDF deck with the system design + how it works (with a diagram).

> **Its best ideas are in `02_REDROB_DEEP_DIVE_AND_IDEAS.md`** (e.g., "SkillProof" — AI Skill-Verification, based on Redrob's "Skill Tests" feature; or "OutreachIQ" — an autonomous sales/GTM agent).

---

## 📌 PS2 — THE AI GROWTH STRATEGIST: "Making AI Go Viral"

**Who it's for:** MBA students, product managers, growth/marketing people. *(The website also calls this "Problem statement 22.")*

**The topic (in plain English):** How would you make a revolutionary AI product **explode (go huge)** in India? Build the full plan:
- The journey from a user's first click to becoming a loyal fan
- How to build **trust**
- How to **make money** (monetization)
- How it goes **viral** (people tell their friends)

**Submit:** A PDF deck with a growth/business plan (with numbers — MBA judges look for numbers).

> **Its most powerful idea is in `02_REDROB_DEEP_DIVE_AND_IDEAS.md`** — "Road to 10 Million" (a plan to take Redrob to 1 crore users, based on their own target).

---

## 📌 PS3 — THE EVERYDAY AI INNOVATOR: "Life, Made Better"

**Who it's for:** Students, designers, creators, **first-time participants (beginners)**. This topic was **specifically designed for beginners.**

**The topic (in plain English):** Think of a **SIMPLE** AI feature that genuinely improves the **everyday life** of an ordinary person in India. Not complex — just real, clear, and made for India.

**Submit:** A PDF deck with one simple AI feature idea + how it works.

> **Best ideas are in `02_REDROB_DEEP_DIVE_AND_IDEAS.md`** (e.g., "VoiceResume" — speak to build a resume + auto-apply, based on Redrob's "Resume Builder" feature).

### 🏅 Track 2 prizes (full list)

| Award | Prize | Winners |
|---|---|---|
| Track Champion | ₹2 Lakh | 1 |
| Runner Ups | ₹2 Lakh | 2 |
| Merit Winners | ₹2 Lakh | 5 |
| Emerging Innovators | ₹1.5 Lakh | 15 |
| Promising Ideas | ₹1.5 Lakh | 30 |
| Recognition | ₹1 Lakh | 50+ |

---
---

# 🥉 TRACK 3 — SOCIAL MEDIA CHALLENGE
## Topic: "Create the Buzz"
## Prize: ₹10 Lakh · ⚠️ Earliest deadline (4 June)

### What is this track? (in plain English)
Just make a **social media post** sharing your **honest, original opinion** about AI and India. Add the hashtag **#IndiaRuns**. The post must be **public**. That's it!

> **The easiest track. 525+ winners. ~20 minutes of work.**

### Rules (required, or your entry won't count):
- The post must be **public** (not private)
- The hashtag **#IndiaRuns** must be present
- You must be **registered**
- The content must be **original** (made by you)
- Any platform — LinkedIn / X (Twitter) / Instagram / YouTube / Medium / blog

### Themes (pick one of 7):
| Theme | Meaning |
|---|---|
| The Next Big Thing | Coolest upcoming AI products |
| **Hiring Heroes** ⭐ | How AI is changing jobs |
| AI in Your Day | Everyday AI things |
| **Redrob Rulz** ⭐ | A cool use of the Redrob platform |
| Level Up Your Life | Making work easier with AI |
| The Creator Economy | AI and creators |
| Digital Dreams | The future of online careers |

> ⭐ Pick **"Hiring Heroes" or "Redrob Rulz"** — they connect directly to Redrob, so judges will like them more.

### 👉 The most important point (Felix said this):
*"Original thinking matters more than production quality."*
Meaning — one simple but honest, thoughtful point beats one expensive but empty video. And: *"AI is important"* is **not** an opinion. Give your **real, specific** take.

### 🏅 Track 3 prizes (525+ winners!)

| Award | Prize | Winners |
|---|---|---|
| Grand Winners | ₹1 Lakh | 5 |
| Star Creators | ₹1.5 Lakh | 20 |
| High Engagement | ₹2 Lakh | 50 |
| Community Winners | ₹2 Lakh | 100 |
| Participation Reward | ₹1.5 Lakh | 200 |
| Recognition Pool | ₹1.5 Lakh | 150+ |
| Surprise Drops | ₹50K | Flexible |

> **Ready-to-post drafts are in `08_TRACK3_EXECUTION_PLAN.md`.**

---
---

# 📐 ADVANCED — "Winning vs Losing" + How Scoring Really Works

> This section shows the difference between a **winning** and a **losing** submission in each topic. Use it to self-check your own work.

## TRACK 1 — Candidate Discovery

| Aspect | ❌ Losing submission | ✅ Winning submission |
|---|---|---|
| Approach | Just cosine similarity | 2-stage retrieve→rerank + Learning-to-Rank |
| Signals | Only skills/text | Behavioral signals too (activity, intent) |
| Output | Just a ranked list | List + a "why" for each candidate |
| India-edge | Nothing | Multilingual + hidden-gem + fairness |
| Proof | "We built it well" | NDCG/MAP table + ablation + error analysis |
| Doc | 1-paragraph README | Structured methodology + architecture diagram |

## TRACK 2 — Ideathon (all PS)

| Aspect | ❌ Losing deck | ✅ Winning deck |
|---|---|---|
| Problem | "India needs AI" (broad) | One specific person/moment |
| Idea | Generic "AI chatbot for X" | A Redrob Coming-Soon feature / GTM |
| Slides | 20+ text-heavy | ≤10, visual, one idea per slide |
| Redrob fit | Didn't even mention it | A full "Redrob fit" slide |
| Business | Nothing | Model + numbers (required in PS2) |
| Tech | Vague | A tech-stack slide (PS1) |
| Visuals | Stock photos | Real mockups/diagrams |

## TRACK 3 — Social Media

| Aspect | ❌ Losing post | ✅ Winning post |
|---|---|---|
| Opinion | "AI is the future" (generic) | A bold, specific point of view |
| Hook | Boring first line | A scroll-stopping hook |
| Voice | Lifeless AI-generated text | Authentic, personal |
| Hashtag | #IndiaRuns missing | #IndiaRuns + 2-3 relevant |
| Engagement | No call to action | A question at the end + fast replies |
| Theme | Random | Hiring Heroes / Redrob Rulz |

---

# 🎯 SELF-CHECK: Ask these before submitting

For every submission — if all four are "yes," you're in the top tier:
1. **Does this solve a REAL, specific problem?** (not broad)
2. **Does it connect to Redrob's business (hiring / sales / cheap-multilingual AI)?**
3. **Does it look like it WORKS?** (Track 1: demo/metrics; Track 2: clear flow; Track 3: real voice)
4. **Is the India angle clear?** (vernacular / Tier-2-3 / cost)

> If any is "no" — fix that before submitting.

---

# 📊 PRIZE STRATEGY — Where to spend effort (by ROI)

| Track | Total prize | Winners | Your chance of winning | Effort | ROI |
|---|---|---|---|---|---|
| Track 1 | ₹10L | ~66 | High (objective, less competition) | High | ⭐⭐⭐⭐⭐ |
| Track 3 | ₹10L | 525+ | High (many winners) | Low | ⭐⭐⭐⭐⭐ |
| Track 2 | ₹30L | ~103 | Medium (subjective, more competition) | Medium | ⭐⭐⭐⭐ |

> **Best ROI plan:** Definitely do Track 1 (high effort, high chance) + Track 3 (low effort, high chance). Do Track 2 if you have time left (by reusing the Track 1 work).

---
---

# ✅ ALL CONFIRMED (the honest truth)

- **Official topics: only 5** (the ones above). Nothing more.
- Prizes, dates, rules — all verified from official sources.
- **The Track 1 dataset hasn't arrived yet** — that's pending on your end.
- **There's a minor confusion about the registration date** (8 June vs 28 June) — register early to be safe.

> Next step: what to build inside these topics is ready in `02_REDROB_DEEP_DIVE_AND_IDEAS.md`. And how to build it is step-by-step in the three TRACK files.
