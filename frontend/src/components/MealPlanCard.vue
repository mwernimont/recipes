<template>
  <div class="card" :class="{ denied }">
    <div class="card-image" :style="imageStyle">
      <span v-if="!recipe.image_path" class="card-placeholder">🍽️</span>
    </div>

    <div class="card-body">
      <h3 class="card-title">{{ recipe.title }}</h3>

      <p v-if="recipe.description" class="card-desc">{{ recipe.description }}</p>

      <div class="card-meta">
        <span v-if="recipe.prep_time_minutes || recipe.cook_time_minutes">⏱ {{ (recipe.prep_time_minutes ?? 0) + (recipe.cook_time_minutes ?? 0) }}m</span>
        <span v-if="recipe.servings">🍴 {{ recipe.servings }}</span>
      </div>

      <div v-if="recipe.tags?.length" class="card-tags">
        <span v-for="tag in recipe.tags" :key="tag.name" class="tag">
          {{ tag.name }}
        </span>
      </div>
    </div>

    <div v-if="variant === 'suggestion'" class="card-actions">
      <button class="action-btn accept" title="Accept" @click="$emit('accept', recipe.id)">✔</button>
      <button class="action-btn deny" :class="{ active: denied }" title="Deny" @click="$emit('deny', recipe.id)">✕</button>
    </div>
    <button v-else class="card-remove" @click="$emit('remove', recipe.id)">✕ Remove</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  recipe: { type: Object, required: true },
  variant: { type: String, default: 'suggestion' },
  denied: { type: Boolean, default: false },
})

defineEmits(['accept', 'deny', 'remove'])

const imageStyle = computed(() => {
  if (!props.recipe.image_path) return {}
  return {
    backgroundImage: `url(${props.recipe.image_path})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  }
})
</script>

<style lang="scss" scoped>
.card {
  @include card;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow 0.15s, opacity 0.15s;
}

.card:hover {
  box-shadow: $shadow-md;
}

.card.denied {
  opacity: 0.55;
}

.card-image {
  height: 160px;
  background: $color-bg-subtle;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-placeholder {
  font-size: 2.5rem;
}

.card-body {
  padding: 0.9rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
}

.card-desc {
  font-size: 0.82rem;
  color: $color-text-muted;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.78rem;
  color: $color-text-muted;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-top: 0.25rem;
}

.tag {
  @include tag-pill;
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0 1rem 0.9rem;
}

.action-btn {
  flex: 1;

  &.accept {
    @include outline-button($color-primary, $color-primary-border, $color-primary-light);
  }

  &.deny {
    @include outline-button($color-danger, $color-danger-border, $color-danger-light);

    &.active {
      background: $color-danger-light;
      border-color: $color-danger;
    }
  }
}

.card-remove {
  @include outline-button($color-danger, $color-danger-border, $color-danger-light);
  margin: 0 1rem 0.9rem;
}
</style>
