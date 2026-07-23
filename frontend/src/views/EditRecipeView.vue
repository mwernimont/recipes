<template>
  <div v-if="store.loading" class="state-msg">Loading…</div>
  <div v-else-if="store.error" class="state-msg error">{{ store.error }}</div>
  <RecipePreviewForm
    v-else-if="store.currentRecipe"
    :recipe="store.currentRecipe"
    :saving="saving"
    heading="Edit Recipe"
    submit-label="Save Changes"
    @save="handleSave"
    @back="handleBack"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRecipeStore } from '@/stores/recipes'
import RecipePreviewForm from '@/components/RecipePreviewForm.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const store = useRecipeStore()
const router = useRouter()
const saving = ref(false)

onMounted(() => store.fetchRecipe(props.id))

async function handleSave(recipeData) {
  saving.value = true
  try {
    await store.updateRecipe(props.id, recipeData)
    router.push(`/recipe/${props.id}`)
  } finally {
    saving.value = false
  }
}

function handleBack() {
  router.push(`/recipe/${props.id}`)
}
</script>

<style lang="scss" scoped>
.state-msg {
  @include state-message;
}
</style>
