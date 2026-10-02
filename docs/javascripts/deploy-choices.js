// Deploy choices: a card with a row of pills per choice (x-daemonless.choices)
// and one block of files per combination under it. Clicking a pill shows the
// block whose key matches every row's pick. Podman and AppJail carry the
// same form, so a pick in one is a pick in the other, and the picks are
// remembered per app in localStorage.
(function () {
  const store = (app) => "deploy-choices:" + app;
  const read = (app) => { try { return JSON.parse(localStorage.getItem(store(app)) || "{}"); } catch (e) { return {}; } };
  const write = (app, picks) => { try { localStorage.setItem(store(app), JSON.stringify(picks)); } catch (e) { /* private window */ } };

  function picksFor(form, saved) {
    const picks = {};
    form.querySelectorAll(".opts").forEach((row) => {
      const choice = row.dataset.choice;
      const ids = Array.from(row.querySelectorAll("button")).map((b) => b.dataset.option);
      const def = row.querySelector("button[data-default]");
      picks[choice] = ids.includes(saved[choice]) ? saved[choice] : (def ? def.dataset.option : ids[0]);
    });
    return picks;
  }

  function apply(form, picks) {
    form.querySelectorAll(".opts").forEach((row) => {
      row.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.option === picks[row.dataset.choice])));
    });
    const key = Array.from(form.querySelectorAll(".opts")).map((row) => row.dataset.choice + "=" + picks[row.dataset.choice]).join(";");
    let el = form.nextElementSibling;
    while (el && el.classList.contains("deploy-combo")) {
      el.hidden = el.dataset.key !== key;
      el = el.nextElementSibling;
    }
  }

  function init() {
    const forms = Array.from(document.querySelectorAll(".deploy-choices"));
    if (!forms.length) return;
    const byApp = {};
    forms.forEach((f) => (byApp[f.dataset.app] = byApp[f.dataset.app] || []).push(f));
    Object.keys(byApp).forEach((app) => {
      const group = byApp[app];
      let picks = picksFor(group[0], read(app));
      group.forEach((f) => apply(f, picks));
      group.forEach((f) => f.addEventListener("click", (e) => {
        const b = e.target.closest("button[data-option]");
        if (!b || !f.contains(b)) return;
        picks = Object.assign({}, picks, { [b.closest(".opts").dataset.choice]: b.dataset.option });
        write(app, picks);
        group.forEach((g) => apply(g, picks));
      }));
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
