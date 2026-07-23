<template>
  <div id="app">
    <header class="nav">
      <RouterLink to="/" class="nav-logo">🗄️ Recipe Vault</RouterLink>
      <div class="nav-actions">
        <RouterLink to="/meal-plan" class="nav-add">Meal Plan</RouterLink>
        <RouterLink to="/add" class="nav-add">+ Add Recipe</RouterLink>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style lang="scss" scoped>
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $space-lg;
  height: 56px;
  border-bottom: 1px solid $color-border;
  position: sticky;
  top: 0;
  background: $color-bg;
  z-index: 100;
}

.nav-logo {
  font-weight: 700;
  font-size: 1.1rem;
  text-decoration: none;
  color: inherit;
}

.nav-actions {
  display: flex;
  gap: $space-sm;
}

.nav-add {
  @include button-variant($color-primary, $color-primary-dark);
  font-size: 0.9rem;
  text-decoration: none;
  padding: 0.4rem 1rem;
}

.main-content {
  max-width: 860px;
  margin: 0 auto;
  padding: $space-xl $space-lg;
}
</style>