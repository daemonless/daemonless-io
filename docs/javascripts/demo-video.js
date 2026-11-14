// Synchronized dark/light hero demo video controller.
// Plays only the video matching Zensical's active color scheme (`slate` vs `default`),
// preserves exact playback timestamp across theme toggles, pauses when scrolled
// off-screen, and falls back to native controls under `prefers-reduced-motion`
// or browser autoplay restrictions.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  function setupBox(box) {
    if (!box || box.dataset.ready) return;
    box.dataset.ready = '1';
    var dark = box.querySelector('.rp-demo-dark');
    var light = box.querySelector('.rp-demo-light');
    if (!dark || !light) return;

    var inView = true;
    var manual = false;

    function activeVideo() {
      return document.body.getAttribute('data-md-color-scheme') === 'slate' ? dark : light;
    }

    function play(v) {
      var p = v.play();
      if (p && p.catch) {
        p.catch(function (e) {
          if (e && e.name === 'NotAllowedError') {
            manual = true;
            dark.controls = light.controls = true;
          }
        });
      }
    }

    function sync(from) {
      var to = activeVideo();
      var wasPlaying = !!from && !from.paused;
      if (from && from !== to && from.readyState > 0) {
        var at = from.currentTime;
        var seek = function () {
          try { to.currentTime = at; } catch (e) {}
        };
        if (to.readyState > 0) seek();
        else to.addEventListener('loadedmetadata', seek, { once: true });
      }
      [dark, light].forEach(function (v) {
        if (v !== to) v.pause();
      });
      manual = manual || reduce.matches;
      dark.controls = light.controls = manual;
      if (manual) {
        if (wasPlaying) play(to);
      } else if (inView) {
        play(to);
      } else {
        to.pause();
      }
    }

    new MutationObserver(function () {
      sync(activeVideo() === dark ? light : dark);
    }).observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        if (!manual) sync();
      }, { threshold: 0.2 }).observe(box);
    }

    if (reduce.addEventListener) {
      reduce.addEventListener('change', function () { sync(); });
    }
    sync();
  }

  function setupAll() {
    document.querySelectorAll('.rp-demo').forEach(setupBox);
  }

  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(setupAll);
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAll);
  } else {
    setupAll();
  }
})();
