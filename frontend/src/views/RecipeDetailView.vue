<template>
  <div v-if="store.loading" class="state-msg">Loading…</div>
  <div v-else-if="store.error" class="state-msg error">{{ store.error }}</div>

  <div v-else-if="recipe" class="detail">

    <!-- Header -->
    <div class="detail-header">
      <RouterLink to="/" class="back">← Back</RouterLink>
      <div class="header-actions">
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
        <span v-if="recipe.prep_time">⏱ Prep: {{ recipe.prep_time }}m</span>
        <span v-if="recipe.cook_time">🔥 Cook: {{ recipe.cook_time }}m</span>
        <span v-if="recipe.prep_time && recipe.cook_time">
          📋 Total: {{ recipe.prep_time + recipe.cook_time }}m
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
            :class="{ done: completedSteps.has(step.step_number) }"
            @click="toggleStep(step.step_number)"
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
    backgroundImage: `url(/uploads/${recipe.value.image_path})`,
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

<style scoped>
.state-msg {
  text-align: center;
  padding: 3rem 0;
  color: #6b7280;
}
.state-msg.error { color: #dc2626; }

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.back {
  color: #16a34a;
  text-decoration: none;
  font-size: 0.9rem;
}

.btn-delete {
  background: none;
  border: 1px solid #fca5a5;
  color: #dc2626;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-delete:hover {
  background: #fef2f2;
}

.hero {
  position: relative;
  height: 280px;
  background: #f3f4f6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.hero-placeholder { font-size: 4rem; }

.image-upload-btn {
  position: absolute;
  bottom: 0.75rem;
  right: 0.75rem;
  background: rgba(0,0,0,0.45);
  color: white;
  border-radius: 6px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 1rem;
}

.hidden { display: none; }

.detail-body { display: flex; flex-direction: column; gap: 1rem; }

h1 { margin: 0; font-size: 1.75rem; }

.description { color: #4b5563; margin: 0; }

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.source-link { color: #16a34a; }

.tags-row { display: flex; flex-wrap: wrap; gap: 0.4rem; }

.tag {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 999px;
  border: 1px solid #bbf7d0;
}

/* Scaler */
.scaler {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.scaler label { font-weight: 600; font-size: 0.9rem; }

.scaler-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scaler-controls button {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 1px solid #d1d5db;
  background: white;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.scaler-controls button:disabled { opacity: 0.35; cursor: default; }

.servings-display {
  font-size: 1.1rem;
  font-weight: 600;
  min-width: 2rem;
  text-align: center;
}

.reset-btn {
  font-size: 0.75rem !important;
  width: auto !important;
  height: auto !important;
  border-radius: 6px !important;
  padding: 0.2rem 0.5rem;
  color: #6b7280;
}

/* Ingredients */
.section { display: flex; flex-direction: column; gap: 0.6rem; }
.section h2 { font-size: 1.15rem; margin: 0; }

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
  border-bottom: 1px solid #f3f4f6;
}

.ing-amount {
  min-width: 80px;
  color: #374151;
  font-weight: 500;
}

.ing-name { color: #4b5563; }

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
  color: #374151;
  cursor: pointer;
  padding: 0.5rem 0.25rem;
  border-radius: 4px;
  transition: all 0.15s;
}

.step:hover { background: #f9fafb; }

.step.done {
  color: #9ca3af;
  text-decoration: line-through;
}
</style>