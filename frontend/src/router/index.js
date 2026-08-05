import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Library',
    component: () => import('@/views/LibraryView.vue'),
  },
  {
    path: '/recipe/:id',
    name: 'RecipeDetail',
    component: () => import('@/views/RecipeDetailView.vue'),
    props: true,
  },
  {
    path: '/recipe/:id/edit',
    name: 'EditRecipe',
    component: () => import('@/views/EditRecipeView.vue'),
    props: true,
  },
  {
    path: '/add',
    name: 'AddRecipe',
    component: () => import('@/views/AddRecipeView.vue'),
  },
  {
    path: '/meal-plan',
    name: 'MealPlan',
    component: () => import('@/views/MealPlanView.vue'),
  },
  {
    path: '/grocery-list',
    name: 'GroceryList',
    component: () => import('@/views/GroceryListView.vue'),
  },
  {
    path: '/archive',
    name: 'Archive',
    component: () => import('@/views/ArchiveView.vue'),
  },
  {
    path: '/archive/:id',
    name: 'ArchiveDetail',
    component: () => import('@/views/ArchiveDetailView.vue'),
    props: true,
  },
]

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition ?? { top: 0 }
  },
})