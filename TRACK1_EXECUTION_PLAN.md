# 🥇 TRACK 1 — STEP-BY-STEP WINNING PLAN (Poora Detail)
## "Intelligent Candidate Discovery" · Coding Track · ₹10 Lakh

> **Yeh document kya hai?** Track 1 jeetne ka pura raasta — aaj se le ke final submission (28 June) tak. Har step simple bhasha mein, har technical shabd samjhaya hua.
>
> **Goal:** Grand Champion (₹2L) ya Elite Builder (₹5L) banna. Yeh track **skill se jeetta hai** — judge ki marzi se nahi.

---

## 📖 PEHLE — Zaroori shabd samajh lo (Glossary)

Yeh shabd baar-baar aayenge. Ek baar samajh lo, phir sab aasaan:

| Shabd | Simple matlab |
|---|---|
| **Candidate** | Naukri dhoondhne wala insaan (jiska resume hai) |
| **JD (Job Description)** | Naukri ka detail — kya skills/experience chahiye |
| **Ranking** | Candidates ko order mein lagana — best (#1) se kam-fit tak |
| **Keyword filter** | Sirf shabd match karna (purana, bewakoof tareeka) |
| **Semantic** | Shabd ka **matlab** samajhna (smart tareeka) |
| **Embedding** | Text ko numbers mein badalna taaki computer "matlab" compare kar sake |
| **Bi-encoder** | Tezi se mota-moti matching (pehla filter) |
| **Cross-encoder** | Dheere par gehra matching (final check) |
| **Learning-to-Rank** | AI ko sikhana ki accha ranking kaise banaye |
| **LambdaMART / LightGBM** | Ek popular tool jo ranking seekhta hai |
| **NDCG / MAP / MRR** | Numbers jo batate hain tumhari ranking kitni achhi hai |
| **Explainability** | Yeh batana ki system ne yeh decision **kyun** liya |
| **EDA** | Data ko ghoor ke samajhna (banane se pehle) |

---

## 🎯 JEETNE KA MANTRA (yeh dil se yaad rakho)

> 90% teams sirf ek simple cheez banayengi: "text match karo, similarity nikalo, rank kar do." Bas.
>
> **Tum 3 cheezein EXTRA karoge** jo tumhe winner banayegi:
> 1. **Do-step system** (pehle tez filter, phir gehra check)
> 2. **AI ko ranking sikhana** (Learning-to-Rank)
> 3. **Har rank ke saath WAJAH dena** (explainability)
>
> Yahi 3 cheezein medal dilayengi.

---

## 📅 POORA TIMELINE (aaj → 28 June)

| Phase | Kitne din | Kya karna |
|---|---|---|
| **Phase 0** | Abhi (dataset se pehle) | Setup + seekhna + practice |
| **Phase 1** | Dataset aate hi, 2-3 din | Data ko ghoor ke samajhna (EDA) |
| **Phase 2** | 4-5 din | Simple version banana (baseline) |
| **Phase 3** | 5-7 din | Asli smart system (do-step + Learning-to-Rank) |
| **Phase 4** | 3-4 din | Wajah dena (explainability) + India-edge |
| **Phase 5** | 3-4 din | Testing + numbers + improvement |
| **Phase 6** | 3 din | Document + repo + final file |
| **Buffer** | 2 din | Extra time (kuch toot gaya toh) |

---
---

## 🔧 PHASE 0 — Setup & Taiyaari (dataset aane se PEHLE shuru karo)

> Dataset ka intezaar mat karo. Yeh sab abhi ho sakta hai.

### Step 0.1 — Team mein kaam baant lo (max 4 log)
- **Person 1 (ML Lead):** main system (matching + ranking)
- **Person 2 (Data):** data saaf karna + features banana
- **Person 3 (Testing):** numbers nikalna + wajah likhna
- **Person 4 (Docs):** README + diagram + final packaging

> Akele ho? Koi baat nahi — yeh roles ko alag-alag dino mein khud kar lo.

### Step 0.2 — Tools install karo
- **Python** (version 3.10 ya upar)
- Yeh libraries: `pandas`, `numpy`, `scikit-learn`, `lightgbm`, `sentence-transformers`, `rapidfuzz`, `matplotlib`
- **GitHub** account + ek private repo banao
- Folders banao: `data/`, `src/` (code), `notebooks/` (experiments), `outputs/` (results)

### Step 0.3 — Concepts seekho (jo nahi aate)
YouTube/docs pe yeh 4 cheezein samajh lo (har ek 20-30 min):
1. **Sentence embeddings** — text ko numbers mein kaise badalte hain
2. **Bi-encoder vs cross-encoder** — tez filter vs gehra check
3. **Ranking metrics (NDCG)** — ranking ki quality kaise naapte hain
4. **LightGBM ranking** — ranking sikhane ka tool

### Step 0.4 — Practice: nakli data pe pura system chalao
Dataset aane se pehle, **khud ka chhota fake data** banao (50 candidates, 5 jobs — Excel mein bhi chalega). Us pe pura system ek baar end-to-end chalao.

**Fayda:** Jab asli dataset aayega, tum sirf file badloge aur sab chal jaayega — naya kuch nahi seekhna padega. Time bachega.

---

## 🔍 PHASE 1 — Data ko Samajhna (EDA) — SABSE IMPORTANT PHASE

> **Felix (Redrob CEO) ne bola:** *"Pehle dataset ke saath time bitao. Data ke signals tumhe architecture se zyada batayenge."*
> Iska matlab — turant code mat likho. Pehle data ko detective ki tarah ghoor ke samjho.

### Step 1.1 — Basic samajh
Apne aap se yeh sawaal pooch ke jawab dhoondho:
- Kitne candidates hain? Kitne jobs?
- Har candidate ke baare mein kya-kya info hai? (skills, experience, titles, company, education, location)
- **Behavioral signals kahan hain?** (yeh chhupe rehte hain — jaise last login, kitne apply kiye, reply rate, profile completeness). **👉 Yeh tumhara secret weapon hai — dhyaan se dhoondho.**
- **Labels (sahi jawab) diye hain?** Matlab kya already bataya hai ki kaunsa candidate kis job ke liye achha hai? (graded 0-3, ya sirf haan/na, ya kuch nahi)

### Step 1.2 — Data ki safai check karo
- Kahan info missing hai? (kisi ka skill khaali? experience nahi likha?)
- Skills kaise likhe hain — list mein? comma se? ya free text paragraph?
- Koi candidate do baar toh nahi (duplicate)?
- JD ka text saaf hai ya messy paragraph?

### Step 1.3 — Plots (graph) banao
Yeh graph banao taaki pattern dikhe:
- Experience ka distribution (kitne fresher, kitne senior)
- Sabse common skills kaunse
- Location spread (metro vs chhote sheher)
- Behavioral signals ka pattern + kya woh "achhe candidate" se jude hain?

### Step 1.4 — 3-4 important baatein likho
EDA se concrete observations nikalo jo aage kaam aayein. Jaise:
- "Jo log jaldi reply karte hain, woh aksar achhe fit hote hain"
- "30% candidates ke skills free-text mein hain → safai zaroori"
- "Jobs zyaadatar metro mein hain par candidates chhote sheher se bhi"

**📓 Output:** Ek notebook (`01_eda.ipynb`) with graphs + yeh baatein. Yeh baad mein document mein daaloge (clarity ke marks badhenge).

---

## 📏 PHASE 2 — Simple Version Pehle (Baseline)

> Pehle ek simple cheez banao jo "kaam karti hai." Phir use behtar karoge. Yeh "ek number" deta hai jisse comparison kar sako.

### Step 2.1 — Keyword version (sabse simple = "dushman" jise harana hai)
JD ke skills aur candidate ke skills ka **exact match** count karo → rank do. Yeh purana bewakoof tareeka hai. Iska NDCG@10 number note karo. **Tum ise beat karoge.**

### Step 2.2 — Semantic version (thoda smart)
- JD ka text aur candidate ka profile **embeddings** mein badlo (matlab numbers mein)
- Inki similarity nikalo → rank do
- Iska NDCG@10 note karo → keyword se behtar hona chahiye

### Step 2.3 — Comparison table shuru karo
| Tareeka | NDCG@10 | MAP | MRR |
|---|---|---|---|
| Keyword | ... | ... | ... |
| Semantic | ... | ... | ... |

> Yeh table aage badhte rahega. Document mein jaayega — judges ko **numbers mein improvement** dikhega.

---

## 🏗️ PHASE 3 — Asli Smart System (Yahin Jeet Hoti Hai)

### Step 3.1 — Pehla step: Tez filter (Retrieval)
- Embeddings se har job ke liye **top 100 candidates** tez se nikalo
- Yeh hazaaron candidates ko 100 tak laata hai (manageable)
- Bada data ho toh **FAISS** (ek fast search tool) use karo

### Step 3.2 — Doosra step: Features banana (har job-candidate jodi ke liye)
Yeh "features" banao (matlab har jodi ke baare mein numbers):
1. **Semantic score** — matlab kitna milta hai
2. **Cross-encoder score** — gehra match (optional par strong)
3. **Skill overlap** — kitne skills match (short forms samajh ke: JS=JavaScript)
4. **Experience fit** — candidate ka experience job ke hisaab se sahi hai?
5. **Seniority match** — junior/senior level match karta hai?
6. **Location fit** — same sheher? remote chalega?
7. **Behavioral signals** — reply rate, profile completeness, last active, applications
8. **Title similarity** — purane job titles JD se milte hain?

### Step 3.3 — Teesra step: AI ko ranking SIKHAO (THE DIFFERENTIATOR)
- **LightGBM** ka "lambdarank" mode use karo
- Yeh AI ko sikhata hai ki upar wale features ko **kaise mila ke** best ranking banaye
- Group = job_id (har job alag se rank hoti hai)
- Train/test alag karo **job ke hisaab se** (ek job dono mein na ho — warna cheating ho jaayegi, ise "data leakage" kehte hain)

> **Yeh kyun jeetta hai:** Simple similarity sirf text match karti hai. Yeh AI **seekhta hai** ki kaunse signals (behaviour + skills + matlab) mil ke "best fit" banate hain — exactly jo Redrob chahta hai.

### Step 3.4 — Agar "sahi jawab" (labels) NAHI diye toh? (Plan B)
Tension mat lo, do raaste:
- **Raasta 1:** Khud rules se pseudo-labels banao (role match + skill coverage + experience + activity ko mila ke score do), phir us pe AI train karo
- **Raasta 2:** Features ko logical weight de ke score banao (bina AI training ke)
- Document mein **saaf likho** ki labels nahi the isliye yeh approach — judges ko honesty + reasoning pasand aayega

---

## 💡 PHASE 4 — Wajah Dena (Explainability) + India-Edge

> Yeh phase judging criteria pe **direct hit** hai. Skip mat karna.

### Step 4.1 — Har candidate ke saath WAJAH (zaroori!)
Har ranked candidate ke saath ek aasaan-samajh wali wajah do:
```
Rank #1 — Candidate A (Score 91%)
  ✓ 7 mein se 6 zaroori skills hain
  ✗ Sirf Kubernetes missing
  ↑ Strong signals: 95% reply rate, 2 din pehle active, profile 100% complete
  ✓ Experience: 6 saal (job ko 5+ chahiye tha) — senior level match
```
- **SHAP** ya feature importance use karo "kyun" justify karne ke liye
- Yeh "explainability" criteria ko **literally** poora karta hai

### Step 4.2 — India-Edge features (Redrob ko impress karega)
1. **Skill short forms:** JS→JavaScript, ML→Machine Learning, k8s→Kubernetes
2. **Chhote college fairness:** unknown college ko kam mat aanko (neutral rakho)
3. **Hinglish samajh:** agar profile/JD mein Hindi+English mix hai, handle karo
4. **Bias check:** dekho ki rank sirf college/location pe toh depend nahi kar raha (ethical hiring — Redrob ko bahut pasand aayega)

---

## 📊 PHASE 5 — Testing, Numbers & Improvement

### Step 5.1 — Poore numbers nikalo
- NDCG@5, @10, @20
- MAP, MRR, Precision@k, Recall@k

### Step 5.2 — Final comparison table (yeh document mein jaayega)
| Tareeka | NDCG@10 | MAP | MRR | P@10 |
|---|---|---|---|---|
| Keyword | ... | ... | ... | ... |
| Semantic | ... | ... | ... | ... |
| + Cross-encoder | ... | ... | ... | ... |
| **+ Learning-to-Rank (final)** | **best** | **best** | **best** | **best** |

> Yeh table dikhata hai ki tumne kadam-dar-kadam kitna improve kiya. Judges ko bahut pasand aata hai.

### Step 5.3 — Galtiyan dekho (Error analysis)
- Kahan system galat ho raha? Top pe galat candidate kyun aaya?
- 2-3 aisi galtiyan document karo + kya improve kar sakte the
- Yeh **maturity** dikhata hai → judges impress

### Step 5.4 — Tuning (settings adjust karo)
- LightGBM ki settings (num_leaves, learning_rate) try karke best dhoondho
- Top-100 ki jagah top-50 ya top-200 try karo

---

## 📝 PHASE 6 — Submission Packaging (Yahan Marks Bante Hain)

### Submit karne ki 3 cheezein (official):
1. ✅ **GitHub repo** — poora code
2. ✅ **Methodology doc / README** — explanation
3. ✅ **Ranked output file** — sahi format mein

### Step 6.1 — README/Document mein yeh sections rakho:
1. Problem & approach (1 paragraph)
2. Architecture diagram (do-step + ranking + wajah)
3. Data understanding (EDA ki key baatein)
4. Features (list + kyun)
5. Model: Learning-to-Rank (kyun yeh, kaise train kiya)
6. Explainability (ek sample output dikhao)
7. India-edge handling
8. Results: numbers + comparison table
9. Galtiyan + limitations + aage kya improve hoga
10. Kaise chalayein (install + commands — taaki judge khud chala sake)

### Step 6.2 — Repo saaf rakho (clarity = marks)
- Clean folders: `src/ data/ notebooks/ outputs/`
- `requirements.txt` (libraries ki list)
- Code mein comments
- README mein ek architecture diagram (draw.io ya mermaid se)
- Code modular ho (alag files: matching, features, ranking, wajah, testing)

### Step 6.3 — Output file (DHYAAN SE)
- **EXACT format follow karo** jo dataset ke saath aayega (columns jaise job_id, candidate_id, rank)
- Check karo: har job ke liye sahi number of candidates, sahi order mein

### Step 6.4 — Bonus: 2-minute demo video
- Optional, par Grand Champion ke liye game-changer
- Ek chhota video: input JD daalo → ranked list with wajah dikhao
- Judges ko "wow" dega

---

## ✅ FINAL CHECKLIST (submit se pehle tick karo)
- [ ] Do-step system bana (tez filter + gehra check)
- [ ] Learning-to-Rank (LightGBM) train kiya
- [ ] Behavioral signals features mein daale (zyadatar teams yeh skip karti hain!)
- [ ] Har candidate ke saath wajah di
- [ ] Skill short forms + chhote college fairness
- [ ] NDCG/MAP/MRR numbers nikale
- [ ] Comparison table banaya (keyword → semantic → +LTR)
- [ ] Galtiyan wala section
- [ ] Saaf README + architecture diagram
- [ ] Output file sahi format mein
- [ ] Repo chal raha (install + run instructions)
- [ ] (Bonus) demo video

---

## ⚠️ YEH GALTIYAN MAT KARNA
1. **Sirf similarity pe rukna** — 90% teams yeh karengi. Tum Learning-to-Rank se aage niklo.
2. **Behavioral signals ignore karna** — yeh wahi "hidden gems" hain jo problem maang raha hai.
3. **Wajah (explainability) skip karna** — yeh ek poora judging criterion hai!
4. **Output format galat** — exactly follow karo, warna disqualify ka risk.
5. **README weak** — clarity = marks. Achha document = aasaan marks.
6. **Last minute submission** — 28 June deadline, 2 din pehle ready rakho.
7. **Data leakage** — train/test job ke hisaab se baanto, randomly nahi.

---

## 🚀 SHORT MEIN POORA RAASTA
**Setup → Fake data pe practice → [Dataset aaya] → Data samjho (EDA) → Simple version → Do-step smart system → Learning-to-Rank → Wajah do → India-edge → Numbers + comparison → Galtiyan dekho → Document + repo → Output file → Submit (2 din pehle).**

> **Sach:** Yeh sab tab final hoga jab dataset aayega. Abhi Phase 0 (setup + practice) kar sakte ho. Dataset mujhe do — main exact code aur features uske hisaab se ready kar dunga.


---
---

# 🔬 ADVANCED SECTION — Deep Technical Detail (yeh top 1% banata hai)

> Yeh section un teams ke liye hai jo Grand Champion (₹2L) target kar rahi hain. Upar wala plan "achha" banata hai — yeh "best" banata hai.

## A. Feature Engineering — har feature exactly kaise banega

Yeh woh exact features hain jo LightGBM ranker mein jaayenge. Har JD-candidate jodi ke liye:

| Feature | Kaise calculate karo | Kyun matter karta hai |
|---|---|---|
| `semantic_sim` | bge embedding(JD) · embedding(candidate) cosine | Matlab-level match |
| `cross_score` | cross-encoder(JD, candidate) | Deep contextual match |
| `skill_overlap` | matched skills / required skills (fuzzy) | Core skill fit |
| `skill_coverage_weighted` | important skills ko zyada weight | Sab skill barabar nahi |
| `exp_gap` | candidate_exp − job_min_exp | Over/under-qualified |
| `seniority_match` | level diff (junior/mid/senior/lead) | Role-level fit |
| `title_sim` | embedding(current_title) · embedding(JD_title) | Role relevance |
| `recency_score` | 1 / (1 + last_active_days) | Kitna active/available |
| `response_rate` | direct (0-1) | Kitna engaged |
| `profile_completeness` | direct (0-1) | Kitna serious |
| `application_intent` | applied to similar roles? (0/1) | Direct intent |
| `location_fit` | same city / remote-ok (0/1) | Practical fit |
| `hidden_gem_flag` | non-tier1 college + high skill match | Visibility angle |

> **Pro tip:** Feature names khud explainable rakho — taaki SHAP output bhi readable ho aur README mein clean dikhe.

## B. Handling missing data (real datasets gande hote hain)
- Skills khaali → headline/title se infer karo (LLM ya keyword)
- Experience NaN → median impute + ek `exp_missing` flag feature
- Behavioral signals missing → 0 + flag (model khud seekh lega)
- **Kabhi row drop mat karo** — flag banao. Missing-ness bhi ek signal hai.

## C. Validation strategy (data leakage se bachna)
- **GroupKFold by job_id** — ek job ke candidates kabhi train aur test dono mein na ho
- 5-fold cross-validation → average NDCG report karo (ek number se zyada bharosemand)
- Train pe overfit check: train NDCG vs val NDCG gap dekho

## D. Cold-start problem (naya candidate, no history)
- Behavioral signals na ho → sirf semantic + skill features pe rely karo
- README mein yeh explicitly address karo — judge ko maturity dikhegi

## E. Bias & fairness audit (Redrob ko bahut pasand aayega)
- Check: kya rank college-tier ya location se correlate kar raha hai (jab nahi karna chahiye)?
- Ek "fairness slide/section" banao: "Humne yeh check kiya, yeh paaya, yeh fix kiya"
- Yeh Felix ki "visibility problem" philosophy ko directly hit karta hai

## F. Performance/scale (agar dataset bada hai)
- FAISS index for retrieval (10k+ candidates ke liye must)
- Embeddings ek baar compute karke cache karo (.npy file)
- Batch processing for cross-encoder (GPU na ho toh top-50 hi rerank)

## G. README/methodology doc — exact winning structure
```
# [Project Name] — Intelligent Candidate Discovery

## 1. TL;DR (3 lines: kya banaya, kaise, result)
## 2. Problem Understanding (keyword filter kyun fail)
## 3. Data Insights (EDA — 4-5 key findings + 2 plots)
## 4. Architecture (diagram: retrieve → rerank → LTR → explain)
## 5. Feature Engineering (table + reasoning)
## 6. Model (LambdaMART — why, training, validation)
## 7. Explainability (sample output with reasons)
## 8. India-Edge (multilingual, hidden-gem, fairness)
## 9. Results (metrics table + ablation + improvement %)
## 10. Error Analysis (2-3 failure cases honestly)
## 11. Limitations & Future Work
## 12. How to Run (pip install + commands, reproducible)
```

## H. Sabse common galti jo disqualify karwati hai
1. **Output format galat** — dataset ke exact format (columns, order) ko 3 baar check karo
2. **Code chalta nahi judge ke system pe** — requirements.txt pinned, clear run steps
3. **Random train/test split** — job-wise karo warna inflated (fake) scores

## I. Time-boxing (agar time kam pad jaye — priority order)
1. Working retrieval + baseline (MUST — kuch toh submit ho)
2. LightGBM LambdaMART (differentiator)
3. Explainability (judging criterion)
4. README + output file (marks yahin)
5. India-edge + demo (bonus, agar time bache)

> **Rule:** Pehle ek end-to-end "kaam karta hua" submission banao (chhota par poora), phir improve karo. Aadha-adhura perfect system se ek poora simple system behtar hai.
