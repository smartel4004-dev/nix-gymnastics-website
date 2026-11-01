/* NIX Gymnastics — site interactions (vanilla, no dependencies) */
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Header shadow on scroll ---------- */
  var header = document.querySelector(".site-header");
  var onScroll = function () {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 8);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu (dialog pattern with focus trap) ---------- */
  var menu = document.getElementById("menu");
  var openBtn = document.querySelector("[data-menu-open]");
  var closeBtn = document.querySelector("[data-menu-close]");
  function focusables() {
    return menu.querySelectorAll('a[href], button:not([disabled])');
  }
  function openMenu() {
    menu.classList.add("is-open");
    menu.removeAttribute("inert");
    menu.setAttribute("aria-hidden", "false");
    openBtn.setAttribute("aria-expanded", "true");
    document.body.classList.add("menu-open");
    setTimeout(function () { closeBtn.focus(); }, 30);
  }
  function closeMenu(returnFocus) {
    menu.classList.remove("is-open");
    menu.setAttribute("inert", "");
    menu.setAttribute("aria-hidden", "true");
    openBtn.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-open");
    if (returnFocus !== false) openBtn.focus();
  }
  if (menu && openBtn && closeBtn) {
    openBtn.addEventListener("click", openMenu);
    closeBtn.addEventListener("click", function () { closeMenu(); });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeMenu(false);
    });
    document.addEventListener("keydown", function (e) {
      if (!menu.classList.contains("is-open")) return;
      if (e.key === "Escape") closeMenu();
      if (e.key === "Tab") {
        var f = focusables(), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    window.matchMedia("(min-width: 961px)").addEventListener("change", function (mq) {
      if (mq.matches && menu.classList.contains("is-open")) closeMenu(false);
    });
  }

  /* ---------- Hero speed line (desktop) ----------
     A 10px band parallel to the photo's angled left edge. Its top and bottom
     ends are cut parallel to the hero's sloped bottom edge, and the bottom end
     sits ~30px below that edge. Geometry mirrors the CSS clip-paths:
     photo edge runs (left + 22% width, top) -> (left, bottom);
     hero bottom runs (0, H) -> (W, H - cut), cut = clamp(36px, 6vw, 110px). */
  var heroLine = document.querySelector("[data-hero-line]");
  if (heroLine) {
    var wrap = heroLine.parentElement;
    var heroSec = wrap.querySelector(".hero");
    var media = wrap.querySelector(".hero-media");
    var poly = heroLine.querySelector("polygon");
    var GAP = 22, THICK = 10, BELOW = 30, START = 0.5;
    function drawHeroLine() {
      if (getComputedStyle(heroLine).display === "none") return;
      var W = heroSec.offsetWidth, H = heroSec.offsetHeight;
      var L = media.offsetLeft, Wm = media.offsetWidth;
      var cut = Math.min(110, Math.max(36, 0.06 * window.innerWidth));
      var slope = cut / W;
      // x of a side of the band at height y (k = 0 right side, 1 left side)
      function sideX(y, k) { return L + 0.22 * Wm * (1 - y / H) - GAP - k * THICK; }
      // intersect a side with a line parallel to the hero bottom: y = base - slope * x
      function meet(base, k) {
        var y = base - slope * sideX(base, k);
        for (var i = 0; i < 3; i++) y = base - slope * sideX(y, k);
        return [sideX(y, k), y];
      }
      var topBase = START * H + slope * sideX(START * H, 0);
      var botBase = H + BELOW;
      var pts = [meet(topBase, 1), meet(topBase, 0), meet(botBase, 0), meet(botBase, 1)];
      heroLine.setAttribute("viewBox", "0 0 " + W + " " + H);
      poly.setAttribute("points", pts.map(function (p) { return p[0].toFixed(1) + "," + p[1].toFixed(1); }).join(" "));
    }
    drawHeroLine();
    window.addEventListener("resize", drawHeroLine, { passive: true });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawHeroLine);
  }

  /* ---------- Mobile action bar: appears once the hero is out of view ---------- */
  var bar = document.querySelector(".mobile-bar");
  var heroEl = document.querySelector("[data-hero]");
  if (bar) {
    document.body.classList.add("has-mobile-bar");
    if (heroEl && "IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        bar.classList.toggle("is-visible", !entries[0].isIntersecting);
      }, { rootMargin: "-40% 0px 0px 0px" }).observe(heroEl);
    } else {
      bar.classList.add("is-visible");
    }
  }

  /* ---------- Main nav dropdowns ----------
     Hover opens them for mouse users (CSS). The chevron button is the keyboard/touch control. */
  var subnavs = document.querySelectorAll("[data-subnav]");
  function closeSub(item, refocus) {
    if (!item.classList.contains("is-open")) return;
    item.classList.remove("is-open");
    var t = item.querySelector(".sub-toggle");
    t.setAttribute("aria-expanded", "false");
    if (refocus) t.focus();
  }
  subnavs.forEach(function (item) {
    var toggle = item.querySelector(".sub-toggle");
    toggle.addEventListener("click", function () {
      var open = !item.classList.contains("is-open");
      subnavs.forEach(function (other) { if (other !== item) closeSub(other); });
      item.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      if (open) item.querySelector(".sub a").focus();
    });
    item.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeSub(item, true);
    });
    item.querySelectorAll(".sub a").forEach(function (a) {
      a.addEventListener("click", function () { closeSub(item); a.blur(); });
    });
    item.addEventListener("focusout", function (e) {
      if (!item.contains(e.relatedTarget)) closeSub(item);
    });
  });
  document.addEventListener("click", function (e) {
    subnavs.forEach(function (item) { if (!item.contains(e.target)) closeSub(item); });
  });

  /* ---------- Scroll reveals ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if (!reduceMotion && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- Program finder (home) ---------- */
  var finder = document.querySelector("[data-finder]");
  if (finder) {
    var segs = finder.querySelectorAll(".seg");
    var rows = finder.querySelectorAll(".program-row");
    var status = finder.querySelector(".finder-status");
    var labels = { all: "", u4: "under 4", "4-5": "ages 4–5", "6-8": "ages 6–8", "9-12": "ages 9–12", "13": "ages 13 and up" };
    segs.forEach(function (seg) {
      seg.addEventListener("click", function () {
        var age = seg.getAttribute("data-age");
        segs.forEach(function (s) { s.setAttribute("aria-pressed", String(s === seg)); });
        var count = 0;
        rows.forEach(function (row) {
          var match = age === "all" || row.getAttribute("data-ages").split(" ").indexOf(age) > -1;
          row.hidden = !match;
          if (match) count++;
        });
        status.textContent = age === "all"
          ? "Showing all " + count + " programs."
          : count + (count === 1 ? " program fits " : " programs fit ") + labels[age] + ".";
      });
    });

    /* Hover preview image — fine pointers only */
    var preview = finder.querySelector(".finder-preview");
    var list = finder.querySelector(".program-list");
    if (preview && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
      var img = preview.querySelector("img");
      rows.forEach(function (row) {
        var src = row.getAttribute("data-preview");
        if (!src) return;
        var a = row.querySelector("a");
        a.addEventListener("mouseenter", function () {
          img.src = src;
          var y = row.offsetTop + row.offsetHeight / 2 - preview.offsetHeight / 2;
          preview.style.transform = "translateY(" + Math.max(-40, y) + "px) rotate(-2deg)";
          preview.classList.add("is-on");
        });
        a.addEventListener("mouseleave", function () { preview.classList.remove("is-on"); });
      });
      list.addEventListener("mouseleave", function () { preview.classList.remove("is-on"); });
    }
  }

  /* ---------- Programs page: scroll-spy index ---------- */
  var index = document.querySelector("[data-spy]");
  if (index && "IntersectionObserver" in window) {
    var links = index.querySelectorAll("a[href^='#']");
    var map = {};
    links.forEach(function (l) { map[l.getAttribute("href").slice(1)] = l; });
    if (links[0]) links[0].classList.add("is-active");
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        links.forEach(function (l) { l.classList.remove("is-active"); l.removeAttribute("aria-current"); });
        var link = map[en.target.id];
        if (link) {
          link.classList.add("is-active");
          link.setAttribute("aria-current", "true");
          // keep the active tab visible in the horizontal (mobile) index
          var ol = link.closest("ol");
          if (ol && ol.scrollWidth > ol.clientWidth) {
            ol.scrollTo({ left: link.offsetLeft - 24, behavior: reduceMotion ? "auto" : "smooth" });
          }
        }
      });
    }, { rootMargin: "-35% 0px -60% 0px" });
    document.querySelectorAll(".program[id]").forEach(function (s) { spy.observe(s); });
  }

  /* ---------- Inquiry / free-trial form ---------- */
  var form = document.querySelector("[data-inquiry]");
  if (form) {
    var params = new URLSearchParams(window.location.search);
    var typeInputs = form.querySelectorAll("input[name='type']");
    var programSel = form.querySelector("#program");
    var ageField = form.querySelector("[data-cond='age']");
    var dateField = form.querySelector("[data-cond='party']");
    var programField = form.querySelector("[data-cond='program']");
    var heading = document.querySelector("[data-form-heading]");
    var submitLabel = form.querySelector("[data-submit-label]");
    var copy = {
      trial: ["Book a free trial class", "Request my free trial"],
      team: ["Request a team evaluation", "Request an evaluation"],
      party: ["Plan a birthday party", "Check party dates"],
      question: ["Ask us anything", "Send my question"]
    };

    function currentType() {
      var c = form.querySelector("input[name='type']:checked");
      return c ? c.value : "trial";
    }
    function syncType() {
      var t = currentType();
      ageField.hidden = t === "question";
      programField.hidden = t === "party" || t === "team";
      dateField.hidden = t !== "party";
      form.querySelector("#age").required = t === "trial" || t === "team";
      ageField.querySelector(".req").hidden = !(t === "trial" || t === "team");
      ageField.querySelector(".opt").hidden = (t === "trial" || t === "team");
      if (heading) heading.textContent = copy[t][0];
      if (submitLabel) submitLabel.textContent = copy[t][1];
    }

    // Prefill from links like contact.html?type=team or ?program=tumbling
    var pType = params.get("type");
    if (pType && copy[pType]) {
      var radio = form.querySelector("input[name='type'][value='" + pType + "']");
      if (radio) radio.checked = true;
    }
    var pProg = params.get("program");
    if (pProg && programSel.querySelector("option[value='" + pProg + "']")) programSel.value = pProg;
    typeInputs.forEach(function (i) { i.addEventListener("change", syncType); });
    syncType();

    var messages = {
      parent: "Enter your name so we know who to reply to.",
      email: "Enter an email address like name@example.com.",
      phone: "Enter a phone number with area code, or leave it blank.",
      age: "Choose your child's age so we can suggest the right class."
    };
    function validateField(input) {
      var field = input.closest(".field");
      if (!field || field.hidden || (field.closest(".cond") && field.closest(".cond").hidden)) return true;
      var v = input.value.trim();
      var ok = true;
      if (input.required && !v) ok = false;
      if (ok && v && input.type === "email") ok = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
      if (ok && v && input.type === "tel") ok = v.replace(/\D/g, "").length >= 10;
      field.classList.toggle("has-error", !ok);
      input.setAttribute("aria-invalid", String(!ok));
      return ok;
    }
    form.querySelectorAll(".input, .select").forEach(function (input) {
      input.addEventListener("blur", function () { if (input.value.trim() || input.getAttribute("aria-invalid")) validateField(input); });
      input.addEventListener("input", function () { if (input.getAttribute("aria-invalid") === "true") validateField(input); });
    });

    var summary = form.querySelector(".error-summary");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var bad = [];
      form.querySelectorAll(".input, .select").forEach(function (input) {
        if (!validateField(input)) bad.push(input);
      });
      if (bad.length) {
        var ul = summary.querySelector("ul");
        ul.innerHTML = "";
        bad.forEach(function (input) {
          var li = document.createElement("li");
          var a = document.createElement("a");
          a.href = "#" + input.id;
          a.textContent = messages[input.name] || "Check this field.";
          a.addEventListener("click", function (ev) { ev.preventDefault(); input.focus(); });
          li.appendChild(a);
          ul.appendChild(li);
        });
        summary.hidden = false;
        summary.focus();
        return;
      }
      summary.hidden = true;
      var btn = form.querySelector("[type='submit']");
      btn.setAttribute("aria-busy", "true");
      submitLabel.textContent = "Sending…";

      /* Demo submission. Connect to your form service (Formspree, Netlify Forms,
         Jotform, or the gym's email handler) by setting the form's action and
         replacing this timeout with fetch(form.action, { method: "POST", body: new FormData(form) }). */
      setTimeout(function () {
        var name = form.querySelector("#parent").value.trim().split(" ")[0];
        var success = document.querySelector("[data-form-success]");
        success.querySelector("[data-success-name]").textContent = name ? ", " + name : "";
        form.hidden = true;
        success.hidden = false;
        success.focus();
      }, 700);
    });
  }

  /* ---------- Team meets ----------
     The build splits meets into upcoming and past using the build date.
     Re-check against today so a stale build never lists a finished meet as upcoming. */
  var DAY = 864e5;
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  function day(iso) { var p = iso.split("-"); return new Date(+p[0], p[1] - 1, +p[2]); }
  function isPast(li) { return day(li.dataset.end) < today; }
  function countdown(li) {
    var d = Math.round((day(li.dataset.start) - today) / DAY);
    if (d < 0) return "Happening now";
    if (d === 0) return "Today";
    if (d === 1) return "Tomorrow";
    return "In " + d + " days";
  }

  var meets = document.querySelector("[data-meets]");
  if (meets) {
    var upcoming = meets.querySelector("[data-meets-upcoming]");
    var pastList = meets.querySelector("[data-meets-past]");
    var status = meets.querySelector("[data-meets-status]");
    var filters = meets.querySelectorAll("[data-squad-filter]");

    var moved = 0;
    upcoming.querySelectorAll(".meet").forEach(function (li) {
      if (isPast(li)) { pastList.insertBefore(li, pastList.firstChild); moved++; }
    });
    var pastCount = pastList.children.length;
    if (moved) meets.querySelector("[data-past-label]").textContent = pastCount + " meets";
    var pastWrap = meets.querySelector("[data-meets-past-wrap]");
    if (!pastCount) pastWrap.hidden = true;

    function applyFilter(squad) {
      var shown = 0, next = null;
      upcoming.querySelectorAll(".meet-month").forEach(function (group) {
        var visible = 0;
        group.querySelectorAll(".meet").forEach(function (li) {
          var match = squad === "all" || li.dataset.squad === squad;
          li.hidden = !match;
          li.classList.remove("is-next");
          var tag = li.querySelector(".meet-next");
          if (tag) tag.remove();
          if (match) { visible++; if (!next) next = li; }
        });
        group.hidden = visible === 0;
        shown += visible;
      });
      if (next) {
        next.classList.add("is-next");
        var label = document.createElement("p");
        label.className = "meet-next";
        label.textContent = "Next meet · " + countdown(next);
        next.insertBefore(label, next.firstChild);
      }
      var total = upcoming.querySelectorAll(".meet").length;
      meets.querySelector("[data-meets-empty]").hidden = total > 0;
      if (squad === "all") {
        status.textContent = total ? total + (total === 1 ? " upcoming meet" : " upcoming meets") : "";
      } else {
        var who = squad === "boys" ? "boys' team" : "girls' team";
        status.textContent = shown
          ? shown + (shown === 1 ? " upcoming meet" : " upcoming meets") + " for the " + who
          : "No upcoming meets for the " + who + " yet.";
      }
    }

    filters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        filters.forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        applyFilter(btn.dataset.squadFilter);
      });
    });
    applyFilter("all");
  }

  /* ---------- Photo gallery index: filter by season and team, kept in the URL ---------- */
  var gIndex = document.querySelector("[data-galleries]");
  if (gIndex) {
    var gCards = gIndex.querySelectorAll(".gcard");
    var gStatus = gIndex.querySelector("[data-gallery-status]");
    var params = new URLSearchParams(location.search);
    var gState = { season: params.get("season") || "all", squad: params.get("squad") || "all" };

    function applyGalleries(updateUrl) {
      var shown = 0;
      gCards.forEach(function (card) {
        var ok = (gState.season === "all" || card.dataset.season === gState.season) &&
                 (gState.squad === "all" || card.dataset.squad === gState.squad || card.dataset.squad === "all");
        card.hidden = !ok;
        if (ok) shown++;
      });
      gIndex.querySelectorAll("[data-gfilter]").forEach(function (b) {
        b.setAttribute("aria-pressed", String(gState[b.dataset.gfilter] === b.dataset.value));
      });
      gIndex.querySelector("[data-gallery-empty]").hidden = shown > 0;
      gStatus.textContent = shown + (shown === 1 ? " gallery" : " galleries");
      if (updateUrl) {
        var q = new URLSearchParams();
        if (gState.season !== "all") q.set("season", gState.season);
        if (gState.squad !== "all") q.set("squad", gState.squad);
        history.replaceState(null, "", location.pathname + (q.toString() ? "?" + q : ""));
      }
    }
    gIndex.querySelectorAll("[data-gfilter]").forEach(function (b) {
      b.addEventListener("click", function () {
        gState[b.dataset.gfilter] = b.dataset.value;
        applyGalleries(true);
      });
    });
    applyGalleries(false);
  }

  // Team page preview: the next three meets that haven't finished.
  var teaser = document.querySelector("[data-meets-teaser-list]");
  if (teaser) {
    var kept = 0;
    Array.prototype.slice.call(teaser.children).forEach(function (li) {
      if (isPast(li) || kept >= 3) li.remove();
      else kept++;
    });
    if (!kept) {
      teaser.hidden = true;
      document.querySelector("[data-meets-teaser-empty]").hidden = false;
    }
  }
})();
