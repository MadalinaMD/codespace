<script setup>
// Editor CodeMirror 6 cu temă întunecată și suport Python.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState } from '@codemirror/state'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'

const props = defineProps({
  modelValue: { type: String, default: '' },
  readonly: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const container = ref(null)
let editor = null

onMounted(() => {
  editor = new EditorView({
    state: EditorState.create({
      doc: props.modelValue,
      extensions: [
        basicSetup,
        python(),
        oneDark,
        EditorState.readOnly.of(props.readonly),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) emit('update:modelValue', update.state.doc.toString())
        }),
      ],
    }),
    parent: container.value,
  })
})

onBeforeUnmount(() => { editor?.destroy(); editor = null })

// Sincronizare externă (ex: resetare la codul inițial)
watch(() => props.modelValue, (valoare) => {
  if (editor && valoare !== editor.state.doc.toString()) {
    editor.dispatch({ changes: { from: 0, to: editor.state.doc.length, insert: valoare } })
  }
})
</script>

<template>
  <div ref="container" class="cm-wrapper rounded-xl overflow-hidden border border-white/10"></div>
</template>
