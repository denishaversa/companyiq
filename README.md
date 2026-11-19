# CompanyIQ

An AI business research assistant built with Streamlit and Google Gemini.
Type a company name (and, optionally, a team) to get a research report you
can read on screen or download as a PDF.

## Run it on your computer

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then paste your key into it
streamlit run app.py
```

You can also put `GEMINI_API_KEY=...` in a `.env` file instead. Both
`.env` and `.streamlit/secrets.toml` are ignored by git, so the key is never
committed.

## Deploy on Streamlit Community Cloud

1. Main file: `app.py`, branch: `main`, Python 3.12.
2. In the app's **Settings > Secrets**, add: `GEMINI_API_KEY = "your-key"`.

## Limits that protect the Gemini quota

Set in `config.py` (some can be changed with environment variables):

- Reports for the same company and team are reused for 6 hours.
- At most 30 new reports per hour for the whole app.
- Each visitor waits 20 seconds between reports, with up to 10 per visit.
- Each report may read at most 3 webpages and run 6 searches.
