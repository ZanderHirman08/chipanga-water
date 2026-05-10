# GitHub setup — tonight's walkthrough

End result: your project is backed up on GitHub, and the dashboard is live at a URL like `https://yourusername.github.io/chipanga-water/` that you can share with Charlie + Rotary.

**Total time: ~15 minutes** the first time. Updates after sync take ~30 seconds.

This guide assumes you don't already have git/GitHub experience. If you do, skip to the "TL;DR" at the bottom.

---

## Step 1 — GitHub account (skip if you have one)

1. Go to **[github.com](https://github.com)** → click **Sign up**.
2. Pick a username — this becomes part of your URL, so something memorable. Examples that'd work: `zanderhirman`, `zhirman`, `chipanga-project`.
3. Free plan, no credit card needed.

## Step 2 — Create the repository

1. Logged in, click the **+** in the top-right → **New repository**.
2. **Repository name**: `chipanga-water` (this becomes part of your URL — easy to remember is good)
3. **Description**: `Chipanga water + gardens project — interactive map and dashboard`
4. Set **Public** (private repos can't use free GitHub Pages)
5. Check ☑ **Add a README file** (we'll overwrite it, but Github likes you to have one to start)
6. Click **Create repository**

## Step 3 — Upload everything

Easiest method, no command line:

1. On your new repo's page, click **Add file** → **Upload files**
2. Open Finder, go to `/Users/zander/Documents/Claude/Projects/Tanzania Map/`
3. Select **everything except**:
   - `_archive_old_project/` (1MB of historical junk, skip it)
   - any `.DS_Store` files (macOS junk, the `.gitignore` will handle these going forward but you can skip them in the initial upload too)
4. Drag-and-drop into the GitHub upload area (or click "choose your files")
5. Wait for everything to upload (~2MB total, fast)
6. Scroll down. **Commit message**: `Initial commit — full project`
7. Click **Commit changes**

You'll see the file tree appear in your repo. Sanity check:
- `README.md` at root
- `docs/` folder containing `index.html` + `data/`
- `master/`, `scripts/`, `chipanga_qfield_pkg/`, etc.

## Step 4 — Enable GitHub Pages

1. In your repo, click **Settings** (right side of the repo nav bar)
2. Left sidebar: click **Pages**
3. Under **Source**, leave **Deploy from a branch**
4. Under **Branch**, pick:
   - Branch: **main**
   - Folder: **/docs** ← important! (not `/ (root)`)
5. Click **Save**
6. Wait ~30–60 seconds. **Refresh the page**.

You should see a green box: **"Your site is live at `https://yourusername.github.io/chipanga-water/`"**

Click that URL. You should see Chipanga's dashboard load with Charlie's KML drafts on the satellite map.

## Step 5 — Share

Send the URL to:
- **Charlie**: WhatsApp, "here's the dashboard so far — let me know if anything looks wrong about the layout before you go back"
- **Rotary**: email to club presidents (community + international + Longmont). One-line context: "Project tracking dashboard — drafts now, real survey data lands next week."

---

## Updating after Charlie syncs new data

When Charlie sends his real `.gpkg` next week:

1. **On your machine:**
   ```bash
   cd "/Users/zander/Documents/Claude/Projects/Tanzania Map"
   python3 scripts/sync_charlie.py /path/to/charlies_real.gpkg
   ```
   This regenerates `docs/index.html` + `docs/data/*.geojson` automatically.

2. **On GitHub:**
   - Go to your repo → click into the **`docs`** folder
   - Click **Add file → Upload files**
   - Drag in the updated `index.html` AND drag the entire updated `data/` folder
   - Commit message: `Sync Charlie's data — [date]`
   - Click **Commit changes**

3. **GitHub Pages auto-rebuilds** in ~30–60 seconds. URL stays the same; data updates.

---

## Troubleshooting

**"Your site is live" but the URL shows a 404.**
Wait 1–2 minutes — the first deploy can take longer. Refresh.

**Site loads but the map is blank.**
Open browser DevTools (F12) → Console tab. Look for errors. Most likely cause: `data/` folder didn't upload. Visit `https://yourusername.github.io/chipanga-water/data/garden_plots.geojson` directly — should display JSON. If it 404s, re-upload the `data/` folder inside `docs/`.

**Updated files but the site shows old data.**
Browser caching. Hard-refresh: **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows). If still stale after 5 min, check the **Actions** tab on your repo for the latest deploy status.

**I want to keep some files private (e.g., raw photos of the village).**
Don't upload them to a public repo. Put them in a folder like `_private/` and the `.gitignore` already has `_archive_old_project/` excluded as a pattern you can copy. Or use a private repo (free) for the source files + a separate public repo just for the `docs/` contents.

---

## TL;DR (if you've used git before)

```bash
cd "/Users/zander/Documents/Claude/Projects/Tanzania Map"
git init
git add .
git commit -m "Initial commit"
git branch -M main
gh repo create chipanga-water --public --source=. --push
gh repo edit --enable-pages --pages-branch main --pages-path /docs
```

Then visit your repo → Settings → Pages to confirm. Done.

---

## What's already prepped

I've already taken care of:
- **`.gitignore`** at the repo root — excludes macOS junk, Excel lock files, QGIS backups, Python cache, and `master/backups/` (those auto-regenerate from sync)
- **Renamed `web_map/` → `docs/`** so GitHub Pages "Deploy from /docs" works without restructuring
- **Updated all scripts** (`build_web_map.py`, `sync_charlie.py`) to write to the new `docs/` path
- **Updated docs** (`README.md`, `PROJECT_RECAP.md`, etc.) reference `docs/` not `web_map/`

So all you have to do tonight is upload + click "Save" on the Pages settings.
