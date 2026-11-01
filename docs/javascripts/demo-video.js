// An image page's demo (.daemonless/demo/) comes in a dark and a light take,
// frame for frame the same (from fjord.daemonless.io).
// Only the one matching the page's scheme is shown and plays; switching the
// scheme hands over at the same second instead of starting over. Off screen,
// nothing plays. With reduced motion asked for, or autoplay refused, it shows
// its controls and waits for the viewer rather than sitting on a still frame.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

  function setup() {
    var box = document.querySelector('.dl-demo');
    if (!box || box.dataset.ready) return;
    box.dataset.ready = '1';
    var dark = box.querySelector('.dl-demo-dark');
    var light = box.querySelector('.dl-demo-light');
    var inView = true;
    var manual = false; // the viewer drives it (reduced motion / no autoplay)

    function scheme() {
      return document.body.getAttribute('data-md-color-scheme') === 'slate' ? dark : light;
    }
    function play(v) {
      var p = v.play();
      if (p && p.catch) p.catch(function (e) {
        // NotAllowedError: autoplay refused. An AbortError is only our own
        // pause() (scrolled away, scheme switched) cutting in, not a refusal.
        if (e && e.name === 'NotAllowedError') { manual = true; dark.controls = light.controls = true; }
      });
    }
    function sync(from) {
      var to = scheme();
      var wasPlaying = !!from && !from.paused;
      if (from && from !== to && from.readyState > 0) {
        // The hidden take may not have its metadata yet; a seek before that
        // is dropped and it would start over.
        var at = from.currentTime;
        var seek = function () { try { to.currentTime = at; } catch (e) {} };
        if (to.readyState > 0) seek();
        else to.addEventListener('loadedmetadata', seek, { once: true });
      }
      [dark, light].forEach(function (v) { if (v !== to) v.pause(); });
      manual = manual || reduce.matches;
      dark.controls = light.controls = manual;
      if (manual) {
        if (wasPlaying) play(to); // a theme switch keeps what the viewer started
      } else if (inView) {
        play(to);
      } else {
        to.pause();
      }
    }

    new MutationObserver(function () {
      sync(scheme() === dark ? light : dark);
    }).observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        inView = es[0].isIntersecting;
        if (!manual) sync();
      }, { threshold: 0.2 }).observe(box);
    }
    if (reduce.addEventListener) reduce.addEventListener('change', function () { sync(); });
    sync();
  }

  // Instant navigation swaps the page without a load event.
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(setup);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup);
  else setup();
})();
