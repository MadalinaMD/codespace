<script setup>
import { computed } from 'vue'
import { randeazaMarkdown } from '@/lib/markdown'

const props = defineProps({ continut: { type: String, default: '' } })
const html = computed(() => randeazaMarkdown(props.continut))
</script>

<template>
  <div class="markdown" v-html="html"></div>
</template>
