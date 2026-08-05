import { defineStore } from 'pinia'
import { ref } from 'vue'
import { mealPlansApi } from '@/services/api'

export const useMealPlanStore = defineStore('mealPlan', () => {
  const activeMealPlan = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchActiveMealPlan() {
    loading.value = true
    error.value = null
    try {
      activeMealPlan.value = await mealPlansApi.getActive()
    } catch (e) {
      if (e.status === 404) {
        activeMealPlan.value = null
      } else {
        error.value = e.message
      }
    } finally {
      loading.value = false
    }
  }

  async function createMealPlan(recipeIds) {
    const plan = await mealPlansApi.create(recipeIds)
    activeMealPlan.value = plan
    return plan
  }

  async function setItemChecked(itemId, isChecked) {
    const updated = await mealPlansApi.checkItem(itemId, isChecked)
    for (const recipe of activeMealPlan.value?.recipes ?? []) {
      const item = recipe.items.find(i => i.id === itemId)
      if (item) item.is_checked = updated.is_checked
    }
    return updated
  }

  async function deleteItem(itemId) {
    await mealPlansApi.deleteItem(itemId)
    for (const recipe of activeMealPlan.value?.recipes ?? []) {
      recipe.items = recipe.items.filter(i => i.id !== itemId)
    }
  }

  async function completeMealPlan() {
    if (!activeMealPlan.value) return
    await mealPlansApi.complete(activeMealPlan.value.id)
    activeMealPlan.value = null
  }

  async function cancelMealPlan() {
    if (!activeMealPlan.value) return
    await mealPlansApi.cancel(activeMealPlan.value.id)
    activeMealPlan.value = null
  }

  return {
    activeMealPlan, loading, error,
    fetchActiveMealPlan, createMealPlan, setItemChecked, deleteItem,
    completeMealPlan, cancelMealPlan,
  }
})
