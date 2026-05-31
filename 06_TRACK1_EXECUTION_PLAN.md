# 🥇 TRACK 1 — STEP-BY-STEP WINNING PLAN (Full Detail)
## "Intelligent Candidate Discovery" · Coding Track · ₹10 Lakh

> **What is this document?** The full path to winning Track 1 — from today to the final submission (28 June). Every step in plain English, every technical term explained.
>
> **Goal:** To become Grand Champion (₹2L) or an Elite Builder (₹5L). This track is **won on skill** — not on a judge's mood.

---

## 📖 FIRST — Learn the key terms (Glossary)

These words appear often. Learn them once, then everything is easy:

| Term | Simple meaning |
|---|---|
| **Candidate** | A job seeker (the one with the resume) |
| **JD (Job Description)** | The job's details — what skills/experience are needed |
| **Ranking** | Putting candidates in order — best (#1) to less-fit |
| **Keyword filter** | Just matching words (the old, dumb way) |
| **Semantic** | Understanding the **meaning** of words (the smart way) |
| **Embedding** | Turning text into numbers so a computer can compare "meaning" |
| **Bi-encoder** | Fast, rough matching (the first filter) |
| **Cross-encoder** | Slow but deep matching (the final check) |
| **Learning-to-Rank** | Teaching the AI how to produce a good ranking |
| **LambdaMART / LightGBM** | A popular tool that learns ranking |
| **NDCG / MAP / MRR** | Numbers that tell you how good your ranking is |
| **Explainability** | Saying **why** the system made a decision |
| **EDA** | Studying the data closely (before building) |

---

## 🎯 THE WINNING MANTRA (memorize this)

> 90% of teams will build one simple thing: "match the text, compute similarity, rank." That's it.
>
> **You'll do 3 EXTRA things** that make you a winner:
> 1. **A two-stage system** (first a fast filter, then a deep check)
> 2. **Teach the AI to rank** (Learning-to-Rank)
> 3. **Give a REASON with each rank** (explainability)
>
> These 3 things win the medal.

---

## 📅 FULL TIMELINE (today → 28 June)

| Phase | Days | What to do |
|---|---|---|
| **Phase 0** | Now (before the dataset) | Setup + learning + practice |
| **Phase 1** | When the dataset arrives, 2-3 days | Study the data closely (EDA) |
| **Phase 2** | 4-5 days | Build a simple version (baseline) |
| **Phase 3** | 5-7 days | The real smart system (two-stage + Learning-to-Rank) |
| **Phase 4** | 3-4 days | Give reasons (explainability) + India-edge |
| **Phase 5** | 3-4 days | Testing + numbers + improvement |
| **Phase 6** | 3 days | Document + repo + final file |
| **Buffer** | 2 days | Extra time (in case something breaks) |

---
---

## 🔧 PHASE 0 — Setup & Prep (start BEFORE the dataset arrives)

> Don't wait for the dataset. All of this can be done now.

### Step 0.1 — Split the work in the team (max 4 people)
- **Person 1 (ML Lead):** the main system (matching + ranking)
- **Person 2 (Data):** cleaning the data + building features
- **Person 3 (Testing):** computing numbers + writing the reasons
- **Person 4 (Docs):** README + diagram + final packaging

> Working solo? No problem — just spread these roles across different days yourself.

### Step 0.2 — Install the tools
- **Python** (version 3.10 or above)
- These libraries: `pandas`, `numpy`, `scikit-learn`, `lightgbm`, `sentence-transformers`, `rapidfuzz`, `matplotlib`
- A **GitHub** account + create a private repo
- Make folders: `data/`, `src/` (code), `notebooks/` (experiments), `outputs/` (results)

### Step 0.3 — Learn the concepts (the ones you don't know)
On YouTube/docs, understand these 4 things (20-30 min each):
1. **Sentence embeddings** — how to turn text into numbers
2. **Bi-encoder vs cross-encoder** — fast filter vs deep check
3. **Ranking metrics (NDCG)** — how to measure ranking quality
4. **LightGBM ranking** — the tool that learns ranking

### Step 0.4 — Practice: run the whole system on fake data
Before the dataset arrives, make your **own small fake data** (50 candidates, 5 jobs — even in Excel). Run the whole system end-to-end on it once.

**The benefit:** when the real dataset arrives, you just swap the file and everything works — nothing new to learn. You save time.

---

## 🔍 PHASE 1 — Understand the Data (EDA) — THE MOST IMPORTANT PHASE

> **Felix (Redrob CEO) said:** *"Spend time with the dataset first. The signals in the data will tell you more than any architecture decision."*
> Meaning — don't rush to code. First study the data like a detective.

### Step 1.1 — Basic understanding
Ask yourself these questions and find the answers:
- How many candidates are there? How many jobs?
- What info do you have about each candidate? (skills, experience, titles, company, education, location)
- **Where are the behavioral signals?** (they're hidden — like last login, number of applications, response rate, profile completeness). **👉 This is your secret weapon — look for it carefully.**
- **Are labels (correct answers) given?** i.e., does it already say which candidate is good for which job? (graded 0-3, or just yes/no, or nothing)

### Step 1.2 — Check the data's cleanliness
- Where is info missing? (someone's skills empty? experience not listed?)
- How are skills written — as a list? comma-separated? or free-text?
- Is any candidate duplicated?
- Is the JD text clean or a messy paragraph?

### Step 1.3 — Make plots (graphs)
Make these graphs so patterns appear:
- Distribution of experience (how many freshers, how many senior)
- The most common skills
- Location spread (metro vs small towns)
- The pattern of behavioral signals + are they tied to "good candidates"?

### Step 1.4 — Write down 3-4 important findings
Pull concrete observations from EDA that will help later. For example:
- "People who reply quickly are often good fits"
- "30% of candidates have skills in free-text → cleaning needed"
- "Jobs are mostly in metros, but candidates come from small towns too"

**📓 Output:** A notebook (`01_eda.ipynb`) with graphs + these findings. You'll put this in the document later (boosts your clarity score).

---

## 📏 PHASE 2 — Simple Version First (Baseline)

> First build a simple thing that "works." Then improve it. This gives you "a number" to compare against.

### Step 2.1 — The keyword version (simplest = the "enemy" to beat)
Count the **exact match** between the JD's skills and the candidate's skills → rank. This is the old, dumb way. Note its NDCG@10. **You'll beat this.**

### Step 2.2 — The semantic version (a bit smarter)
- Turn the JD text and candidate profile into **embeddings** (i.e., numbers)
- Compute their similarity → rank
- Note its NDCG@10 → it should be better than keyword

### Step 2.3 — Start a comparison table
| Method | NDCG@10 | MAP | MRR |
|---|---|---|---|
| Keyword | ... | ... | ... |
| Semantic | ... | ... | ... |

> This table keeps growing. It goes in the document — the judges see the **improvement in numbers**.

---

## 🏗️ PHASE 3 — The Real Smart System (where you win)

### Step 3.1 — Step one: a fast filter (Retrieval)
- Use embeddings to quickly pull the **top 100 candidates** for each job
- This brings thousands of candidates down to 100 (manageable)
- For big data, use **FAISS** (a fast search tool)

### Step 3.2 — Step two: build features (for each job-candidate pair)
Build these "features" (i.e., numbers describing each pair):
1. **Semantic score** — how much the meaning matches
2. **Cross-encoder score** — a deep match (optional but strong)
3. **Skill overlap** — how many skills match (understanding short forms: JS=JavaScript)
4. **Experience fit** — is the candidate's experience right for the job?
5. **Seniority match** — does the junior/senior level match?
6. **Location fit** — same city? remote okay?
7. **Behavioral signals** — response rate, profile completeness, last active, applications
8. **Title similarity** — do past job titles match the JD?

### Step 3.3 — Step three: TEACH the AI to rank (THE DIFFERENTIATOR)
- Use **LightGBM's** "lambdarank" mode
- This teaches the AI **how to combine** the features above into the best ranking
- Group = job_id (each job is ranked separately)
- Split train/test **by job** (a job shouldn't be in both — otherwise it's cheating, called "data leakage")

> **Why this wins:** simple similarity only matches text. This AI **learns** which signals (behavior + skills + meaning) combine to make a "best fit" — exactly what Redrob wants.

### Step 3.4 — What if labels (correct answers) are NOT given? (Plan B)
Don't panic, two paths:
- **Path 1:** Create pseudo-labels from your own rules (combine role match + skill coverage + experience + activity into a score), then train the AI on that
- **Path 2:** Build a score by logically weighting the features (without AI training)
- In the document, **clearly state** that labels weren't given so you used this approach — judges respect honesty + reasoning

---

## 💡 PHASE 4 — Give Reasons (Explainability) + India-Edge

> This phase is a **direct hit** on the judging criteria. Don't skip it.

### Step 4.1 — A REASON with each candidate (required!)
Give an easy-to-understand reason with each ranked candidate:
```
Rank #1 — Candidate A (Score 91%)
  ✓ Has 6 of the 7 required skills
  ✗ Only Kubernetes is missing
  ↑ Strong signals: 95% response rate, active 2 days ago, profile 100% complete
  ✓ Experience: 6 years (the job needed 5+) — senior-level match
```
- Use **SHAP** or feature importance to justify the "why"
- This **literally** satisfies the "explainability" criterion

### Step 4.2 — India-Edge features (will impress Redrob)
1. **Skill short forms:** JS→JavaScript, ML→Machine Learning, k8s→Kubernetes
2. **Fairness for small colleges:** don't undervalue unknown colleges (keep it neutral)
3. **Hinglish understanding:** if a profile/JD mixes Hindi+English, handle it
4. **Bias check:** verify the rank doesn't just depend on college/location (ethical hiring — Redrob will love this)

---

## 📊 PHASE 5 — Testing, Numbers & Improvement

### Step 5.1 — Compute the full numbers
- NDCG@5, @10, @20
- MAP, MRR, Precision@k, Recall@k

### Step 5.2 — The final comparison table (this goes in the document)
| Method | NDCG@10 | MAP | MRR | P@10 |
|---|---|---|---|---|
| Keyword | ... | ... | ... | ... |
| Semantic | ... | ... | ... | ... |
| + Cross-encoder | ... | ... | ... | ... |
| **+ Learning-to-Rank (final)** | **best** | **best** | **best** | **best** |

> This table shows how much you improved step by step. Judges love it.

### Step 5.3 — Look at the mistakes (Error analysis)
- Where is the system wrong? Why did a wrong candidate appear at the top?
- Document 2-3 such mistakes + what you could improve
- This shows **maturity** → judges are impressed

### Step 5.4 — Tuning (adjust the settings)
- Try LightGBM's settings (num_leaves, learning_rate) to find the best
- Try top-50 or top-200 instead of top-100

---

## 📝 PHASE 6 — Submission Packaging (where marks are made)

### The 3 things to submit (official):
1. ✅ **GitHub repo** — full code
2. ✅ **Methodology doc / README** — the explanation
3. ✅ **Ranked output file** — in the correct format

### Step 6.1 — Put these sections in the README/Document:
1. Problem & approach (1 paragraph)
2. Architecture diagram (two-stage + ranking + reason)
3. Data understanding (key EDA findings)
4. Features (list + why)
5. Model: Learning-to-Rank (why this, how trained)
6. Explainability (show a sample output)
7. India-edge handling
8. Results: numbers + comparison table
9. Mistakes + limitations + what to improve next
10. How to run (install + commands — so a judge can run it themselves)

### Step 6.2 — Keep the repo clean (clarity = marks)
- Clean folders: `src/ data/ notebooks/ outputs/`
- `requirements.txt` (list of libraries)
- Comments in the code
- An architecture diagram in the README (from draw.io or mermaid)
- Modular code (separate files: matching, features, ranking, reason, testing)

### Step 6.3 — The output file (be careful)
- **Follow the EXACT format** that comes with the dataset (columns like job_id, candidate_id, rank)
- Check: the right number of candidates for each job, in the right order

### Step 6.4 — Bonus: a 2-minute demo video
- Optional, but a game-changer for Grand Champion
- A short video: input a JD → show the ranked list with reasons
- It gives the judges a "wow"

---

## 🔬 ADVANCED SECTION — Deep Technical Detail (this makes the top 1%)

> This section is for teams targeting Grand Champion (₹2L). The plan above makes you "good" — this makes you "the best."

## A. Feature Engineering — exactly how each feature is built

These are the exact features that go into the LightGBM ranker. For each JD-candidate pair:

| Feature | How to calculate | Why it matters |
|---|---|---|
| `semantic_sim` | cosine of embedding(JD) · embedding(candidate) | Meaning-level match |
| `cross_score` | cross-encoder(JD, candidate) | Deep contextual match |
| `skill_overlap` | matched skills / required skills (fuzzy) | Core skill fit |
| `skill_coverage_weighted` | weight important skills more | Not all skills are equal |
| `exp_gap` | candidate_exp − job_min_exp | Over/under-qualified |
| `seniority_match` | level diff (junior/mid/senior/lead) | Role-level fit |
| `title_sim` | embedding(current_title) · embedding(JD_title) | Role relevance |
| `recency_score` | 1 / (1 + last_active_days) | How active/available |
| `response_rate` | direct (0-1) | How engaged |
| `profile_completeness` | direct (0-1) | How serious |
| `application_intent` | applied to similar roles? (0/1) | Direct intent |
| `location_fit` | same city / remote-ok (0/1) | Practical fit |
| `hidden_gem_flag` | non-tier1 college + high skill match | Visibility angle |

> **Pro tip:** Keep feature names self-explanatory — so the SHAP output is also readable and looks clean in the README.

## B. Handling missing data (real datasets are messy)
- Skills empty → infer from headline/title (LLM or keyword)
- Experience NaN → median impute + an `exp_missing` flag feature
- Behavioral signals missing → 0 + a flag (the model learns it itself)
- **Never drop a row** — make a flag instead. Missing-ness is itself a signal.

## C. Validation strategy (avoiding data leakage)
- **GroupKFold by job_id** — a job's candidates should never be in both train and test
- 5-fold cross-validation → report the average NDCG (more reliable than one number)
- Check overfitting: compare train NDCG vs validation NDCG gap

## D. Cold-start problem (a new candidate, no history)
- If behavioral signals are absent → rely only on semantic + skill features
- Address this explicitly in the README — it shows the judge maturity

## E. Bias & fairness audit (Redrob will love this)
- Check: does the rank correlate with college-tier or location (when it shouldn't)?
- Make a "fairness slide/section": "We checked this, found this, fixed this"
- This directly hits Felix's "visibility problem" philosophy

## F. Performance/scale (if the dataset is big)
- A FAISS index for retrieval (a must for 10k+ candidates)
- Compute embeddings once and cache them (.npy file)
- Batch processing for the cross-encoder (no GPU → only rerank the top-50)

## G. README/methodology doc — the exact winning structure
```
# [Project Name] — Intelligent Candidate Discovery
## 1. TL;DR (3 lines: what you built, how, the result)
## 2. Problem Understanding (why keyword filters fail)
## 3. Data Insights (EDA — 4-5 key findings + 2 plots)
## 4. Architecture (diagram: retrieve → rerank → LTR → explain)
## 5. Feature Engineering (table + reasoning)
## 6. Model (LambdaMART — why, training, validation)
## 7. Explainability (sample output with reasons)
## 8. India-Edge (multilingual, hidden-gem, fairness)
## 9. Results (metrics table + ablation + improvement %)
## 10. Error Analysis (2-3 failure cases, honestly)
## 11. Limitations & Future Work
## 12. How to Run (pip install + commands, reproducible)
```

## H. The most common mistake that causes disqualification
1. **Wrong output format** — check the dataset's exact format (columns, order) three times
2. **Code doesn't run on the judge's system** — pinned requirements.txt, clear run steps
3. **Random train/test split** — do it job-wise, or you'll get inflated (fake) scores

## I. Time-boxing (if you run short on time — priority order)
1. Working retrieval + baseline (MUST — at least something submits)
2. LightGBM LambdaMART (the differentiator)
3. Explainability (a judging criterion)
4. README + output file (this is where marks are)
5. India-edge + demo (bonus, if time remains)

> **Rule:** First build one end-to-end "working" submission (small but complete), then improve. A complete simple system beats a half-finished perfect one.

---

## 🚀 THE WHOLE PATH IN SHORT
**Setup → practice on fake data → [dataset arrives] → understand data (EDA) → simple version → two-stage smart system → Learning-to-Rank → give reasons → India-edge → numbers + comparison → look at mistakes → document + repo → output file → submit (2 days early).**

> **The truth:** All of this finalizes once the dataset arrives. For now you can do Phase 0 (setup + practice). Give me the dataset — I'll prepare the exact code and features around it.
