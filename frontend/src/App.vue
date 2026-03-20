<template>
  <div id="app">
    <header class="nav">
      <RouterLink to="/" class="nav-logo">🗄️ Recipe Vault</RouterLink>
      <RouterLink to="/add" class="nav-add">+ Add Recipe</RouterLink>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  height: 56px;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  background: white;
  z-index: 100;
}

.nav-logo {
  font-weight: 700;
  font-size: 1.1rem;
  text-decoration: none;
  color: inherit;
}

.nav-add {
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  background: #16a34a;
  color: white;
  padding: 0.4rem 1rem;
  border-radius: 6px;
}

.nav-add:hover {
  background: #15803d;
}

.main-content {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}
</style>