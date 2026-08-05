<template>
  <div v-if="loading" class="state-msg">Loading…</div>
  <div v-else-if="!mealPlan" class="state-msg error">{{ error }}</div>

  <div v-else class="grocery-list">
    <div class="list-header">
      <h1>Grocery List</h1>
      <span class="recipe-count">{{ mealPlan.recipes.length }} recipes</span>
    </div>

    <p v-if="error" class="action-error">{{ error }}</p>

    <GroceryListSection
      v-for="recipe in mealPlan.recipes"
      :key="recipe.id"
      :recipe="recipe"
      @toggle-item="toggleItem"
      @remove-item="removeItem"
    />

    <div class="list-footer">
      <button class="cancel-btn" :disabled="finishing" @click="handleCancel">
        Cancel Plan
      </button>
      <button class="complete-btn" :disabled="finishing" @click="handleComplete">
        {{ finishing ? 'Finishing…' : '✓ Mark Complete' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMealPlanStore } from '@/stores/mealPlan'
import GroceryListSection from '@/components/GroceryListSection.vue'

const mealPlanStore = useMealPlanStore()
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const finishing = ref(false)
const mealPlan = computed(() => mealPlanStore.activeMealPlan)

onMounted(async () => {
  if (!mealPlanStore.activeMealPlan) {
    await mealPlanStore.fetchActiveMealPlan()
  }
  loading.value = false

  if (mealPlanStore.error) {
    // A real failure fetching the plan - show it rather than silently
    // bouncing to the meal-plan builder as if there just wasn't one.
    error.value = mealPlanStore.error
    return
  }
  if (!mealPlanStore.activeMealPlan) {
    router.push('/meal-plan')
  }
})

async function toggleItem(item, event) {
  error.value = null
  try {
    await mealPlanStore.setItemChecked(item.id, event.target.checked)
  } catch (e) {
    error.value = e.message ?? 'Could not update that item.'
    // The store's is_checked never changed, but the checkbox's own DOM
    // state already flipped on click and won't revert on its own since
    // the bound value (item.is_checked) didn't change - reset it by hand.
    event.target.checked = item.is_checked
  }
}

async function removeItem(item) {
  error.value = null
  try {
    await mealPlanStore.deleteItem(item.id)
  } catch (e) {
    error.value = e.message ?? 'Could not remove that item.'
  }
}

async function handleComplete() {
  finishing.value = true
  error.value = null
  try {
    await mealPlanStore.completeMealPlan()
    router.push('/')
  } catch (e) {
    error.value = e.message ?? 'Could not complete the meal plan.'
  } finally {
    finishing.value = false
  }
}

async function handleCancel() {
  if (!confirm("Cancel this meal plan? You won't be able to continue shopping against it.")) return

  finishing.value = true
  error.value = null
  try {
    await mealPlanStore.cancelMealPlan()
    router.push('/meal-plan')
  } catch (e) {
    error.value = e.message ?? 'Could not cancel the meal plan.'
  } finally {
    finishing.value = false
  }
}
</script>

<style lang="scss" scoped>
.state-msg {
  @include state-message;
}

.list-header {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.recipe-count {
  font-size: 0.9rem;
  color: $color-text-muted;
}

.action-error {
  color: $color-danger;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.list-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid $color-border;
}

.cancel-btn {
  @include outline-button($color-danger, $color-danger-border, $color-danger-light);
}

.complete-btn {
  @include button-variant($color-primary, $color-primary-dark);
}
</style>
