<template>
  <div class="preview-form">
    <div class="preview-header">
      <button class="back-btn" @click="$emit('back')">← Back</button>
      <h1>{{ heading }}</h1>
    </div>

    <!-- Core fields -->
    <section class="section">
      <label><span class="label-text">Title *</span>
        <input v-model="form.title" type="text" placeholder="Recipe title" />
      </label>
      <label><span class="label-text">Source URL</span>
        <input v-model="form.source_url" type="url" placeholder="https://…" />
      </label>
      <label><span class="label-text">Description</span>
        <textarea v-model="form.description" rows="5" placeholder="Brief description…" />
      </label>
    </section>

    <!-- Times + servings -->
    <section class="section timing">
      <label><span class="label-text">Prep (mins)</span>
        <input v-model.number="form.prep_time_minutes" type="number" min="0" />
      </label>
      <label><span class="label-text">Cook (mins)</span>
        <input v-model.number="form.cook_time_minutes" type="number" min="0" />
      </label>
      <label><span class="label-text">Servings</span>
        <input v-model.number="form.servings" type="number" min="1" />
      </label>
    </section>

    <!-- Ingredients -->
    <section class="section">
      <div class="section-header">
        <h2>Ingredients</h2>
        <button class="add-btn" @click="addIngredient">+ Add</button>
      </div>
      <div
        v-for="(ing, i) in form.ingredients"
        :key="i"
        class="ingredient-row"
      >
        <input v-model.number="ing.amount" type="number" placeholder="Qty" step="0.1" min="0" />
        <input v-model="ing.unit" type="text" placeholder="Unit" />
        <input v-model="ing.name" type="text" placeholder="Ingredient" class="flex-grow" />
        <button class="remove-btn" @click="removeIngredient(i)">✕</button>
      </div>
    </section>

    <!-- Steps -->
    <section class="section">
      <div class="section-header">
        <h2>Steps</h2>
        <button class="add-btn" @click="addStep">+ Add</button>
      </div>
      <div
        v-for="(step, i) in form.steps"
        :key="i"
        class="step-row"
      >
        <span class="step-num">{{ i + 1 }}</span>
        <textarea v-model="step.instruction" rows="2" placeholder="Step instruction…" />
        <button class="remove-btn" @click="removeStep(i)">✕</button>
      </div>
    </section>

    <!-- Tags -->
    <section class="section">
      <div class="section-header">
        <h2>Tags</h2>
      </div>
      <div class="tags-row">
        <span
          v-for="tag in form.tags"
          :key="tag"
          class="tag"
        >
          {{ tag }}
          <button @click="removeTag(tag)">✕</button>
        </span>
        <input
          v-model="newTag"
          type="text"
          placeholder="Add tag…"
          @keydown.enter.prevent="addTag"
          @keydown.comma.prevent="addTag"
        />
      </div>
    </section>

    <!-- Save -->
    <div class="save-row">
      <button
        class="save-btn"
        :disabled="!form.title.trim() || saving"
        @click="submit"
      >
        {{ saving ? 'Saving…' : submitLabel }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  recipe: { type: Object, required: true },
  saving: Boolean,
  heading: { type: String, default: 'Review Recipe' },
  submitLabel: { type: String, default: 'Save Recipe' },
})

const emit = defineEmits(['save', 'back'])

// Deep clone so edits don't mutate the scraped draft
const form = reactive({
  title: props.recipe.title ?? '',
  description: props.recipe.description ?? '',
  source_url: props.recipe.source_url ?? '',
  prep_time_minutes: props.recipe.prep_time_minutes ?? null,
  cook_time_minutes: props.recipe.cook_time_minutes ?? null,
  servings: props.recipe.servings ?? null,
  ingredients: (props.recipe.ingredients ?? []).map(i => ({ ...i })),
  steps: (props.recipe.steps ?? []).map(s => ({ ...s })),
  tags: [...(props.recipe.tags?.map(t => t.name ?? t) ?? [])],
})

const newTag = ref('')

// Ingredients
function addIngredient() {
  form.ingredients.push({ amount: null, unit: '', name: '' })
}
function removeIngredient(i) {
  form.ingredients.splice(i, 1)
}

// Steps
function addStep() {
  form.steps.push({ instruction: '', order: form.steps.length + 1 })
}
function removeStep(i) {
  form.steps.splice(i, 1)
  // Renumber
  form.steps.forEach((s, idx) => { s.order = idx + 1 })
}

// Tags
function addTag() {
  const t = newTag.value.trim().toLowerCase().replace(/,$/, '')
  if (t && !form.tags.includes(t)) form.tags.push(t)
  newTag.value = ''
}
function removeTag(tag) {
  form.tags = form.tags.filter(t => t !== tag)
}

function submit() {
  emit('save', { ...form })
}
</script>
<style scoped>
.section{
  display:flex;
  flex-direction: column;
  flex-wrap: wrap;
}

label{
  margin-bottom: 10px;
  flex: 1;
  display: grid;
  grid-template-columns: 85px 1fr;
  align-items: center;
  gap: 10px;
}

.label-text{
  flex-shrink: 0;
}

input, textarea{
  width: 100%;
  max-width: 100%;
  padding: 5px;
}

.ingredient-row, .step-row{
  display: flex;
  gap: 10px;
  margin-top: 10px;
  align-items: center;
}

</style>