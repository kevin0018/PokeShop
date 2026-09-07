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

`pnpm build` runs type checking and bundling sequentially. Source folders separate Pokémon, cart, shared preferences and UI translations. Catalog URL state is independent of the Pinia entity cache; cart entries contain only IDs and quantities; a separate versioned key stores recent product IDs for the header preview. Prices always come from the API.

## Browser tests

Start the development server and imported API first. Then:

```sh
pnpm exec playwright install --with-deps chromium
pnpm test:e2e
pnpm exec playwright show-report
```

Tests use one headless Chromium worker. Set `PLAYWRIGHT_BASE_URL` when the running frontend is not at `http://localhost:5173`. The suite covers interactions and four routes across five widths, two themes and two languages. Screenshots and traces are ignored under `test-results/`; the HTML report is also ignored. Other browser engines have not been verified.

The homepage is a full-width collage of the three Kanto starters and appears immediately, without an opening overlay. Catalog cards follow compact six-item editorial blocks, independent of biological height; partial blocks preserve order. The cart paginates six products while keeping global totals, with a Chansey receipt scene. Statistics live inside the detail illustration. The animated Espeon/Umbreon switch initially follows the browser preference and remembers manual selections; page transitions remain 700 ms. Three-second pie countdowns pause on hover/focus. Reduced motion skips decorative animation. No database credentials belong in Vite variables.

The header previews the three most recently added distinct products and the complete cart total on hover, keyboard focus, click or tap. “View full cart” opens the list; “Empty cart” clears the saved selection. Recent order persists without rearranging cart pages.

Type colors are shared across catalog cards, detail artwork, cart thumbnails and cart preview. The receipt takes a subtle tint from the most recently added product.

## Deployment status

**Live at [http://62.171.169.187](http://62.171.169.187)** on the Contabo VPS. Domain and HTTPS are pending. Production uses the standalone root `compose.production.yaml`; the default Compose remains for development. See the [deployment runbook](../docs/deployment.md) for routing, private configuration, data and release procedures.
