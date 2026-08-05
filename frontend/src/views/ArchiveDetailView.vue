<template>
  <div v-if="loading" class="state-msg">Loading…</div>
  <div v-else-if="error" class="state-msg error">{{ error }}</div>

  <div v-else-if="plan" class="archive-detail">
    <RouterLink to="/archive" class="back-link">← Back to archive</RouterLink>

    <p v-if="actionError" class="action-error">{{ actionError }}</p>

    <div class="list-header">
      <div>
        <h1>Grocery List</h1>
        <span class="plan-date">{{ formatDate(plan.created_at) }}</span>
        <span class="plan-status" :class="plan.status">{{ capitalize(plan.status) }}</span>
      </div>
      <span class="recipe-count">{{ plan.recipes.length }} recipes</span>
    </div>

    <GroceryListSection
      v-for="recipe in plan.recipes"
      :key="recipe.id"
      :recipe="recipe"
      readonly
    />

    <div class="list-footer">
      <p v-if="reuseNote" class="reuse-note">{{ reuseNote }}</p>
      <div class="footer-actions">
        <button class="delete-btn" @click="handleDelete">Delete Plan</button>
        <button
          class="reuse-btn"
          :disabled="!canReuse || reusing"
          :title="reuseDisabledReason"
          @click="handleReuse"
        >
          {{ reusing ? 'Starting…' : '↻ Reuse This Plan' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { mealPlansApi } from '@/services/api'
import { capitalize } from '@/utils/capitalize'
import { useRecipeStore } from '@/stores/recipes'
import { useMealPlanStore } from '@/stores/mealPlan'
import GroceryListSection from '@/components/GroceryListSection.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const router = useRouter()
const recipeStore = useRecipeStore()
const mealPlanStore = useMealPlanStore()

const plan = ref(null)
const loading = ref(true)
const error = ref(null)
const actionError = ref(null)
const reusing = ref(false)

onMounted(async () => {
  try {
    const [loadedPlan] = await Promise.all([
      mealPlansApi.get(props.id),
      recipeStore.recipes.length === 0 ? recipeStore.fetchRecipes() : null,
      // Don't rely on App.vue's own fire-and-forget check having resolved
      // yet - the reuse button needs an up-to-date answer before it renders.
      mealPlanStore.fetchActiveMealPlan(),
    ])
    plan.value = loadedPlan
  } catch (e) {
    error.value = e.message ?? 'Could not load that meal plan.'
  } finally {
    loading.value = false
  }
})

// Only recipes still in the library can be reused - a plan can outlive the
// recipes it was built from, since GroceryListItem snapshots ingredients
// rather than referencing them live.
const reusableRecipeIds = computed(() => {
  if (!plan.value) return []
  const libraryIds = new Set(recipeStore.recipes.map(r => r.id))
  return plan.value.recipes
    .filter(r => r.recipe_id != null && libraryIds.has(r.recipe_id))
    .map(r => r.recipe_id)
})

const reuseNote = computed(() => {
  if (!plan.value) return null
  const missing = plan.value.recipes.length - reusableRecipeIds.value.length
  if (missing === 0) return null
  if (reusableRecipeIds.value.length === 0) {
    return "None of these recipes are still in your library, so this plan can't be reused."
  }
  return `${missing} of ${plan.value.recipes.length} recipes have been removed from your library and won't be included.`
})

const canReuse = computed(() =>
  !mealPlanStore.activeMealPlan && reusableRecipeIds.value.length > 0
)

const reuseDisabledReason = computed(() => {
  if (mealPlanStore.activeMealPlan) return 'Finish or cancel your current meal plan first'
  if (reusableRecipeIds.value.length === 0) return "None of these recipes are still in your library"
  return null
})

async function handleReuse() {
  reusing.value = true
  actionError.value = null
  try {
    await mealPlanStore.createMealPlan(reusableRecipeIds.value)
    router.push('/grocery-list')
  } catch (e) {
    actionError.value = e.message ?? 'Could not reuse this meal plan.'
    reusing.value = false
  }
}

async function handleDelete() {
  if (!confirm(`Delete this meal plan from ${formatDate(plan.value.created_at)}? This can't be undone.`)) return

  actionError.value = null
  try {
    await mealPlansApi.delete(plan.value.id)
    router.push('/archive')
  } catch (e) {
    actionError.value = e.message ?? 'Could not delete that meal plan.'
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}
</script>

<style lang="scss" scoped>
.state-msg {
  @include state-message;
}

.back-link {
  display: inline-block;
  color: $color-primary;
  text-decoration: none;
  font-size: 0.9rem;
  margin-bottom: 1.25rem;
}

.back-link:hover {
  text-decoration: underline;
}

.action-error {
  color: $color-danger;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.list-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.plan-date {
  color: $color-text-muted;
  font-size: 0.9rem;
  margin-right: 0.5rem;
}

.plan-status {
  @include tag-pill($color-text-muted, $color-bg-subtle, $color-border-strong);
}

.plan-status.completed {
  @include tag-pill($color-primary, $color-primary-light, $color-primary-border);
}

.plan-status.cancelled {
  @include tag-pill($color-danger, $color-danger-light, $color-danger-border);
}

.recipe-count {
  font-size: 0.9rem;
  color: $color-text-muted;
}

.list-footer {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid $color-border;
}

.reuse-note {
  color: $color-text-muted;
  font-size: 0.85rem;
  margin: 0 0 0.75rem;
  text-align: right;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.delete-btn {
  @include outline-button($color-danger, $color-danger-border, $color-danger-light);
}

.reuse-btn {
  @include button-variant($color-primary, $color-primary-dark);

  &:disabled {
    background: $color-bg-subtle;
    color: $color-text-muted;
    cursor: not-allowed;
  }
}
</style>
