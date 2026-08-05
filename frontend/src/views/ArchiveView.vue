<template>
  <div v-if="loading" class="state-msg">Loading…</div>
  <div v-else-if="error" class="state-msg error">{{ error }}</div>

  <div v-else class="archive">
    <h1>Meal Plan Archive</h1>

    <p v-if="actionError" class="action-error">{{ actionError }}</p>

    <p v-if="plans.length === 0" class="empty-note">
      No past meal plans yet. Plans show up here once you complete or cancel them.
    </p>

    <ul v-else class="plan-list">
      <li v-for="plan in plans" :key="plan.id">
        <RouterLink :to="`/archive/${plan.id}`" class="plan-card">
          <div class="plan-card-header">
            <span class="plan-date">{{ formatDate(plan.created_at) }}</span>
            <div class="plan-card-actions">
              <span class="plan-status" :class="plan.status">{{ capitalize(plan.status) }}</span>
              <button class="remove-btn" title="Delete" @click.prevent="handleDelete(plan)">✕</button>
            </div>
          </div>
          <p class="plan-recipes">{{ recipeTitles(plan) }}</p>
        </RouterLink>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { mealPlansApi } from '@/services/api'
import { capitalize } from '@/utils/capitalize'

const plans = ref([])
const loading = ref(true)
const error = ref(null)
const actionError = ref(null)

onMounted(async () => {
  try {
    const all = await mealPlansApi.list()
    plans.value = all.filter(p => p.status !== 'active')
  } catch (e) {
    error.value = e.message ?? 'Could not load the archive.'
  } finally {
    loading.value = false
  }
})

async function handleDelete(plan) {
  if (!confirm(`Delete this meal plan from ${formatDate(plan.created_at)}? This can't be undone.`)) return

  actionError.value = null
  try {
    await mealPlansApi.delete(plan.id)
    plans.value = plans.value.filter(p => p.id !== plan.id)
  } catch (e) {
    actionError.value = e.message ?? 'Could not delete that meal plan.'
  }
}

function recipeTitles(plan) {
  return plan.recipes.map(r => r.recipe_title).join(', ')
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

.archive h1 {
  margin-bottom: 1.5rem;
}

.empty-note {
  color: $color-text-muted;
}

.action-error {
  color: $color-danger;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.plan-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.plan-card {
  @include card;
  display: block;
  padding: 1rem 1.25rem;
  color: inherit;
  text-decoration: none;
  transition: border-color 0.15s ease;
}

.plan-card:hover {
  border-color: $color-border-strong;
}

.plan-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.plan-date {
  font-weight: 600;
}

.plan-card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remove-btn {
  background: none;
  border: none;
  color: $color-text-muted;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.15rem 0.4rem;
}

.remove-btn:hover {
  color: $color-danger;
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

.plan-recipes {
  color: $color-text-muted;
  font-size: 0.9rem;
  margin: 0;
}
</style>
