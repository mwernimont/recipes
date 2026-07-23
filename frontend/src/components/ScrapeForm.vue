<template>
  <div class="scrape-form">
    <h1>Add a Recipe</h1>

    <div class="url-row">
      <input
        v-model="url"
        type="url"
        placeholder="Paste a recipe URL…"
        :disabled="loading"
        @keydown.enter="submit"
      />
      <button :disabled="!url.trim() || loading" @click="submit">
        {{ loading ? 'Scraping…' : 'Import' }}
      </button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div class="divider">or</div>

    <button class="manual-btn" :disabled="loading" @click="$emit('manual')">
      Enter Manually
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  loading: Boolean,
  error: String,
})

const emit = defineEmits(['scrape', 'manual'])
const url = ref('')

function submit() {
  if (url.value.trim()) emit('scrape', url.value.trim())
}
</script>
<style lang="scss" scoped>
.url-row {
  display: flex;
}
.url-row input {
  flex: 1;
  padding: 5px 10px;
}
</style>