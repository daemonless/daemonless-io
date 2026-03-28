function initSplide() {
  document.querySelectorAll('.screenshot-carousel:not(.is-initialized)').forEach(function (el) {
    new Splide(el, {
      type: 'loop',
      padding: '10%',
      gap: '1rem',
      arrows: true,
      pagination: true,
    }).mount();
  });
}

var _glightbox;

function initGlightbox() {
  if (_glightbox) { _glightbox.destroy(); }
  if (typeof GLightbox !== 'undefined') {
    _glightbox = GLightbox({ selector: '.glightbox' });
  }
}

// Scripts load at bottom of body in MkDocs — DOM is already ready, call directly.
initSplide();
initGlightbox();

// Hook into MkDocs Material instant navigation for subsequent page switches.
if (typeof document$ !== 'undefined') {
  document$.subscribe(function () { initSplide(); initGlightbox(); });
}
