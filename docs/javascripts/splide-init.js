(function () {
  function initSplide() {
    if (typeof Splide === 'undefined') return;
    document.querySelectorAll('.screenshot-carousel:not(.is-initialized)').forEach(function (el) {
      var slides = el.querySelectorAll('.splide__slide').length;
      var multi = slides > 1;
      new Splide(el, {
        type: multi ? 'loop' : 'slide',
        padding: multi ? '10%' : 0,
        gap: '1rem',
        arrows: multi,
        pagination: multi,
        autoplay: el.dataset.autoplay === 'true' && multi,
        interval: 3000,
        pauseOnHover: true,
      }).mount();
      el.querySelectorAll('.splide__slide--clone a.glightbox').forEach(function (cloneLink) {
        cloneLink.addEventListener('click', function (ev) {
          var href = cloneLink.getAttribute('href');
          var orig = Array.prototype.find.call(
            el.querySelectorAll('.splide__slide:not(.splide__slide--clone) a.glightbox'),
            function (a) { return a.getAttribute('href') === href; }
          );
          if (orig) {
            ev.preventDefault();
            orig.click();
          }
        });
      });
    });
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(initSplide);
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSplide);
  } else {
    initSplide();
  }
})();
