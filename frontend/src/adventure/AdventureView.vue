<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, toRaw, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { Award, LockKeyhole, Plus, X, ArrowRight, Flag, History } from 'lucide-vue-next'
import BattleSprite from './BattleSprite.vue'
import TrainerPortrait from './TrainerPortrait.vue'
import GymBackdrop from './GymBackdrop.vue'
import CenterReception from './CenterReception.vue'
import CollectionPc from './CollectionPc.vue'
import {
  type Battle,
  type BattleEvent,
  type Fighter,
  type Companion,
  useAdventureStore,
} from './store'

const { t, te, locale } = useI18n()
const game = useAdventureStore()
const openedGym = ref<number | null>(null)
function dismissGym(event: PointerEvent) {
  if (!(event.target instanceof Element) || !event.target.closest('.gym-stop'))
    openedGym.value = null
}
onMounted(() => document.addEventListener('pointerdown', dismissGym))
onUnmounted(() => document.removeEventListener('pointerdown', dismissGym))
function leaveGym(event: MouseEvent) {
  if (!(event.currentTarget as HTMLElement).contains(document.activeElement)) openedGym.value = null
}
function blurGym(event: FocusEvent) {
  if (!(event.currentTarget as HTMLElement).contains(event.relatedTarget as Node | null))
    openedGym.value = null
}
const saleDialog = ref<HTMLDialogElement>()
const pendingSale = ref<Companion | null>(null)
function cancelSale() {
  saleDialog.value?.close()
  pendingSale.value = null
}
let saleRequest = ''
async function askSale(member: Companion) {
  pendingSale.value = member
  saleRequest = crypto.randomUUID()
  await nextTick()
  saleDialog.value?.showModal()
}
async function confirmSale() {
  const result = await game.mutate('/sales', 'POST', {
    pokemon_id: pendingSale.value?.id,
    request_id: saleRequest,
  })
  if (result) {
    saleDialog.value?.close()
    pendingSale.value = null
  }
}
const mode = ref<'login' | 'register'>('login')
const username = ref(''),
  password = ref(''),
  invitation = ref('')
const tab = ref<'team' | 'gyms'>('team')
const route = useRoute()
watch(
  () => route.query,
  (query) => {
    if (query.mode === 'login' || query.mode === 'register') setMode(query.mode)
    if (query.tab === 'team' || query.tab === 'gyms') tab.value = query.tab
  },
  { immediate: true },
)
const draft = ref<number[]>([])
const saved = ref(false)
const arenaOpen = ref(false)
const entering = ref(false)
const revealing = ref(false)
const arenaHeading = ref<HTMLElement>()
const displayed = ref<Battle | null>(null)
const pcDialog = ref<HTMLDialogElement>()
const box = ref(0)
const boxCount = computed(() => Math.max(2, Math.ceil((game.trainer?.collection.length ?? 0) / 30)))
const boxSlots = computed(() =>
  Array.from({ length: 30 }, (_, i) => game.trainer?.collection[box.value * 30 + i] ?? null),
)
watch(boxCount, (count) => {
  box.value = Math.min(box.value, count - 1)
})
watch(
  () => route.fullPath,
  () => pcDialog.value?.close(),
)
watch(
  () => game.trainer?.username,
  () => {
    pcDialog.value?.close()
    box.value = 0
  },
)
const historyDialog = ref<HTMLDialogElement>()
const history = computed(() => (game.battle ?? displayed.value)?.history ?? [])
watch(
  () => game.battle?.id,
  () => historyDialog.value?.close(),
)
function eventActor(event: BattleEvent) {
  const side =
    event.kind === 'damage'
      ? event.side === 'player'
        ? 'opponent'
        : 'player'
      : (event.side ?? 'player')
  return side === 'player' ? t('adventure.you') : gym.value?.leader
}
const playing = ref(false)
const motion = ref('')
const leaving = ref(false)
const log = ref<BattleEvent[]>([])
let mounted = true
const name = (pokemon: { name: string; names: Record<string, string> }) =>
  pokemon.names[locale.value] || pokemon.name
const gym = computed(() => game.gyms.find((g) => g.id === displayed.value?.gym_id))
const player = computed(() => displayed.value?.player[displayed.value.player_active])
const opponent = computed(() => displayed.value?.opponent[displayed.value.opponent_active])
const dirty = computed(
  () => JSON.stringify(draft.value) !== JSON.stringify(game.trainer?.team ?? []),
)
const blocked = computed(() => game.busy || playing.value || entering.value)
const errorText = computed(() =>
  te(`adventure.errors.${game.error}`)
    ? t(`adventure.errors.${game.error}`)
    : t('adventure.errors.connectionError'),
)
const slots = computed(() =>
  Array.from({ length: 6 }, (_, i) =>
    game.trainer?.collection.find((p) => p.id === draft.value[i]),
  ),
)
const allPpGone = computed(() => player.value?.moves.every((m) => m.pp <= 0))

watch(
  () => game.trainer?.team,
  (team) => {
    draft.value = [...(team ?? [])]
  },
  { immediate: true },
)
watch(
  () => game.battle,
  (battle) => {
    if (!playing.value) {
      displayed.value = battle ? structuredClone(toRaw(battle)) : null
      log.value = battle?.events ?? []
    }
  },
)
onMounted(async () => {
  await game.load()
  displayed.value = game.battle ? structuredClone(toRaw(game.battle)) : null
  log.value = game.battle?.events ?? []
  arenaOpen.value = game.active
})
onUnmounted(() => {
  mounted = false
})

async function authenticate() {
  const result = await game.mutate(`/${mode.value}`, 'POST', {
    username: username.value,
    password: password.value,
    ...(mode.value === 'register' ? { invitation: invitation.value.trim() } : {}),
  })
  if (result) {
    password.value = ''
    invitation.value = ''
    tab.value = 'team'
    arenaOpen.value = game.active
  }
}

function toggle(id: number) {
  saved.value = false
  if (draft.value.includes(id)) draft.value = draft.value.filter((value) => value !== id)
  else if (draft.value.length < 6) draft.value.push(id)
}

function setMode(value: 'login' | 'register') {
  mode.value = value
  game.error = ''
}

function backToGyms() {
  arenaOpen.value = false
  tab.value = 'gyms'
}

function makeLead(id: number) {
  draft.value = [id, ...draft.value.filter((value) => value !== id)]
  saved.value = false
}

async function saveTeam() {
  saved.value = !!(await game.mutate('/team', 'PUT', { ids: draft.value }))
}

async function challenge(gymId: number) {
  if (blocked.value) return
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  entering.value = !reduced
  revealing.value = false
  const resultPromise = game.mutate<Battle>('/battles', 'POST', { gym_id: gymId })
  if (!reduced) await new Promise((resolve) => window.setTimeout(resolve, 600))
  const result = await resultPromise
  if (!mounted) return
  if (result) {
    displayed.value = game.battle ? structuredClone(toRaw(game.battle)) : result
    log.value = []
    arenaOpen.value = true
    leaving.value = false
    await nextTick()
    arenaHeading.value?.scrollIntoView({ block: 'start' })
  }
  revealing.value = true
  if (!reduced) await new Promise((resolve) => window.setTimeout(resolve, 450))
  entering.value = false
}

function eventText(event: BattleEvent) {
  const fighters = event.side
    ? (displayed.value?.[event.side] ?? [])
    : [...(displayed.value?.player ?? []), ...(displayed.value?.opponent ?? [])]
  const pokemon = fighters.find((p) => p.id === event.pokemon)
  const move = pokemon?.moves.find((m) => m.id === event.move)
  const pokemonName = pokemon ? name(pokemon) : ''
  if (event.kind === 'attack')
    return t('adventure.attackLine', {
      name: pokemonName,
      move:
        move?.names[locale.value] ??
        (event.move === 'struggle'
          ? locale.value === 'es'
            ? 'Forcejeo'
            : 'Struggle'
          : event.move),
    })
  if (event.kind === 'damage') {
    const effect =
      event.effectiveness === 0
        ? 'immune'
        : (event.effectiveness ?? 1) > 1
          ? 'superEffective'
          : (event.effectiveness ?? 1) < 1
            ? 'notEffective'
            : ''
    return `${t('adventure.damageLine', { name: pokemonName, amount: event.amount })}${effect ? ' ' + t(`adventure.${effect}`) : ''}`
  }
  const key = {
    miss: 'missLine',
    switch: 'switchLine',
    faint: 'faintLine',
    recoil: 'recoilLine',
    surrender: 'surrenderLine',
  }[event.kind]
  return t(`adventure.${key}`, { name: pokemonName })
}

async function play(action: {
  kind: 'move' | 'switch' | 'surrender'
  move?: string
  slot?: number
}) {
  if (!displayed.value || blocked.value) return
  playing.value = true
  leaving.value = false
  log.value = []
  const result = await game.mutate<Battle>(`/battles/${displayed.value.id}/turns`, 'POST', {
    revision: displayed.value.revision,
    ...action,
  })
  if (result && mounted) {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    for (const event of result.events) {
      if (!mounted) break
      log.value.push(event)
      motion.value =
        event.kind === 'attack'
          ? `${event.side}-attack`
          : event.kind === 'damage'
            ? `${event.side}-hit`
            : ''
      if (event.side && displayed.value) {
        const member = displayed.value[event.side].find((p) => p.id === event.pokemon)
        if (member && event.hp !== undefined) member.hp = event.hp
        if (event.kind === 'switch')
          displayed.value[`${event.side}_active`] = displayed.value[event.side].findIndex(
            (p) => p.id === event.pokemon,
          )
      }
      if (!reduced) await new Promise((resolve) => window.setTimeout(resolve, 300))
    }
  }
  if (mounted) {
    displayed.value = game.battle ? structuredClone(toRaw(game.battle)) : null
    if (!result) log.value = game.battle?.events ?? []
    motion.value = ''
    playing.value = false
  }
}

function health(pokemon: Fighter) {
  return t('adventure.health', { name: name(pokemon), hp: pokemon.hp, max: pokemon.max_hp })
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="arenaOpen && displayed"
      class="gym-world pokemon-palette"
      :data-type="gym?.type"
      aria-hidden="true"
    >
      <GymBackdrop :type="gym?.type" />
    </div>
    <div v-if="entering" class="battle-entry" :class="{ revealing }" aria-hidden="true">
      <div class="battle-entry-top" />
      <div class="battle-entry-bottom" />
    </div>
  </Teleport>
  <section
    class="adventure pokemon-palette"
    :data-type="arenaOpen && displayed ? gym?.type : undefined"
    :class="{ 'is-battling': arenaOpen && displayed }"
  >
    <header v-if="!arenaOpen || !displayed" class="adventure-heading">
      <h1>{{ t('adventure.title') }}</h1>
    </header>

    <div v-if="game.error" class="adventure-error" role="alert">
      <p>{{ errorText }}</p>
      <button class="text-button" :disabled="blocked" @click="game.load()">
        {{ t('adventure.retry') }}
      </button>
    </div>
    <p v-if="game.loading" class="state-box" role="status">{{ t('adventure.loading') }}</p>

    <div v-else-if="!game.trainer" class="trainer-access">
      <div class="trainer-pass">
        <div class="pass-stamp"><Award :size="40" /><span>KANTO</span></div>
        <h2>{{ t('adventure.privateAccess') }}</h2>
        <p>{{ t('adventure.accessText') }}</p>
        <div class="pass-companions" aria-hidden="true">
          <img
            v-for="id in [1, 4, 7]"
            :key="id"
            :src="`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`"
            alt=""
          />
        </div>
        <ol class="pass-badges" aria-label="Kanto">
          <li
            v-for="g in game.gyms"
            :key="g.id"
            :title="g.leader"
            class="pokemon-palette"
            :data-type="g.type"
          >
            <Award :size="24" /><span>{{ g.id }}</span>
          </li>
        </ol>
      </div>
      <form class="trainer-form" @submit.prevent="authenticate">
        <div class="adventure-tabs">
          <button type="button" :aria-pressed="mode === 'login'" @click="setMode('login')">
            {{ t('adventure.login') }}
          </button>
          <button type="button" :aria-pressed="mode === 'register'" @click="setMode('register')">
            {{ t('adventure.register') }}
          </button>
        </div>
        <label for="trainer-name">{{ t('adventure.username') }}</label>
        <input
          id="trainer-name"
          v-model="username"
          name="username"
          autocomplete="username"
          required
          minlength="3"
          maxlength="24"
          pattern="[a-zA-Z0-9_]+"
          autocapitalize="none"
          :spellcheck="false"
          aria-describedby="trainer-name-help"
        />
        <small id="trainer-name-help">{{ t('adventure.usernameHelp') }}</small>
        <label for="trainer-password">{{ t('adventure.password') }}</label>
        <input
          id="trainer-password"
          v-model="password"
          name="password"
          type="password"
          :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
          required
          minlength="10"
          maxlength="128"
          aria-describedby="trainer-password-help"
        />
        <small id="trainer-password-help">{{ t('adventure.passwordHelp') }}</small>
        <template v-if="mode === 'register'">
          <label for="trainer-invitation">{{ t('adventure.invitation') }}</label>
          <input
            id="trainer-invitation"
            v-model="invitation"
            name="invitation"
            autocomplete="off"
            required
            minlength="20"
            maxlength="128"
            autocapitalize="none"
            :spellcheck="false"
          />
        </template>
        <button class="button primary" :disabled="game.busy">
          {{ t(`adventure.${mode}`) }}<ArrowRight :size="18" />
        </button>
      </form>
    </div>

    <template v-else>
      <div v-if="!arenaOpen || !displayed" class="trainer-strip">
        <strong>{{ game.trainer.username }}</strong>
        <span
          ><Award :size="18" />{{
            t('adventure.medals', { count: game.trainer.medals.length })
          }}</span
        >
      </div>

      <template v-if="arenaOpen && displayed && player && opponent">
        <div ref="arenaHeading" class="gym-intro pokemon-palette" :data-type="gym?.type">
          <Award :size="28" />
          <div>
            <p>{{ gym?.names[locale] }}</p>
            <h1>{{ gym?.leader }}</h1>
          </div>
          <button
            class="turn-history-button"
            :disabled="blocked"
            :aria-label="t('adventure.viewHistory', { turn: displayed.turn })"
            aria-haspopup="dialog"
            @click="historyDialog?.showModal()"
          >
            <History :size="16" aria-hidden="true" />{{
              t('adventure.turn', { turn: displayed.turn })
            }}
          </button>
        </div>
        <div
          class="battle-arena pokemon-palette"
          :class="motion"
          :data-type="gym?.type"
          :aria-busy="blocked"
        >
          <GymBackdrop :type="gym?.type" />
          <div class="fighter-hud enemy-hud">
            <strong>{{ name(opponent) }}</strong
            ><span>{{ t('adventure.level', { level: opponent.level }) }}</span>
            <progress :value="opponent.hp" :max="opponent.max_hp" :aria-label="health(opponent)" />
            <small>{{ opponent.hp }} / {{ opponent.max_hp }}</small>
          </div>
          <div class="battle-platform enemy-platform" aria-hidden="true" />
          <BattleSprite
            class="battle-sprite enemy-sprite"
            :src="opponent.front"
            :name="name(opponent)"
          />
          <div class="battle-platform player-platform" aria-hidden="true" />
          <BattleSprite
            class="battle-sprite player-sprite"
            :src="player.back"
            :name="name(player)"
            :fallback="player.front"
          />
          <div class="fighter-hud player-hud">
            <strong>{{ name(player) }}</strong
            ><span>{{ t('adventure.level', { level: player.level }) }}</span>
            <progress :value="player.hp" :max="player.max_hp" :aria-label="health(player)" />
            <small>{{ player.hp }} / {{ player.max_hp }}</small>
          </div>
        </div>
        <div class="battle-console">
          <div
            class="battle-log"
            role="log"
            aria-live="polite"
            :aria-label="t('adventure.battleLog')"
          >
            <p v-for="(event, i) in log" :key="i">{{ eventText(event) }}</p>
            <p v-if="blocked" role="status">{{ t('adventure.processing') }}</p>
          </div>
          <template v-if="displayed.status === 'active'">
            <div class="battle-moves">
              <button
                v-for="move in player.moves"
                :key="move.id"
                class="pokemon-palette"
                :data-type="move.type"
                :disabled="blocked || move.pp <= 0"
                :aria-label="t('adventure.move', { name: move.names[locale] })"
                @click="play({ kind: 'move', move: move.id })"
              >
                <strong>{{ move.names[locale] }}</strong
                ><span>{{ t('adventure.power', { power: move.power }) }}</span
                ><small>{{ t('adventure.pp', { current: move.pp, max: move.max_pp }) }}</small>
              </button>
              <button
                v-if="allPpGone"
                :disabled="blocked"
                @click="play({ kind: 'move', move: 'struggle' })"
              >
                {{ locale === 'es' ? 'Forcejeo' : 'Struggle' }}
              </button>
            </div>
            <div class="battle-bench" :aria-label="t('adventure.yourTeam')">
              <button
                v-for="(member, slot) in displayed.player"
                :key="member.id"
                :disabled="blocked || member.hp <= 0 || slot === displayed.player_active"
                :aria-label="t('adventure.switch', { name: name(member) })"
                @click="play({ kind: 'switch', slot })"
              >
                <img :src="member.front" alt="" /><span>{{ name(member) }}</span
                ><small>{{ member.hp }} / {{ member.max_hp }}</small>
              </button>
            </div>
            <div v-if="leaving" class="leave-confirm">
              <strong>{{ t('adventure.confirmSurrender') }}</strong>
              <p>{{ t('adventure.surrenderHelp') }}</p>
              <button class="button secondary" @click="leaving = false">
                {{ t('adventure.cancel') }}
              </button>
              <button
                class="button primary"
                :disabled="blocked"
                @click="play({ kind: 'surrender' })"
              >
                {{ t('adventure.surrender') }}
              </button>
            </div>
            <button
              v-else
              class="text-button battle-leave"
              :disabled="blocked"
              @click="leaving = true"
            >
              <Flag :size="16" />{{ t('adventure.surrender') }}
            </button>
          </template>
          <div v-else class="battle-result" role="status">
            <Award v-if="displayed.status === 'won'" :size="36" />
            <h2>{{ t(`adventure.${displayed.status}`) }}</h2>
            <p v-if="displayed.status === 'won'">
              {{
                displayed.reward
                  ? t('adventure.reward', { amount: displayed.reward })
                  : t('adventure.noReward')
              }}
            </p>
            <p>{{ t('adventure.recovered') }}</p>
            <button class="button primary" :disabled="blocked" @click="backToGyms">
              {{ t('adventure.backToGyms') }}
            </button>
          </div>
        </div>
      </template>

      <template v-else>
        <button v-if="game.active" class="button primary resume-battle" @click="arenaOpen = true">
          {{ t('adventure.resume') }}
        </button>
        <nav class="adventure-tabs" :aria-label="t('adventure.nav')">
          <button
            v-for="item in ['team', 'gyms'] as const"
            :key="item"
            :aria-pressed="tab === item"
            @click="tab = item"
          >
            {{ t(`adventure.${item}Tab`) }}
          </button>
          <RouterLink to="/catalogo">{{ t('catalog') }}</RouterLink>
        </nav>

        <section v-if="tab === 'team'" class="adventure-panel pokemon-center">
          <div class="center-station">
            <header class="center-canopy">
              <span class="pokeball" aria-hidden="true"></span>
              <h2>{{ t('adventure.pokemonCenter') }}</h2>
            </header>
            <div class="center-body">
              <CenterReception :selected="draft.length">
                <button
                  class="pc-access"
                  :aria-label="t('adventure.openPc')"
                  :title="t('adventure.openPc')"
                  aria-haspopup="dialog"
                  @click="pcDialog?.showModal()"
                >
                  <CollectionPc />
                  <span class="pc-access-label" aria-hidden="true">{{
                    t('adventure.openPc')
                  }}</span>
                </button>
              </CenterReception>
              <p>{{ t('adventure.teamHelp') }}</p>
              <div class="team-slots">
                <div
                  v-for="(member, i) in slots"
                  :key="i"
                  class="team-slot"
                  :class="{ occupied: member }"
                >
                  <div class="slot-header">
                    <small>{{ t('adventure.slot', { number: i + 1 }) }}</small>
                    <button
                      v-if="member"
                      class="slot-remove"
                      :disabled="game.active || blocked"
                      :aria-label="t('adventure.removeFromTeam', { name: name(member) })"
                      @click="toggle(member.id)"
                    >
                      <X :size="16" />
                    </button>
                  </div>
                  <div class="slot-artwork">
                    <span class="slot-pokeball" aria-hidden="true"></span>
                    <img
                      v-if="member"
                      :src="`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${member.id}.png`"
                      :alt="name(member)"
                    />
                    <Plus v-else :size="26" aria-hidden="true" />
                  </div>
                  <template v-if="member">
                    <strong>{{ name(member) }}</strong>
                    <span v-if="i === 0" class="slot-lead">{{ t('adventure.lead') }}</span>
                    <button
                      v-if="i > 0"
                      class="lead-button"
                      :disabled="game.active || blocked"
                      :aria-label="t('adventure.leadAction', { name: name(member) })"
                      @click="makeLead(member.id)"
                    >
                      {{ t('adventure.lead') }}
                    </button>
                  </template>
                  <span v-else class="slot-empty-label">{{ t('adventure.emptySlot') }}</span>
                </div>
              </div>
              <div class="team-save">
                <button
                  class="button primary"
                  :disabled="!dirty || game.active || blocked"
                  @click="saveTeam"
                >
                  {{ t('adventure.saveTeam') }}</button
                ><span v-if="saved" role="status">{{ t('adventure.teamSaved') }}</span>
              </div>
            </div>
          </div>
        </section>

        <section v-if="tab === 'gyms'" class="adventure-panel">
          <h2>{{ t('adventure.gymsTitle') }}</h2>
          <p>{{ t('adventure.gymsHelp') }}</p>
          <p v-if="!game.trainer.team.length" class="team-note">{{ t('adventure.needsTeam') }}</p>
          <p v-else-if="dirty" class="team-note">{{ t('adventure.unsavedTeam') }}</p>
          <ol class="gym-route">
            <li
              v-for="g in game.gyms"
              :key="g.id"
              class="gym-stop pokemon-palette"
              :data-type="g.type"
              :class="{ 'gym-locked': g.id > game.trainer.medals.length + 1 }"
              @mouseenter="openedGym = g.id"
              @mouseleave="leaveGym"
              @focusin="openedGym = g.id"
              @focusout="blurGym"
              @keydown.esc.stop.prevent="openedGym = null"
            >
              <button
                class="gym-card-trigger"
                :aria-label="t('adventure.gymDetails', { name: g.leader })"
                :aria-expanded="openedGym === g.id"
                :aria-controls="`gym-actions-${g.id}`"
                @click="openedGym = g.id"
              >
                <div class="gym-medal">
                  <TrainerPortrait :gym-id="g.id" :leader="g.leader" />
                  <span class="gym-status"
                    ><Award v-if="game.trainer.medals.includes(g.id)" :size="14" /><LockKeyhole
                      v-else-if="g.id > game.trainer.medals.length + 1"
                      :size="14"
                    />{{ g.id }}</span
                  >
                </div>
                <span class="gym-info">
                  <strong>{{ g.leader }}</strong>
                  <small>{{ t(`types.${g.type}`, g.type) }}</small>
                </span>
              </button>
              <div
                v-if="openedGym === g.id"
                :id="`gym-actions-${g.id}`"
                class="gym-actions"
                role="group"
                :aria-label="g.leader"
              >
                <small>{{ g.names[locale] }}</small>
                <p>
                  {{ t('adventure.level', { level: g.level }) }} &middot;
                  {{ t('adventure.firstReward', { amount: g.reward }) }}
                </p>
                <span v-if="game.trainer.medals.includes(g.id)" class="earned-badge">{{
                  t('adventure.earned')
                }}</span>
                <button
                  class="button secondary"
                  :disabled="
                    blocked ||
                    game.active ||
                    dirty ||
                    !game.trainer.team.length ||
                    g.id > game.trainer.medals.length + 1
                  "
                  @click="challenge(g.id)"
                >
                  {{
                    g.id > game.trainer.medals.length + 1
                      ? t('adventure.locked')
                      : t(
                          game.trainer.medals.includes(g.id)
                            ? 'adventure.practice'
                            : 'adventure.challenge',
                          { name: g.leader },
                        )
                  }}
                </button>
              </div>
            </li>
          </ol>
        </section>
      </template>
    </template>
    <details class="adventure-rules">
      <summary>{{ t('adventure.rulesTitle') }}</summary>
      <p>{{ t('adventure.rules') }}</p>
    </details>
  </section>
  <dialog ref="historyDialog" class="sale-dialog history-dialog" aria-labelledby="history-title">
    <div class="history-heading">
      <h2 id="history-title">{{ t('adventure.historyTitle') }}</h2>
      <button
        class="history-close"
        :aria-label="t('adventure.closeHistory')"
        @click="historyDialog?.close()"
      >
        <X :size="20" aria-hidden="true" />
      </button>
    </div>
    <p v-if="!history.length">{{ t('adventure.emptyHistory') }}</p>
    <p v-else-if="history[0]!.turn > 1">{{ t('adventure.partialHistory') }}</p>
    <ol class="battle-history">
      <li v-for="turn in history" :key="turn.turn" class="history-turn">
        <h3>{{ t('adventure.turn', { turn: turn.turn }) }}</h3>
        <ol>
          <li v-for="(event, i) in turn.events" :key="i">
            <strong>{{ eventActor(event) }}</strong
            ><span>{{ eventText(event) }}</span>
          </li>
        </ol>
      </li>
    </ol>
  </dialog>
  <dialog ref="pcDialog" class="sale-dialog pc-dialog" aria-labelledby="pc-title">
    <template v-if="game.trainer">
      <div class="pc-screen">
        <header class="pc-screen-header">
          <h2 id="pc-title">{{ t('adventure.collectionTitle') }}</h2>
          <span>{{
            t('adventure.collectionCount', { count: game.trainer.collection.length })
          }}</span>
          <button
            class="history-close"
            :aria-label="t('adventure.closePc')"
            @click="pcDialog?.close()"
          >
            <X :size="20" aria-hidden="true" />
          </button>
        </header>
        <div class="pc-box-tabs" :aria-label="t('adventure.boxes')" role="group">
          <button v-for="i in boxCount" :key="i" :aria-pressed="box === i - 1" @click="box = i - 1">
            {{ t('adventure.box', { number: i }) }}
          </button>
        </div>
        <p v-if="!game.trainer.collection.length" class="team-note">
          {{ t('adventure.emptyCollection') }}
          <RouterLink to="/catalogo">{{ t('catalog') }}</RouterLink>
        </p>
        <div class="collection-picker pc-box-grid">
          <div
            v-for="(member, i) in boxSlots"
            :key="member?.id ?? `empty-${i}`"
            :class="member ? 'collection-member' : 'pc-empty-slot'"
          >
            <template v-if="member">
              <button
                :aria-pressed="draft.includes(member.id)"
                :aria-label="t('adventure.select', { name: name(member) })"
                :disabled="
                  game.active || blocked || (!draft.includes(member.id) && draft.length === 6)
                "
                @click="toggle(member.id)"
              >
                <img
                  :src="`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${member.id}.png`"
                  alt=""
                /><strong>{{ name(member) }}</strong>
              </button>
              <button
                class="collection-sell"
                :aria-label="t('adventure.sell', { name: name(member) })"
                :disabled="game.active || blocked"
                @click="askSale(member)"
              >
                {{ t('adventure.sellButton') }}
              </button>
            </template>
            <span v-else aria-hidden="true">{{ i + 1 }}</span>
          </div>
        </div>
        <p class="pc-selection-count">{{ t('adventure.selectedTeam', { count: draft.length }) }}</p>
        <p v-if="draft.length === 6" class="team-note">{{ t('adventure.teamFull') }}</p>
        <p class="team-note">{{ t('adventure.salePolicy') }}</p>
        <button class="button primary" @click="pcDialog?.close()">
          {{ t('adventure.backToTeam') }}
        </button>
      </div>
    </template>
  </dialog>
  <dialog
    ref="saleDialog"
    class="sale-dialog"
    aria-labelledby="sale-title"
    @cancel="pendingSale = null"
  >
    <template v-if="pendingSale">
      <h2 id="sale-title">{{ t('adventure.saleTitle') }}</h2>
      <p>
        {{
          t('adventure.saleHelp', { name: name(pendingSale), amount: pendingSale.sale_price ?? 0 })
        }}
      </p>
      <p v-if="game.error" role="alert">{{ errorText }}</p>
      <button class="button primary" :disabled="blocked" @click="confirmSale">
        {{ t('adventure.confirmSale') }}
      </button>
      <button class="button secondary" :disabled="blocked" @click="cancelSale">
        {{ t('adventure.cancelSale') }}
      </button>
    </template>
  </dialog>
</template>

<style src="./adventure.css"></style>
