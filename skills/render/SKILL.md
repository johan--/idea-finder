---
name: render
description: >
  Rebuilds the Self-Map web app from discovery.md by running the render script.
  Use this skill whenever the user types /render, "render", "rebuild the map",
  "regenerate data.jsx", or "update the web app from discovery.md".
---

# Render

Run this command:

```bash
python3 ~/problem-finder/scripts/render.py
```

Report the output to the user. If it succeeds, tell them to refresh the browser at http://localhost:3737/Self-Map.html. If it fails, show the error.
