import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { recipesApi } from '@/services/api'

export const useRecipeStore = defineStore('recipes', () => {
  // --- State ---
  const recipes = ref([])
  const currentRecipe = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Search / filter state
  const searchQuery = ref('')

  // --- Getters ---
  const filteredRecipes = computed(() => {
    let result = recipes.value

    if (searchQuery.value.trim()) {
      const q = searchQuery.value.toLowerCase()
      result = result.filter(r =>
        r.title.toLowerCase().includes(q) ||
        r.description?.toLowerCase().includes(q)
      )
    }

    return result
  })

  // --- Actions ---
  async function fetchRecipes(params = {}) {
    loading.value = true
    error.value = null
    try {
      recipes.value = await recipesApi.list(params)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchRecipe(id) {
    loading.value = true
    error.value = null
    try {
      currentRecipe.value = await recipesApi.get(id)
    } catch (e) {
      error.value = e.message
      currentRecipe.value = null
    } finally {
      loading.value = false
    }
  }

  async function createRecipe(data) {
    const recipe = await recipesApi.create(data)
    recipes.value.unshift(recipe)
    return recipe
  }

  async function updateRecipe(id, data) {
    const updated = await recipesApi.update(id, data)
    const idx = recipes.value.findIndex(r => r.id === id)
    if (idx !== -1) recipes.value[idx] = updated
    if (currentRecipe.value?.id === id) currentRecipe.value = updated
    return updated
  }

  async function deleteRecipe(id) {
    await recipesApi.delete(id)
    recipes.value = recipes.value.filter(r => r.id !== id)
    if (currentRecipe.value?.id === id) currentRecipe.value = null
  }

  async function uploadImage(id, file) {
    const updated = await recipesApi.uploadImage(id, file)
    const idx = recipes.value.findIndex(r => r.id === id)
    if (idx !== -1) recipes.value[idx] = updated
    if (currentRecipe.value?.id === id) currentRecipe.value = updated
    return updated
  }

  function setSearch(q) {
    searchQuery.value = q
  }

  function clearFilters() {
    searchQuery.value = ''
  }

  return {
    // State
    recipes, currentRecipe, loading, error,
    searchQuery,
    // Getters
    filteredRecipes,
    // Actions
    fetchRecipes, fetchRecipe, createRecipe, updateRecipe,
    deleteRecipe, uploadImage,
    setSearch, clearFilters,
  }
})