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

// Cover the first home paint while the capture scene is loading.
if (location.pathname === '/' && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  try {
    if (!localStorage.getItem('pokeshop.capture.v1')) {
      document.documentElement.dataset.captureBoot = ''
      setTimeout(() => {
        delete document.documentElement.dataset.captureBoot
      }, 5000)
    }
  } catch {
    /* The home view can still play the intro with restricted storage. */
  }
}
