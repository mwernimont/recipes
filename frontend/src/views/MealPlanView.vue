<template>
  <div v-if="store.loading" class="state-msg">Loading…</div>
  <div v-else-if="store.error" class="state-msg error">{{ store.error }}</div>

  <div v-else-if="stage === 'count'" class="count-picker">
    <h1>How many meals are we planning?</h1>
    <div class="count-options">
      <button v-for="n in 7" :key="n" class="count-btn" @click="selectMealCount(n)">{{ n }}</button>
    </div>
  </div>

  <div v-else class="meal-plan">
    <div class="plan-header">
      <button class="back-btn" @click="startOver">← Start over</button>
      <h1>Plan {{ mealCount }} meal{{ mealCount > 1 ? 's' : '' }}</h1>
      <span class="progress">{{ accepted.length }} / {{ mealCount }} planned</span>
    </div>

    <section class="accepted-section">
      <p v-if="accepted.length === 0" class="empty-note">No meals accepted yet.</p>
      <div v-else class="accepted-grid">
        <MealPlanCard
          v-for="r in accepted"
          :key="r.id"
          :recipe="r"
          variant="accepted"
          @remove="removeAccepted"
        />
      </div>
    </section>

    <div v-if="isPlanComplete" class="ready-state">
      <p>✅ Your plan is ready!</p>
    </div>

    <template v-else>
      <section class="search-section">
        <input
          v-model="searchInput"
          type="search"
          placeholder="Search recipes by title…"
          class="search-input"
        />
        <ul v-if="searchResults.length" class="search-results">
          <li v-for="r in searchResults" :key="r.id">
            <span>{{ r.title }}</span>
            <button class="add-btn" @click="acceptRecipe(r)">+ Add</button>
          </li>
        </ul>
        <p v-else-if="searchInput.trim()" class="empty-note">No matching recipes.</p>
      </section>

      <section class="suggestions-section">
        <button class="help-btn" @click="generateSuggestions">
          {{ hasGeneratedOnce ? 'Show me more recipes' : 'Help me plan' }}
        </button>

        <p v-if="hasGeneratedOnce && suggestions.length === 0" class="empty-note">
          No eligible recipes right now — try again later or add more recipes to your library.
        </p>
        <div v-else-if="suggestions.length" class="suggestions-grid">
          <MealPlanCard
            v-for="r in suggestions"
            :key="r.id"
            :recipe="r"
            variant="suggestion"
            :denied="deniedIds.has(r.id)"
            @accept="acceptSuggestion"
            @deny="toggleDeny"
          />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRecipeStore } from '@/stores/recipes'
import MealPlanCard from '@/components/MealPlanCard.vue'

const store = useRecipeStore()

const stage = ref('count') // 'count' | 'plan'
const mealCount = ref(null)
const accepted = ref([])
const suggestions = ref([])
const deniedIds = ref(new Set())
const cooldown = ref(new Map())
const hasGeneratedOnce = ref(false)
const searchInput = ref('')

onMounted(async () => {
  await store.fetchRecipes()
})

const isPlanComplete = computed(() => accepted.value.length === mealCount.value)

const searchResults = computed(() => {
  if (!searchInput.value.trim()) return []
  const q = searchInput.value.toLowerCase()
  const acceptedIds = new Set(accepted.value.map(r => r.id))
  return store.recipes.filter(r => !acceptedIds.has(r.id) && r.title.toLowerCase().includes(q))
})

function selectMealCount(n) {
  mealCount.value = n
  stage.value = 'plan'
}

function sample(pool, n) {
  const arr = [...pool]
  const result = []
  for (let i = 0; i < n && arr.length > 0; i++) {
    const idx = Math.floor(Math.random() * arr.length)
    result.push(arr.splice(idx, 1)[0])
  }
  return result
}

function eligiblePool() {
  const acceptedIds = new Set(accepted.value.map(r => r.id))
  return store.recipes.filter(r => !acceptedIds.has(r.id) && !cooldown.value.has(r.id))
}

function tickCooldown() {
  for (const [id, remaining] of cooldown.value) {
    if (remaining <= 1) cooldown.value.delete(id)
    else cooldown.value.set(id, remaining - 1)
  }
}

function generateSuggestions() {
  tickCooldown()
  for (const id of deniedIds.value) cooldown.value.set(id, 3)
  deniedIds.value.clear()

  const openSlots = mealCount.value - accepted.value.length
  suggestions.value = sample(eligiblePool(), openSlots)
  hasGeneratedOnce.value = true
}

function acceptRecipe(recipe) {
  if (accepted.value.length >= mealCount.value) return
  if (accepted.value.some(r => r.id === recipe.id)) return
  accepted.value.push(recipe)
  suggestions.value = suggestions.value.filter(r => r.id !== recipe.id)
  deniedIds.value.delete(recipe.id)
}

function acceptSuggestion(id) {
  const recipe = suggestions.value.find(r => r.id === id)
  if (recipe) acceptRecipe(recipe)
}

function toggleDeny(id) {
  if (deniedIds.value.has(id)) deniedIds.value.delete(id)
  else deniedIds.value.add(id)
}

function removeAccepted(id) {
  accepted.value = accepted.value.filter(r => r.id !== id)
}

function startOver() {
  stage.value = 'count'
  mealCount.value = null
  accepted.value = []
  suggestions.value = []
  deniedIds.value.clear()
  cooldown.value.clear()
  searchInput.value = ''
  hasGeneratedOnce.value = false
}
</script>

<style lang="scss" scoped>
.state-msg {
  @include state-message;
}

.count-picker {
  text-align: center;
  padding: 2rem 0;
}

.count-options {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.count-btn {
  @include outline-button($color-primary, $color-border-strong, $color-primary-light);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  font-size: 1.1rem;
  padding: 0;
}

.plan-header {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.plan-header h1 {
  flex: 1;
  font-size: 1.4rem;
  margin: 0;
}

.progress {
  font-size: 0.9rem;
  color: $color-text-muted;
}

.back-btn {
  background: none;
  border: none;
  color: $color-primary;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0;
}

.accepted-section {
  margin-bottom: 2rem;
}

.accepted-grid,
.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.empty-note {
  color: $color-text-muted;
  font-size: 0.9rem;
}

.ready-state {
  text-align: center;
  padding: 2rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.search-section {
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 0.6rem 0.9rem;
  font-size: 1rem;
  border: 1px solid $color-border-strong;
  border-radius: 8px;
  outline: none;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: $color-primary;
  box-shadow: 0 0 0 2px $color-primary-border;
}

.search-results {
  list-style: none;
  margin: 0.75rem 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.search-results li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border: 1px solid $color-border;
  border-radius: $radius-md;
}

.add-btn {
  @include outline-button($color-primary, $color-primary-border, $color-primary-light);
}

.suggestions-section {
  margin-bottom: 2rem;
}

.help-btn {
  @include button-variant($color-primary, $color-primary-dark);
  padding: 0.6rem 1.2rem;
  margin-bottom: 1.25rem;
}
</style>
