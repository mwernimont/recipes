<template>
  <div class="add-recipe">
    <ScrapeForm
      v-if="stage === 'input'"
      :loading="scraping"
      :error="scrapeError"
      @scrape="handleScrape"
      @manual="handleManual"
    />

    <RecipePreviewForm
      v-else-if="stage === 'preview'"
      :recipe="draft"
      :saving="saving"
      @save="handleSave"
      @back="resetToInput"
    />

    <div v-else-if="stage === 'done'" class="done">
      <p>✅ Recipe saved!</p>
      <RouterLink :to="`/recipe/${savedId}`">View Recipe</RouterLink>
      <button @click="resetToInput">Add Another</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { scraperApi } from '@/services/api'
import { useRecipeStore } from '@/stores/recipes'
import ScrapeForm from '@/components/ScrapeForm.vue'
import RecipePreviewForm from '@/components/RecipePreviewForm.vue'

const store = useRecipeStore()

const stage = ref('input')       // 'input' | 'preview' | 'done'
const draft = ref(null)
const scraping = ref(false)
const scrapeError = ref(null)
const saving = ref(false)
const savedId = ref(null)

async function handleScrape(url) {
  scraping.value = true
  scrapeError.value = null
  try {
    draft.value = await scraperApi.scrape(url)
    stage.value = 'preview'
  } catch (e) {
    scrapeError.value = e.message ?? 'Could not scrape that URL. Try manual entry.'
  } finally {
    scraping.value = false
  }
}

function handleManual() {
  draft.value = emptyRecipe()
  stage.value = 'preview'
}

async function handleSave(recipeData) {
  saving.value = true
  try {
    const saved = await store.createRecipe(recipeData)
    savedId.value = saved.id
    stage.value = 'done'
  } finally {
    saving.value = false
  }
}

function resetToInput() {
  stage.value = 'input'
  draft.value = null
  scrapeError.value = null
  savedId.value = null
}

function emptyRecipe() {
  return {
    title: '',
    description: '',
    source_url: '',
    prep_time_minutes: null,
    cook_time_minutes: null,
    servings: null,
    ingredients: [],
    steps: [],
    tags: [],
  }
}
</script>