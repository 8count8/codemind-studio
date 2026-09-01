const BLOCKED_TAGS = 'script,style,iframe,object,embed,link,meta,base,form,input,button,textarea,select'

/** Sanitize the HTML produced from Markdown before handing it to v-html. */
export function sanitizeHtml(html) {
  if (typeof document === 'undefined') {
    return String(html || '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
  }
  const template = document.createElement('template')
  template.innerHTML = String(html || '')
  template.content.querySelectorAll(BLOCKED_TAGS).forEach(node => node.remove())
  template.content.querySelectorAll('*').forEach(node => {
    for (const attr of [...node.attributes]) {
      const name = attr.name.toLowerCase()
      const value = attr.value.trim().toLowerCase().replace(/\s+/g, '')
      if (
        name.startsWith('on') ||
        name === 'srcdoc' ||
        ((name === 'href' || name === 'src' || name === 'xlink:href') &&
          (value.startsWith('javascript:') || value.startsWith('data:text/html')))
      ) {
        node.removeAttribute(attr.name)
      }
    }
  })
  return template.innerHTML
}
