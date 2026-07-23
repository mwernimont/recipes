<template>
  <div v-if="store.loading" class="state-msg">Loading…</div>
  <div v-else-if="store.error" class="state-msg error">{{ store.error }}</div>

  <div v-else-if="recipe" class="detail">

    <!-- Header -->
    <div class="detail-header">
      <RouterLink to="/" class="back">← Back</RouterLink>
      <div class="header-actions">
        <RouterLink :to="`/recipe/${props.id}/edit`" class="btn-edit">Edit</RouterLink>
        <button class="btn-delete" @click="handleDelete">Delete</button>
      </div>
    </div>

    <!-- Hero image -->
    <div class="hero" :style="heroStyle">
      <span v-if="!recipe.image_path" class="hero-placeholder">🍽️</span>
      <label class="image-upload-btn" title="Upload image">
        📷
        <input type="file" accept="image/*" class="hidden" @change="handleImageUpload" />
      </label>
    </div>

    <!-- Title + meta -->
    <div class="detail-body">
      <h1>{{ recipe.title }}</h1>
      <p v-if="recipe.description" class="description">{{ recipe.description }}</p>

      <div class="meta-row">
        <span v-if="recipe.prep_time_minutes">⏱ Prep: {{ recipe.prep_time_minutes }}m</span>
        <span v-if="recipe.cook_time_minutes">🔥 Cook: {{ recipe.cook_time_minutes }}m</span>
        <span v-if="recipe.prep_time_minutes && recipe.cook_time_minutes">
          📋 Total: {{ recipe.prep_time_minutes + recipe.cook_time_minutes }}m
        </span>
        <a v-if="recipe.source_url" :href="recipe.source_url" target="_blank" class="source-link">
          View Source ↗
        </a>
      </div>

      <div v-if="recipe.tags?.length" class="tags-row">
        <span v-for="tag in recipe.tags" :key="tag.name" class="tag">
          {{ tag.name }}
        </span>
      </div>

      <!-- Serving scaler -->
      <div class="scaler">
        <label>Servings</label>
        <div class="scaler-controls">
          <button @click="decrementServings" :disabled="scaledServings <= 1">−</button>
          <span class="servings-display">{{ scaledServings }}</span>
          <button @click="scaledServings++">+</button>
          <button v-if="scaledServings !== recipe.servings" class="reset-btn" @click="resetServings">
            Reset
          </button>
        </div>
      </div>

      <!-- Ingredients -->
      <section class="section">
        <h2>Ingredients</h2>
        <ul class="ingredients-list">
          <li v-for="ing in scaledIngredients" :key="ing.id">
            <span class="ing-amount">
              {{ ing.amount != null ? formatAmount(ing.amount) : '' }}
              {{ ing.unit }}
            </span>
            <span class="ing-name">{{ ing.name }}</span>
          </li>
        </ul>
      </section>

      <!-- Steps -->
      <section class="section">
        <h2>Steps</h2>
        <ol class="steps-list">
          <li
            v-for="step in recipe.steps"
            :key="step.id"
            class="step"
            :class="{ done: completedSteps.has(step.order) }"
            @click="toggleStep(step.order)"
          >
            {{ step.instruction }}
          </li>
        </ol>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useRecipeStore } from '@/stores/recipes'

const props = defineProps({
  id: { type: String, required: true },
})

const store = useRecipeStore()
const router = useRouter()

const recipe = computed(() => store.currentRecipe)
const scaledServings = ref(1)
const completedSteps = ref(new Set())

onMounted(async () => {
  await store.fetchRecipe(props.id)
  resetServings()
})

function resetServings() {
  scaledServings.value = recipe.value?.servings ?? 1
}

function decrementServings() {
  if (scaledServings.value > 1) scaledServings.value--
}

// Scale ingredient amounts proportionally
const scaledIngredients = computed(() => {
  if (!recipe.value?.ingredients) return []
  const base = recipe.value.servings || 1
  const ratio = scaledServings.value / base
  return recipe.value.ingredients.map(ing => ({
    ...ing,
    amount: ing.amount != null ? ing.amount * ratio : null,
  }))
})

// Format decimals nicely: 0.5 → ½, 0.25 → ¼, 0.75 → ¾, else 1 decimal
const FRACTIONS = [
  [1/8,  '⅛'],
  [1/4,  '¼'],
  [1/3,  '⅓'],
  [3/8,  '⅜'],
  [1/2,  '½'],
  [5/8,  '⅝'],
  [2/3,  '⅔'],
  [3/4,  '¾'],
  [7/8,  '⅞'],
]

function formatAmount(val) {
  if (val == null) return ''

  const whole = Math.floor(val)
  const decimal = val - whole

  // Close enough to a whole number
  if (decimal < 0.05) return `${whole || ''}`
  if (decimal > 0.95) return `${whole + 1}`

  // Find the closest fraction
  let closest = FRACTIONS[0]
  let minDiff = Math.abs(decimal - FRACTIONS[0][0])

  for (const f of FRACTIONS) {
    const diff = Math.abs(decimal - f[0])
    if (diff < minDiff) {
      minDiff = diff
      closest = f
    }
  }

  return whole > 0 ? `${whole} ${closest[1]}` : closest[1]
}

// Step completion toggle
function toggleStep(stepNumber) {
  const s = new Set(completedSteps.value)
  s.has(stepNumber) ? s.delete(stepNumber) : s.add(stepNumber)
  completedSteps.value = s
}

// Hero image
const heroStyle = computed(() => {
  if (!recipe.value?.image_path) return {}
  return {
    backgroundImage: `url(${recipe.value.image_path})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  }
})

async function handleImageUpload(e) {
  const file = e.target.files[0]
  if (file) await store.uploadImage(props.id, file)
}

async function handleDelete() {
  if (confirm(`Delete "${recipe.value.title}"?`)) {
    await store.deleteRecipe(props.id)
    router.push('/')
  }
}
</script>

<style lang="scss" scoped>
.state-msg {
  @include state-message;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.back {
  color: $color-primary;
  text-decoration: none;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-edit {
  @include outline-button($color-primary, $color-primary-border, $color-primary-light);
  text-decoration: none;
}

.btn-delete {
  @include outline-button($color-danger, $color-danger-border, $color-danger-light);
}

.hero {
  position: relative;
  height: 280px;
  background: $color-bg-subtle;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.hero-placeholder {
  font-size: 4rem;
}

.image-upload-btn {
  position: absolute;
  bottom: 0.75rem;
  right: 0.75rem;
  background: rgba(0, 0, 0, 0.45);
  color: white;
  border-radius: $radius-md;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 1rem;
}

.hidden {
  display: none;
}

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

h1 {
  margin: 0;
  font-size: 1.75rem;
}

.description {
  color: $color-body;
  margin: 0;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.875rem;
  color: $color-text-muted;
}

.source-link {
  color: $color-primary;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.tag {
  @include tag-pill;
}

/* Scaler */
.scaler {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: $color-bg-muted;
  border-radius: 8px;
  border: 1px solid $color-border;
}

.scaler label {
  font-weight: 600;
  font-size: 0.9rem;
}

.scaler-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scaler-controls button {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid $color-border-strong;
  background: $color-bg;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;

  &:disabled {
    opacity: 0.35;
    cursor: default;
  }

  &.reset-btn {
    width: auto;
    height: auto;
    font-size: 0.75rem;
    border-radius: $radius-md;
    padding: 0.2rem 0.5rem;
    color: $color-text-muted;
  }
}

.servings-display {
  font-size: 1.1rem;
  font-weight: 600;
  min-width: 2rem;
  text-align: center;
}

/* Ingredients */
.section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.section h2 {
  font-size: 1.15rem;
  margin: 0;
}

.ingredients-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.ingredients-list li {
  display: flex;
  gap: 0.5rem;
  font-size: 0.95rem;
  padding: 0.4rem 0;
  border-bottom: 1px solid $color-bg-subtle;
}

.ing-amount {
  min-width: 80px;
  color: $color-heading;
  font-weight: 500;
}

.ing-name {
  color: $color-body;
}

/* Steps */
.steps-list {
  padding-left: 1.5rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.step {
  font-size: 0.95rem;
  line-height: 1.6;
  color: $color-heading;
  cursor: pointer;
  padding: 0.5rem 0.25rem;
  border-radius: $radius-sm;
  transition: all 0.15s;
}

.step:hover {
  background: $color-bg-muted;
}

.step.done {
  color: $color-text-subtle;
  text-decoration: line-through;
}
</style>