<template>
  <div class="library">
    <div class="library-header">
      <h1>My Recipes</h1>
      <span class="recipe-count">{{ filteredRecipes.length }} recipes</span>
    </div>

    <!-- Search + filters -->
    <div class="controls">
      <input
        v-model="searchInput"
        type="search"
        placeholder="Search recipes…"
        class="search-input"
        @input="store.setSearch(searchInput)"
      />
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="state-msg">Loading…</div>

    <!-- Error -->
    <div v-else-if="store.error" class="state-msg error">{{ store.error }}</div>

    <!-- Empty state -->
    <div v-else-if="filteredRecipes.length === 0" class="empty">
      <p v-if="store.searchQuery">
        No recipes match your search.
        <button @click="store.clearFilters">Clear filters</button>
      </p>
      <p v-else>
        No recipes yet.
        <RouterLink to="/add">Add your first one →</RouterLink>
      </p>
    </div>

    <!-- Recipe grid -->
    <div v-else class="recipe-grid">
      <RecipeCard
        v-for="recipe in filteredRecipes"
        :key="recipe.id"
        :recipe="recipe"
        @delete="handleDelete"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useRecipeStore } from '@/stores/recipes'
import RecipeCard from '@/components/RecipeCard.vue'

const store = useRecipeStore()
const searchInput = ref(store.searchQuery)
const filteredRecipes = computed(() => store.filteredRecipes)

onMounted(async () => {
  await store.fetchRecipes()
})

async function handleDelete(id) {
  if (confirm('Delete this recipe?')) {
    await store.deleteRecipe(id)
  }
}
</script>

<style lang="scss" scoped>
.library-header {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.recipe-count {
  font-size: 0.9rem;
  color: $color-text-muted;
}

.controls {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 0.6rem 0.9rem;
  font-size: 1rem;
  border: 1px solid $color-border-strong;
  border-radius: 8px;
  outline: none;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: $color-primary;
  box-shadow: 0 0 0 2px $color-primary-border;
}

.recipe-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.state-msg {
  @include state-message;
}

.empty {
  text-align: center;
  padding: 3rem 0;
  color: $color-text-muted;
}

.empty a,
.empty button {
  color: $color-primary;
  background: none;
  border: none;
  cursor: pointer;
  font-size: inherit;
  text-decoration: underline;
  padding: 0;
}
</style>