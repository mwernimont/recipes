<template>
  <RouterLink :to="`/recipe/${recipe.id}`" class="card">
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

    <button class="card-delete" @click.prevent="$emit('delete', recipe.id)">✕</button>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  recipe: { type: Object, required: true },
})

defineEmits(['delete'])

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
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid $color-border;
  border-radius: $radius-lg;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.15s;
}

.card:hover {
  box-shadow: $shadow-md;
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

.card-delete {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.35);
  color: white;
  font-size: 0.7rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.15s;
}

.card:hover .card-delete {
  opacity: 1;
}
</style>