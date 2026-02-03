(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Year
  const yearEl = $("[data-year]");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Theme: auto -> saved -> system
  const themeKey = "egorprotasov-theme";
  const root = document.documentElement;

  const getSystemTheme = () =>
    window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches
      ? "light"
      : "dark";

  const applyTheme = (t) => {
    root.setAttribute("data-theme", t);
  };

  const savedTheme = localStorage.getItem(themeKey);
  applyTheme(savedTheme || getSystemTheme());

  const themeBtn = $("[data-theme-toggle]");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(themeKey, next);
      toast(next === "dark" ? "Тёмная тема" : "Светлая тема");
    });
  }

  // Mobile nav
  const toggleBtn = $("[data-nav-toggle]");
  const menu = $("[data-nav-menu]");
  const header = $("[data-header]");

  const closeMenu = () => {
    if (!menu || !toggleBtn) return;
    menu.classList.remove("is-open");
    toggleBtn.setAttribute("aria-expanded", "false");
  };

  const openMenu = () => {
    if (!menu || !toggleBtn) return;
    menu.classList.add("is-open");
    toggleBtn.setAttribute("aria-expanded", "true");
  };

  if (toggleBtn && menu) {
    toggleBtn.addEventListener("click", () => {
      const isOpen = menu.classList.contains("is-open");
      isOpen ? closeMenu() : openMenu();
    });

    // Close on nav click
    $$(".nav__link", menu).forEach((a) => {
      a.addEventListener("click", () => closeMenu());
    });

    // Close on outside click
    document.addEventListener("click", (e) => {
      if (!menu.classList.contains("is-open")) return;
      const target = e.target;
      const insideMenu = menu.contains(target);
      const insideBtn = toggleBtn.contains(target);
      if (!insideMenu && !insideBtn) closeMenu();
    });

    // Close on ESC
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeMenu();
    });

    // Prevent sticky header overlap on anchor jumps: add top padding via scroll-margin in CSS? (not used)
    // Here keep it minimal.
  }

  // Accordion: only one open at a time
  const accRoot = $("[data-accordion]");
  if (accRoot) {
    const items = $$("details", accRoot);
    items.forEach((d) => {
      d.addEventListener("toggle", () => {
        if (!d.open) return;
        items.forEach((other) => {
          if (other !== d) other.open = false;
        });
      });
    });
  }

  // Copy-to-clipboard
  const copyBtn = $("[data-copy]");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const text = copyBtn.getAttribute("data-copy") || "";
      try {
        await navigator.clipboard.writeText(text);
        toast("Email скопирован");
      } catch {
        // fallback
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try {
          document.execCommand("copy");
          toast("Email скопирован");
        } catch {
          toast("Не удалось скопировать");
        }
        document.body.removeChild(ta);
      }
    });
  }

  // Toast
  const toastEl = $("[data-toast]");
  let toastTimer = null;

  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("is-show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastEl.classList.remove("is-show");
    }, 1800);
  }

  // Improve UX: add class when scrolled
  const onScroll = () => {
    if (!header) return;
    const y = window.scrollY || 0;
    header.style.boxShadow = y > 8 ? "0 10px 28px rgba(0,0,0,0.18)" : "none";
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
