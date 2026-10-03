# Trainer adventure

[English](adventure.md) · [Español](adventure.es.md)

The adventure is a private, single-player Kanto challenge alongside the public catalog and demonstration cart. Trainers receive 1,000 fictional credits once, buy Pokémon for their permanent collection, select an ordered team of up to six, and challenge six gyms. The first team member leads each battle. Pokémon recover and PP reset when a new battle starts. Defeat or surrender costs no credits.

[![Actual local battle interface](adventure.png)](adventure.png)

[Mobile interface](adventure-mobile.png) · [Catalog purchases](catalog-trainer.png). Captured from the local preview.

[Gym leaders](gyms.png) · [Gyms on mobile](gyms-mobile.png). Each gym uses its type palette and a classic trainer PNG from [Pokémon Showdown's trainer sprites](https://play.pokemonshowdown.com/sprites/trainers/). Trainer artwork belongs to its respective rights holders. A portrait failure leaves the leader name and gym controls available.

[Pokémon Center](center.png) · [Collection PC](collection-pc.png)

## Access and deployment

Apply the additive migration before opening the adventure:

```sh
docker compose exec backend alembic upgrade head
docker compose exec backend python -m src.adventure.invitations --hours 72
docker compose exec backend python -m src.adventure.invitations --revoke CODE
```

For production, use `docker compose -f compose.production.yaml ...`. Give the printed code directly to the visitor; do not publish it in the portfolio or commit it. Only the SHA-256 digest is stored. Codes expire, are single-use, and can be revoked before redemption. Issuance is available only through the owner CLI. Revoking an invitation does not disable an already registered account.

Set `ALLOWED_ORIGINS` to the exact public frontend origin(s), including the HTTPS scheme, in production. `ENVIRONMENT=production` enables Secure cookies. Sessions last seven days, are stored as digests, and use HttpOnly/SameSite=Strict cookies scoped to the adventure API. Authenticated writes also require the session-derived CSRF token returned by `/me`. Passwords use salted scrypt. Login and registration share persistent limits of 20 attempts per 15 minutes by network peer and username. Behind the existing frontend proxy the peer bucket is shared; forwarded client headers are deliberately not trusted. Password reset and email verification are outside this invitation-only version.

## Rules and economy

Gyms use square cards in three desktop columns or two mobile columns. Hover, keyboard focus or tapping a card opens its details and challenge action; Escape or clicking outside closes the panel. Collection sale buttons show only “Sell”; the exact refund appears in the confirmation dialog.

- Purchases reuse `/catalogo`, its existing cards, search, filters, pagination and detail views. Signed-in trainers see server-priced credits and add Pokémon to the existing cart and confirm the whole purchase there. The catalog initially filters to the 26 Kanto Pokémon currently supported in battle; turning off the playable filter shows the full catalog and marks unsupported Pokémon. Price ordering uses credit prices. The anonymous demonstration keeps its euro cart. There is one copy of each species per trainer, no trading, evolution or real payments.
- Credit price is `100 + 2 × max(0, sum(base stats) − 250)`, rounded to the nearest ten, with a minimum of 100. This is independent of the catalog's euro demonstration prices and shared fictional stock. It is an initial balancing policy, not a competitive valuation.
- Trainer Pokémon use level 50. Gym levels are 28, 34, 38, 42, 46 and 50. Teams and four-move loadouts are defined in `backend/src/adventure/content.py`.
- Implemented: physical/special damage, STAB, modern type effectiveness (including dual types/immunity), speed, move priority, accuracy, PP, switching and Struggle with recoil. Equal speed/priority uses a server-side random tie-break. Opponents choose the move with the greatest estimated damage adjusted for accuracy.
- This is a simplified ruleset: passive abilities, critical hits, statuses, stat stages, items, IVs/EVs, secondary move effects and exact historical generation rules are not implemented. Low Kick has fixed power 50; draining moves do not heal and Swift follows the simplified accuracy system. The UI explains these limits before play.
- Fainted Pokémon are replaced by the next healthy member in team order. Switching voluntarily spends the turn. All-PP exhaustion permits Struggle. A simultaneous wipe is a trainer loss.
- Gyms unlock sequentially. First victories grant a medal and 150/200/250/300/350/400 credits respectively. Rematches are free practice and grant no additional credits. The unique medal constraint prevents repeated reward claims.

Selling from the collection requires confirmation and returns half the original paid price, rounded down. The server removes the Pokémon from both collection and saved team. Sales are blocked during active battles. Checkout validates every cart line and available credits in one transaction; any failure rolls back all lines. Migration `004` adds durable, trainer-scoped receipts for checkout and sales. Retrying the same request after a lost response returns the original receipt without charging or refunding again. Draft carts persist per trainer in browser storage; they do not grant ownership.

Battle entry uses two consecutive black wipes and skips them with reduced motion. During battle the header, footer, cart notices and rules are hidden, leaving the gym, fighters, turn history and battle controls in focus. Gym-specific scenery covers the viewport as well as the arena. Reloads retain this focused view; returning to the gyms restores navigation.

## Authority and recovery

The Pokémon Center contains a clickable pixel-art PC. It opens the collection in a modal with 30-slot boxes, team selection and confirmed sales. Boxes display the collection in groups of 30; closing the PC keeps the draft team, which is persisted with Save team.

The API accepts only intents. It loads prices, balances, ownership, moves and opponent decisions itself. Trainer row locks serialize purchases, team updates and battles. Each battle holds a server-side snapshot and revision; stale/replayed turns return 409. One active battle per trainer is enforced by a partial unique index. Ownership is checked on every battle read/write. Battles persist across reloads and login; animation does not control outcomes or rewards.

The browser renders ordered server events and the final authoritative state. If a response is lost, refresh the trainer/battle before retrying. The old demonstration cart does not grant ownership and is never submitted as an adventure purchase.

## Verification

The turn indicator opens a battle history grouped by resolved turn, with the player or gym leader identified for each action. The server stores this history in the battle snapshot, so reloads preserve it and rejected duplicate turns do not add entries. Existing snapshots can recover their last stored turn; earlier overwritten events cannot be reconstructed.

Verified locally on 2026-10-03: 25 adventure tests, 22 existing backend regression tests, 19 frontend unit tests passed. The 33-test catalog/cart Chrome suite passed during the redesign, and targeted checks plus the complete adventure journey were repeated after the latest UI changes. Type checking, ESLint, production build and Ruff passed. Browser coverage includes registration, purchases, team persistence, battle reload, language changes, 320/375/414/768/1280 px layouts, first victory and unlocking, logout/login, and a committed attack whose response is deliberately lost and recovered without replay. A seeded test using imported Kanto base stats verifies an affordable route through all six gyms; this demonstrates feasibility, not comprehensive game balance.

Run API tests against a separately created, migrated database whose name starts with `adventure_test`. The suite truncates adventure tables and writes biological fixtures there; never point it at a real catalog database.

```sh
# Configure POSTGRES_DB=adventure_test_<suffix> in the test process only.
python -m unittest tests.test_adventure -v
```

The browser integration test also requires a disposable database and a new invitation:

```sh
PLAYWRIGHT_BASE_URL=http://localhost:5173 PLAYWRIGHT_ADVENTURE_CODE='<single-use-code>' pnpm --dir frontend test:e2e
```

Without that environment variable, the adventure registration test is skipped. Set `PLAYWRIGHT_CHANNEL=chrome` to use installed Chrome instead of Playwright Chromium. Keep invitation values and Playwright traces out of Git.

The suite verifies actual PostgreSQL transactions, single-use invitation redemption, hashing, authentication, CSRF/origin checks, concurrent purchases, server-calculated prices, team ownership, battle recovery/revisions and one-time rewards. Sprite assets come from [PokeAPI/sprites](https://github.com/PokeAPI/sprites); characters and names belong to their respective owners. This remains a noncommercial portfolio demonstration.
