<template>
  <div v-if="loading" class="state-msg">Loading…</div>
  <div v-else-if="error" class="state-msg error">{{ error }}</div>

  <div v-else class="archive">
    <h1>Meal Plan Archive</h1>

    <p v-if="plans.length === 0" class="empty-note">
      No past meal plans yet. Plans show up here once you complete or cancel them.
    </p>

    <ul v-else class="plan-list">
      <li v-for="plan in plans" :key="plan.id">
        <RouterLink :to="`/archive/${plan.id}`" class="plan-card">
          <div class="plan-card-header">
            <span class="plan-date">{{ formatDate(plan.created_at) }}</span>
            <span class="plan-status" :class="plan.status">{{ capitalize(plan.status) }}</span>
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
