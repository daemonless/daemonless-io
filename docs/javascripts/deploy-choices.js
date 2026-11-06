// Deploy choices: a card with a row of pills per choice (x-daemonless.choices)
// and the files under it. Podman and AppJail carry the same form, so a pick in
// one is a pick in the other, and the picks are remembered per app in
// localStorage.
//
// The files come one of two ways (dbuild's README.mkdocs.j2):
// - a block per combination (.deploy-combo[data-key]): the one whose key
//   matches every row's pick is shown;
// - one merged block (.deploy-merged) whose varying lines carry the picks that
//   keep them (data-when, from dbuild/choice_merge.py): the lines the picks
//   keep are shown, in the code blocks too, so copy and the zip download take
//   exactly those. A combination the merge cannot express follows it as a
//   .deploy-combo and is shown in its place.
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
    // A choice that only keeps a part or drops it is one switch (.toggle).
    form.querySelectorAll("button.toggle").forEach((t) => {
      const c = t.dataset.choice;
      picks[c] = [t.dataset.on, t.dataset.off].includes(saved[c]) ? saved[c] : t.dataset.on;
    });
    return picks;
  }

  // The choices in the order the page lists them, for the combination key.
  const choiceIds = (form) => Array.from(form.querySelectorAll(".opts, button.toggle")).map((el) => el.dataset.choice);

  // Which superset lines the picks show: choice_merge.visible, line for line.
  // lines[k] = [cond id or "", separator?, blank?].
  function visible(data, picks) {
    const L = data.lines;
    const kept = (c) => !c || Object.entries(data.conds[c]).every(([ch, opts]) => opts.includes(picks[ch]));
    const base = L.map(([c, s]) => !s && kept(c));
    const side = (k, step) => {
      let saw = false;
      for (let j = k + step; j >= 0 && j < L.length; j += step) {
        const [c, s, b] = L[j];
        if (s || b) continue;
        if (!c) return !saw;
        saw = true;
        if (base[j]) return true;
      }
      return false;
    };
    const out = L.map(([, s], k) => base[k] || (!!s && side(k, -1) && side(k, 1)));
    let lastBlank = true;
    L.forEach(([, s, b], k) => {
      if (!out[k]) return;
      if (s && lastBlank) { out[k] = false; return; }
      lastBlank = !!b;
    });
    return out;
  }

  // A highlighted block's lines, as Pygments writes them: each starts at its
  // <a id="__codelineno-…"> anchor. Lines a pick drops wait in a hidden holder
  // inside the block, still in the page, so the placeholder settings keep
  // reaching them.
  function lineGroups(hl) {
    if (hl._groups) return hl._groups;
    const code = hl.querySelector("code");
    const nums = hl.querySelector(".linenodiv pre");
    if (!code) return null;
    const head = [], groups = [];
    Array.from(code.childNodes).forEach((n) => {
      if (n.nodeType === 1 && n.matches("a[id^='__codelineno-']")) groups.push([]);
      (groups.length ? groups[groups.length - 1] : head).push(n);
    });
    const numbers = [];
    if (nums) {
      Array.from(nums.childNodes).forEach((n) => {
        if (n.nodeType === 1 && n.classList.contains("normal")) numbers.push([n]);
        else if (numbers.length) numbers[numbers.length - 1].push(n);
      });
    }
    const holder = document.createElement("div");
    holder.hidden = true;
    holder.className = "merged-holder";
    hl.appendChild(holder);
    hl._groups = { code, nums, head, groups, numbers, holder };
    return hl._groups;
  }

  function showLines(hl, mask) {
    const g = lineGroups(hl);
    if (!g || g.groups.length !== mask.length) {
      console.warn("deploy-choices: line count differs", hl, g && g.groups.length, mask.length);
      return false;
    }
    g.code.append(...g.head);
    let n = 0;
    g.groups.forEach((nodes, i) => {
      (mask[i] ? g.code : g.holder).append(...nodes);
      if (mask[i]) n++;
    });
    if (g.nums) g.numbers.forEach((nodes, i) => (i < n ? g.nums : g.holder).append(...nodes));
    return true;
  }

  // "a · b — data in x, y": the separators follow what is shown.
  function separators(p) {
    const shown = (sel) => Array.from(p.querySelectorAll(sel)).filter((el) => !el.closest("[hidden]"));
    shown(".yg").forEach((el, i) => el.classList.toggle("sep", i > 0));
    shown(".yf").forEach((el, i) => { el.classList.toggle("first", i === 0); el.classList.toggle("sep", i > 0); });
  }

  function applyMerged(box, picks) {
    if (!box._when) {
      box._when = JSON.parse(box.dataset.when);
      // Between the items, only the separators the script puts there.
      box.querySelectorAll(".you-get").forEach((p) => {
        Array.from(p.childNodes).forEach((n) => { if (n.nodeType === 3 && !n.textContent.trim()) n.remove(); });
      });
    }
    const data = box._when;
    const vis = visible(data, picks);
    box.querySelectorAll("span[data-l]").forEach((el) => { el.hidden = !vis[+el.dataset.l]; });
    let ok = true;
    box.querySelectorAll(".highlight[data-wb]").forEach((hl) => {
      hl.hidden = !vis[+hl.dataset.l];
      const idx = data.blocks[hl.dataset.wb] || [];
      const mask = idx.map((k) => vis[k]);
      // A file starts and ends at text, as the highlighter renders one: a
      // blank line left first or last by what the picks hide goes too
      // (choice_merge._norm proves it so).
      const blank = (i) => data.lines[idx[i]][2];
      for (let i = 0; i < mask.length && (!mask[i] || blank(i)); i++) mask[i] = false;
      for (let i = mask.length - 1; i >= 0 && (!mask[i] || blank(i)); i--) mask[i] = false;
      ok = showLines(hl, mask) && ok;
    });
    box.querySelectorAll(".you-get").forEach(separators);
    return ok;
  }

  function apply(form, picks) {
    form.querySelectorAll(".opts").forEach((row) => {
      row.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.option === picks[row.dataset.choice])));
    });
    form.querySelectorAll("button.toggle").forEach((t) => t.setAttribute("aria-pressed", String(picks[t.dataset.choice] === t.dataset.on)));
    const order = form.dataset.order ? form.dataset.order.split(" ") : choiceIds(form);
    const key = order.map((c) => c + "=" + picks[c]).join(";");
    let merged = null, whole = null;
    for (let el = form.nextElementSibling; el && (el.classList.contains("deploy-combo") || el.classList.contains("deploy-merged")); el = el.nextElementSibling) {
      if (el.classList.contains("deploy-merged")) { merged = el; continue; }
      el.hidden = el.dataset.key !== key;
      if (!el.hidden) whole = el;
    }
    if (merged) {
      merged.hidden = !!whole;
      if (!whole) applyMerged(merged, picks);
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
        const b = e.target.closest("button[data-option], button.toggle, button[data-toggle-all]");
        if (!b || !f.contains(b)) return;
        picks = Object.assign({}, picks);
        if (b.dataset.option) picks[b.closest(".opts").dataset.choice] = b.dataset.option;
        else if (b.classList.contains("toggle")) picks[b.dataset.choice] = picks[b.dataset.choice] === b.dataset.on ? b.dataset.off : b.dataset.on;
        else f.querySelectorAll("button.toggle").forEach((t) => { picks[t.dataset.choice] = t.dataset[b.dataset.toggleAll]; });
        write(app, picks);
        group.forEach((g) => apply(g, picks));
      }));
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
