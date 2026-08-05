<template>
  <section class="recipe-section">
    <h2>
      <RouterLink v-if="recipe.recipe_id" :to="`/recipe/${recipe.recipe_id}`">
        {{ recipe.recipe_title }}
      </RouterLink>
      <template v-else>{{ recipe.recipe_title }}</template>
    </h2>

    <p v-if="recipe.items.length === 0" class="empty-note">No ingredients listed.</p>
    <ul v-else class="item-list">
      <li
        v-for="item in recipe.items"
        :key="item.id"
        class="item"
        :class="{ checked: item.is_checked }"
      >
        <label class="item-label">
          <input
            type="checkbox"
            :checked="item.is_checked"
            :disabled="readonly"
            @change="$emit('toggle-item', item, $event)"
          />
          <span class="item-amount">
            {{ item.amount != null ? formatAmount(item.amount) : '' }}
            {{ item.unit }}
          </span>
          <span class="item-name">{{ item.name }}</span>
        </label>
        <button
          v-if="!readonly"
          class="remove-btn"
          title="Remove"
          @click="$emit('remove-item', item)"
        >
          ✕
        </button>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { formatAmount } from '@/utils/formatAmount'

defineProps({
  recipe: { type: Object, required: true },
  readonly: Boolean,
})

defineEmits(['toggle-item', 'remove-item'])
</script>

<style lang="scss" scoped>
.recipe-section {
  margin-bottom: 2rem;
}

.recipe-section h2 {
  font-size: 1.1rem;
  margin-bottom: 0.6rem;
}

.recipe-section h2 a {
  color: inherit;
  text-decoration: none;
}

.recipe-section h2 a:hover {
  text-decoration: underline;
}

.empty-note {
  color: $color-text-muted;
  font-size: 0.9rem;
}

.item-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid $color-border;
  border-radius: $radius-md;
}

.item-label {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  cursor: pointer;
  flex: 1;
}

.item-amount {
  color: $color-text-muted;
  font-size: 0.9rem;
  white-space: nowrap;
}

.item.checked .item-name,
.item.checked .item-amount {
  text-decoration: line-through;
  color: $color-text-muted;
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
</style>
