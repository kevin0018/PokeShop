// Apply the saved/system theme before CSS loads, avoiding a light flash.
;(() => {
  let theme = 'system'
  try {
    theme = localStorage.getItem('pokeshop.theme') || 'system'
  } catch {
    /* Restricted storage. */
  }
  document.documentElement.dataset.theme =
    theme === 'light' || theme === 'dark'
      ? theme
      : window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
})()
