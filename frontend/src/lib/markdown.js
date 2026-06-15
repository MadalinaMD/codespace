// Randarea Markdown: marked (parsare) + highlight.js (sintaxă) + DOMPurify (igienizare).
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import json from 'highlight.js/lib/languages/json'
import DOMPurify from 'dompurify'
import 'highlight.js/styles/github-dark.css'

hljs.registerLanguage('python', python)
hljs.registerLanguage('json', json)

marked.setOptions({
  highlight: undefined, // folosim walkTokens mai jos pentru control complet
  gfm: true,
  breaks: false,
})

const renderer = new marked.Renderer()
renderer.code = function ({ text, lang }) {
  const limbaj = lang && hljs.getLanguage(lang) ? lang : 'python'
  const evidentiat = hljs.highlight(text, { language: limbaj }).value
  return `<pre><code class="hljs language-${limbaj}">${evidentiat}</code></pre>`
}

export function randeazaMarkdown(text) {
  const html = marked.parse(text || '', { renderer })
  return DOMPurify.sanitize(html)
}
