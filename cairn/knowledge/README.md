# Cairn knowledge articles

Plain-language articles distilled from the AWSNA 2026 booth handouts
(`sagerock/tradeshows/awsna-2026/`), written to feed Cairn's RAG knowledge base
(the Qdrant `sagerock` collection). Each file answers real questions a sagerock.com
visitor might ask, in SageRock's voice (warm, direct, no em-dashes).

| File | Covers |
|---|---|
| `about-sagerock.md` | Who SageRock is, since 1999, Build/Run/Teach, additive-not-replacement |
| `how-we-work-with-schools.md` | The four-step engagement: Explore, Analyze, Implement, Support |
| `enrollment-audit.md` | The $2,500 Enrollment Audit + Wire-Up: what we examine, produce, deliver |
| `pricing-and-plans.md` | Free call, $2,500 audit, plans from $100/mo, Managed from $250/mo |
| `ai-assistants-overview.md` | "Many sources in, one assistant out"; the read-only/draft trust model |
| `case-study-spring-garden-waldorf.md` | Linden, K-8 Waldorf, 8 sources |
| `case-study-center-for-anthroposophy.md` | Iris, teacher education, 8 sources |
| `case-study-b2b-manufacturer.md` | Athena, anonymized national manufacturer, weekly Monday email |
| `meet-rocky-lewis.md` | Rocky's bio, Waldorf admissions experience, contact |

## Ingestion

The current `seed_qdrant.py` ingests **public URLs** from `knowledge_pages.yaml`, not
local files. To get these articles into the `sagerock` collection, either:

1. **Publish as web resources** (e.g. pages/posts on sagerock.com), add the URLs to
   `knowledge_pages.yaml`, and re-run `seed_qdrant.py`. Bonus: they become real,
   SEO-friendly web content too. Best long-term fit with the existing pipeline.
2. **Seed the local files directly** via a small local-file ingestion path (companion
   to `seed_qdrant.py`). KB-only, no public footprint, fastest.

Either way, `seed_qdrant.py` CLEARS and re-seeds the whole collection, so the existing
3 site URLs must stay in the mix on the same run.

## Notes / things to confirm before seeding production

- **Conference Special is intentionally NOT in these articles.** It is time-bound to
  AWSNA (June 22-26, 2026); baking it into the permanent KB would make Cairn offer an
  expired deal. Add a separate, dated entry if you want it live during the show only.
- **Pricing tiers** (Report and Ask vs Managed) are described loosely; confirm exact
  numbers before Cairn quotes them.
- **Client names:** the case studies name Spring Garden Waldorf and the Center for
  Anthroposophy (both appear on the public handouts). The manufacturer stays anonymous.
  Confirm you're comfortable with the public bot citing the two named clients.
