# PokeShop frontend

Vue 3, TypeScript, Pinia, Vue Router, Vue I18n and Reka UI. Use Node.js 22.12+ and **pnpm 10.10.0**, pinned in `package.json`.

See the [root README](../README.md) for Docker setup, database migration/import, routes, memory limits and verification results. The frontend needs the migrated and imported API. `/api` is proxied to `http://localhost:8000`; Docker sets `API_PROXY_TARGET=http://backend:8000`.

```sh
pnpm install --frozen-lockfile
pnpm dev
pnpm test:unit --run
pnpm type-check
pnpm exec eslint .
pnpm build-only
```

`pnpm build` runs type checking and bundling sequentially. Source folders separate PokÃ©mon, cart, shared preferences and UI translations. Catalog URL state is independent of the Pinia entity cache; cart storage contains only IDs and quantities.

## Browser tests

Start the development server and imported API first. Then:

```sh
pnpm exec playwright install --with-deps chromium
pnpm test:e2e
pnpm exec playwright show-report
```

Tests use one headless Chromium worker. Set `PLAYWRIGHT_BASE_URL` when the running frontend is not at `http://localhost:5173`. The suite covers interactions and four routes across five widths, two themes and two languages. Screenshots and traces are ignored under `test-results/`; the HTML report is also ignored. Other browser engines have not been verified.

The homepage uses an animated 2D Pikachu scene. The catalog uses CSS Grid by height, with draft filters in a Reka dialog; stats use a hover/focus/tap popover. Theme changes reveal over 700 ms (300 ms color fallback), while action notices expire after three seconds with hover/focus pause. Reduced motion disables decorative animation. No database credentials belong in Vite variables.
