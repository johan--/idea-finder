---
name: render
description: >
  Rebuilds the Self-Map web app from discovery.md by running the render script.
  Use this skill whenever the user types /render, "render", "rebuild the map",
  "regenerate data.jsx", or "update the web app from discovery.md".
---

# Render

## Step 1 — Rebuild data.jsx

```bash
python3 ~/idea-finder/scripts/render.py
```

If this fails, show the error and stop.

## Step 2 — Ensure the server is running

Check if serve.py is already running on port 3737:

```bash
lsof -ti :3737
```

If nothing is returned, start it in the background:

```bash
python3 ~/idea-finder/scripts/serve.py &
```

Wait 1 second, then confirm it started by checking the port again.

## Step 3 — Report

Tell the user the build succeeded and open **http://localhost:3737/Self-Map.html**.
