# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Activate virtualenv first (always required)
source .venv/bin/activate

# Run dev server
python manage.py runserver --settings=portfolio.settings.development

# Apply migrations
python manage.py migrate

# Dump local data to fixture (source of truth for Render)
python manage.py dumpdata projects.project projects.projectfile core.skill --indent 2 > projects/fixtures/initial_projects.json

# Rebuild the FAISS RAG index after editing knowledge base files
python manage.py build_rag_index

# Create superuser locally
python manage.py createsuperuser

# Load the fixture into local DB
python manage.py loaddata initial_projects
```

The `DJANGO_SETTINGS_MODULE` must be `portfolio.settings.development` locally; production uses `portfolio.settings.production`. Set it in `.env` or pass `--settings=` explicitly.

## Architecture

### Django Apps

- **`core`** — Static pages (home, about, skills, resume, contact), the `Skill` model, and the `ContactForm`. Views are all `TemplateView`/`FormView` subclasses.
- **`projects`** — `Project` and `ProjectFile` models. Projects have `tools_used` and `key_features` as `JSONField`s. `ProjectAdmin` uses a custom form (`ProjectAdminForm`) that accepts either valid JSON arrays or bare comma-separated strings in those fields. Project images are served as **static files** (not media) — images live in `core/static/img/projects/` and are referenced via `project.static_image_name` property in templates, not `project.image.url`.
- **`chatbot`** — RAG-powered Q&A chatbot. See RAG Pipeline section below.

### Settings Split

`portfolio/settings/` has three files:
- `base.py` — shared config, loads `.env` via `python-dotenv`
- `development.py` — SQLite, `DEBUG=True`, console email backend
- `production.py` — `dj-database-url` (PostgreSQL), WhiteNoise compressed static storage, HSTS/SSL

### Static vs. Media Files

- **Static** (committed to git, served by WhiteNoise): headshot (`core/static/img/MarcoHeadshot.jpg`), resume PDF (`core/static/img/Marco_Dilaudo_2026.pdf`), all project images (`core/static/img/projects/`)
- **Media** (user-uploaded at runtime): `ProjectFile` attachments go to Cloudinary in production when `CLOUDINARY_URL` is set; falls back to local disk in dev. Cloudinary is activated in `base.py` only when `CLOUDINARY_URL` env var is present.

### RAG Pipeline (`chatbot/rag/`)

Three modules with module-level caches so the index and chain are built once per process:

1. **`loader.py`** — Reads all `.md` files from `chatbot/knowledge_base/`, splits into 500-token chunks with 50-token overlap using `RecursiveCharacterTextSplitter`.
2. **`embeddings.py`** — Embeds chunks using `GoogleGenerativeAIEmbeddings(model='models/gemini-embedding-001')` and persists the FAISS index to `chatbot/rag/faiss_index/` (gitignored). `load_index()` builds from scratch if the directory is missing.
3. **`chain.py`** — LCEL chain: retriever → format docs → `ChatPromptTemplate` → `ChatGoogleGenerativeAI(model='gemini-2.5-flash')` → `StrOutputParser`. The `ask(question)` function is the only external entry point.

All Google AI calls use the `GEMINI_KEY` env var.

**Updating chatbot knowledge:** Edit files in `chatbot/knowledge_base/`, then run `python manage.py build_rag_index`. The index is rebuilt on every Render deploy automatically via `build.sh`.

### Data Sync Workflow (Local → Render)

Render's free tier has no persistent disk. The fixture is the source of truth:

1. Edit data locally via Django admin (`/admin`)
2. `python manage.py dumpdata projects.project projects.projectfile core.skill --indent 2 > projects/fixtures/initial_projects.json`
3. Commit and push — Render's `build.sh` runs `seed_initial_projects` which calls `loaddata initial_projects` (upsert) on every deploy

### Render Deployment (`build.sh`)

```
pip install → collectstatic → migrate → seed_initial_projects → build_rag_index → create_superuser_env
```

`create_superuser_env` reads `DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD` env vars. Render has no shell access on the free tier, so this is the only way to create a superuser.

### Required Environment Variables

| Variable | Where set |
|---|---|
| `SECRET_KEY` | `.env` / Render env |
| `GEMINI_KEY` | `.env` / Render env |
| `DJANGO_SETTINGS_MODULE` | `.env` / Render env |
| `DATABASE_URL` | Render (injected from linked PostgreSQL) |
| `RENDER_EXTERNAL_HOSTNAME` | Render (injected automatically) |
| `CLOUDINARY_URL` | Render env (optional; enables Cloudinary media) |
| `DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD` | Render env (for `create_superuser_env`) |
