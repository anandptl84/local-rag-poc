# Local RAG POC

Two FastAPI endpoints over a local vector store:

- **Ingestion** — accepts a local PDF path, chunks and embeds it, stores it in ChromaDB on disk.
- **Query** — takes a question, retrieves the top-k chunks, and asks Gemini for a grounded answer.

## Setting up from scratch (fresh Mac, nothing installed)

Follow these steps in order. You only do this once.

### Step 1: Create a GitHub account (skip if you have one)

1. Go to https://github.com/signup in your browser.
2. Enter your email address, create a password, and pick a username.
3. Complete the verification puzzle, then enter the launch code GitHub
   emails you.
4. You can skip the personalization questions — choose the **Free** plan.

### Step 2: Get added as a collaborator (needed to contribute)

Anyone can read this repo, but to push changes you need write access:

1. Send your GitHub username to the repo owner (**anandptl84**).
2. The owner adds you under **Settings → Collaborators → Add people** on the
   repo page.
3. You'll get an email invitation — open it and click **Accept invitation**.

### Step 3: Get a Gemini API key

The query API uses Google's Gemini to generate answers:

1. Go to https://aistudio.google.com/apikey and sign in with a Google account.
2. Click **Create API key** and copy it somewhere handy — the setup script
   asks for it in Step 4.

### Step 4: Run the setup script

1. Open **Terminal**: press `Cmd + Space`, type `Terminal`, press Enter.
2. Paste this command and press Enter:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/anandptl84/local-rag-poc/main/setup.sh | bash
   ```

3. Respond to the prompts as they come up:
   - **Mac login password** — needed once to install Homebrew.
   - **GitHub login** — a browser window opens; log in and approve. Pick
     **HTTPS** and **Login with a web browser** if asked.
   - **Gemini API key** — paste the key from Step 3 (or press Enter to skip
     and add it to `.env` later).

   The first run takes several minutes — it installs Homebrew, Python 3.12,
   and the GitHub CLI, clones this repo to `~/local-rag-poc`, creates the
   virtual environment, and installs all Python dependencies.

4. When you see `Uvicorn running on http://127.0.0.1:8000`, the server is up.

### Step 5: Verify it works

Open http://127.0.0.1:8000/docs in your browser — you should see the
interactive API documentation. The health check at
http://127.0.0.1:8000/health should return `{"status":"ok"}`.

Note: the first PDF you ingest downloads the embedding model (~90 MB), so it
takes a minute; after that it's fast.

## Day-to-day: starting and stopping the server

Stop the server with `Ctrl + C`. Start it again any time with:

```bash
cd ~/local-rag-poc
./venv/bin/uvicorn app.main:app --reload
```

Re-running the setup script also works — it skips everything that's already
installed and just starts the server.

## Contributing

`main` is protected — work on a branch and open a pull request:

```bash
cd ~/local-rag-poc
git checkout -b feature/my-change
# ...edit, commit...
git push -u origin feature/my-change
gh pr create
```

Every PR needs one approving review before it can merge.
