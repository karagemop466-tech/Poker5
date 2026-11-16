# One Entry Vegas

A small, source-linked Las Vegas poker research dashboard focused on **single-entry-overall** tournament terms. Confirmed re-entry/rebuy events and entry-cap-unknown events are intentionally shown in separate categories. The current research snapshot verifies **zero** upcoming events as single-entry overall.

The static site also includes room-specific hotel details, clearly labeled illustrative booking snapshots, the official room-tax note, and rough third-party walking estimates. No trip dates were provided; the sample stay is not a personalized quote or recommendation. Hotels are compared by disclosed room and source facts, not ranked overall.

## Run locally

Requires Node.js 20 or newer; no packages need installing.

```sh
npm run check
npm run dev
```

Then open `http://localhost:4173`. To preview the exact static build output:

```sh
npm run build
npm run preview
```

The build copies the site into the ignored `dist/` directory. GitHub Pages currently serves the same static source files from the repository root, so no client-side API key or backend is required.

## Research & maintenance

- The source review date is shown on the site and stored in `data.mjs`.
- `data.mjs` is the single source of truth for event, hotel, tax, and walking-route facts.
- Each event card and the [source ledger](./sources.html) links to the materials used.
- If official sources conflict, the disagreement is displayed instead of silently resolved.
- Update rules only after checking the current event-specific terms. Never infer a freezeout from silence, a one-day label, or one-entry-per-flight language.
- Run `npm run check` after any data or interface change.

This project is independent research and is not affiliated with any poker room, hotel, or tournament operator. Verify all current terms, schedules, and prices directly before making plans.
