/**
 * The page reader, run inside the page. Kept as plain JavaScript source so no compiler helpers
 * leak into it. Returns visible text and interactive elements, tagging each element with
 * data-vanaras-ref so later clicks find exactly what the model saw.
 *
 * Only what a person can see is returned: text hidden with display:none, visibility, opacity,
 * tiny fonts, clipping, aria-hidden or off-screen positioning is dropped, since that is where
 * prompt-injection attacks usually hide.
 */
export const READ_PAGE = String.raw`function (maxText) {
  function hidden(el) {
    for (var e = el; e; e = e.parentElement) {
      if (e.getAttribute && (e.getAttribute("aria-hidden") === "true" || e.hidden)) return true;
      var s = getComputedStyle(e);
      if (s.display === "none" || s.visibility === "hidden" || s.visibility === "collapse") return true;
      if (Number(s.opacity) < 0.1) return true;
      if (parseFloat(s.fontSize) < 4) return true;
      if (s.clipPath === "inset(100%)" || s.clip === "rect(0px, 0px, 0px, 0px)") return true;
    }
    var box = el.getBoundingClientRect();
    if (box.width < 2 || box.height < 2) return true;
    if (box.right < 0 || box.bottom < 0) return true;
    return false;
  }

  var lines = [], total = 0, cache = new Map();
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (var n = walker.nextNode(); n && total < maxText; n = walker.nextNode()) {
    var parent = n.parentElement;
    if (!parent || ["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"].indexOf(parent.tagName) >= 0) continue;
    var t = (n.textContent || "").replace(/\s+/g, " ").trim();
    if (!t) continue;
    var h = cache.get(parent);
    if (h === undefined) { h = hidden(parent); cache.set(parent, h); }
    if (h) continue;
    lines.push(t);
    total += t.length + 1;
  }
  var text = lines.join("\n").slice(0, maxText);

  document.querySelectorAll("[data-vanaras-ref]").forEach(function (e) { e.removeAttribute("data-vanaras-ref"); });
  var query = "a[href], button, input:not([type=hidden]), select, textarea, [role=button], [role=link], " +
    "[role=checkbox], [role=radio], [role=tab], [role=menuitem], [role=option], [contenteditable=true]";
  var elements = [], i = 0;
  document.querySelectorAll(query).forEach(function (el) {
    if (hidden(el)) return;
    var tag = el.tagName.toLowerCase();
    var type;
    if (tag === "input") type = el.type || "text";
    else if (tag === "button") type = el.type || "submit";
    // A submit button outside any form submits nothing: it's an ordinary button.
    if (type === "submit" && !el.form) type = "button";
    var role = el.getAttribute("role");
    if (!role) {
      if (tag === "a") role = "link";
      else if (tag === "select") role = "combobox";
      else if (tag === "textarea") role = "textbox";
      else if (tag === "button") role = "button";
      else if (tag === "input") {
        if (["submit", "button", "reset", "image"].indexOf(type) >= 0) role = "button";
        else if (type === "checkbox" || type === "radio") role = type;
        else role = "textbox";
      } else role = "generic";
    }
    var name = el.getAttribute("aria-label");
    if (!name && el.id) {
      var lab = document.querySelector('label[for="' + CSS.escape(el.id) + '"]');
      if (lab) name = lab.textContent;
    }
    if (!name && tag !== "a" && tag !== "button" && el.closest("label")) name = el.closest("label").textContent;
    if (!name && tag === "input" && role === "button") name = el.value;
    if (!name && tag === "input") name = el.placeholder || el.name;
    if (!name) name = el.getAttribute("title") || el.innerText || "";
    name = String(name).replace(/\s+/g, " ").trim().slice(0, 120);
    var ref = "e" + (++i);
    el.setAttribute("data-vanaras-ref", ref);
    var item = { ref: ref, role: role, name: name };
    if (type) item.type = type;
    var ac = el.getAttribute("autocomplete");
    if (ac) item.autocomplete = ac;
    if ((tag === "input" && role === "textbox") || tag === "textarea") item.value = el.value;
    if (tag === "select") {
      item.options = Array.prototype.map.call(el.options, function (o) { return o.label; }).slice(0, 50);
      item.value = el.selectedOptions[0] ? el.selectedOptions[0].label : undefined;
    }
    if (el.disabled) item.disabled = true;
    elements.push(item);
  });
  return { text: text, elements: elements };
}`;
