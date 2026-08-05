<template>
  <div v-if="loading" class="state-msg">Loading…</div>
  <div v-else-if="error" class="state-msg error">{{ error }}</div>

  <div v-else-if="plan" class="archive-detail">
    <RouterLink to="/archive" class="back-link">← Back to archive</RouterLink>

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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { mealPlansApi } from '@/services/api'
import { capitalize } from '@/utils/capitalize'
import GroceryListSection from '@/components/GroceryListSection.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const plan = ref(null)
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    plan.value = await mealPlansApi.get(props.id)
  } catch (e) {
    error.value = e.message ?? 'Could not load that meal plan.'
  } finally {
    loading.value = false
  }
})

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
</style>
