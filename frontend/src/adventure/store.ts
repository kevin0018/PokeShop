import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export interface Companion {
  id: number
  name: string
  names: Record<string, string>
  types: string[]
  image_url: string
  price: number
  stats: Record<string, number>
}
export interface Move {
  id: string
  names: Record<string, string>
  type: string
  power: number
  accuracy: number
  pp: number
  max_pp: number
}
export interface Fighter {
  id: number
  name: string
  names: Record<string, string>
  types: string[]
  hp: number
  max_hp: number
  level: number
  front: string
  back: string
  moves: Move[]
}
export interface BattleEvent {
  kind: 'attack' | 'damage' | 'miss' | 'switch' | 'faint' | 'recoil' | 'surrender'
  side?: 'player' | 'opponent'
  pokemon?: number
  move?: string
  amount?: number
  hp?: number
  effectiveness?: number
}
export interface Battle {
  id: string
  gym_id: number
  revision: number
  status: 'active' | 'won' | 'lost' | 'surrendered'
  turn: number
  player: Fighter[]
  opponent: Fighter[]
  player_active: number
  opponent_active: number
  events: BattleEvent[]
  reward: number
}
export interface Gym {
  id: number
  leader: string
  names: Record<string, string>
  type: string
  level: number
  reward: number
}
export interface Trainer {
  username: string
  credits: number
  team: number[]
  collection: Companion[]
  medals: number[]
  csrf_token: string
  battle_id: string | null
}

class ApiError extends Error {
  constructor(
    public code: string,
    public status: number,
  ) {
    super(code)
  }
}

export const useAdventureStore = defineStore('adventure', () => {
  const trainer = ref<Trainer | null>(null)
  const shop = ref<Companion[]>([])
  const gyms = ref<Gym[]>([])
  const battle = ref<Battle | null>(null)
  const loading = ref(false)
  const busy = ref(false)
  const error = ref('')
  const active = computed(() => battle.value?.status === 'active')

  async function request<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
    let response: Response
    try {
      response = await fetch(`/api/v1/adventure${path}`, {
        method,
        credentials: 'same-origin',
        cache: 'no-store',
        headers: {
          ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
          ...(method !== 'GET' && trainer.value
            ? { 'X-CSRF-Token': trainer.value.csrf_token }
            : {}),
        },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: AbortSignal.timeout(15000),
      })
    } catch {
      throw new ApiError('connectionError', 0)
    }
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new ApiError(
        typeof data.detail === 'string' ? data.detail : 'requestInvalid',
        response.status,
      )
    }
    return response.json()
  }

  async function refresh() {
    try {
      trainer.value = await request<Trainer>('/me')
      battle.value = trainer.value.battle_id
        ? await request<Battle>(`/battles/${trainer.value.battle_id}`)
        : null
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        trainer.value = null
        battle.value = null
      } else throw cause
    }
  }

  async function load() {
    loading.value = true
    error.value = ''
    try {
      const [market, route] = await Promise.all([
        request<{ items: Companion[] }>('/shop'),
        request<{ items: Gym[] }>('/gyms'),
        refresh(),
      ])
      shop.value = market.items
      gyms.value = route.items
    } catch (cause) {
      error.value = cause instanceof ApiError ? cause.code : 'connectionError'
    } finally {
      loading.value = false
    }
  }

  async function mutate<T>(path: string, method: string, body?: unknown): Promise<T | null> {
    if (busy.value) return null
    busy.value = true
    error.value = ''
    try {
      const result = await request<T>(path, method, body)
      await refresh()
      return result
    } catch (cause) {
      let code = cause instanceof ApiError ? cause.code : 'connectionError'
      // A lost response can mean the operation committed. Reconcile before a retry.
      try {
        await refresh()
        if (code === 'connectionError' && trainer.value) code = 'connectionRecovered'
      } catch {
        /* Keep the actionable original error. */
      }
      error.value = code
      return null
    } finally {
      busy.value = false
    }
  }

  return { trainer, shop, gyms, battle, loading, busy, error, active, load, refresh, mutate }
})
