(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Year
  const yearEl = $("[data-year]");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Theme
  const themeKey = "egorprotasov-theme";
  const root = document.documentElement;
  const getSystemTheme = () =>
    window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  const applyTheme = (t) => root.setAttribute("data-theme", t);

  applyTheme(localStorage.getItem(themeKey) || getSystemTheme());

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

    $$(".nav__link", menu).forEach((a) => a.addEventListener("click", closeMenu));

    document.addEventListener("click", (e) => {
      if (!menu.classList.contains("is-open")) return;
      const t = e.target;
      if (!menu.contains(t) && !toggleBtn.contains(t)) closeMenu();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeMenu();
    });
  }

  // Accordion: only one open
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

  // Copy
  const copyBtn = $("[data-copy]");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const text = copyBtn.getAttribute("data-copy") || "";
      try {
        await navigator.clipboard.writeText(text);
        toast("Email скопирован");
      } catch {
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
    toastTimer = setTimeout(() => toastEl.classList.remove("is-show"), 1800);
  }

  // Header shadow on scroll
  const onScroll = () => {
    if (!header) return;
    const y = window.scrollY || 0;
    header.style.boxShadow = y > 8 ? "0 10px 28px rgba(0,0,0,0.18)" : "none";
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Active nav link
  const navLinks = $$(".nav__link").filter((a) => a.getAttribute("href")?.startsWith("#"));
  const map = new Map(navLinks.map((a) => [a.getAttribute("href"), a]));
  const sections = ["#about", "#services", "#cases", "#process", "#faq", "#contact"]
    .map((id) => document.querySelector(id))
    .filter(Boolean);

  if ("IntersectionObserver" in window && sections.length) {
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (!visible) return;
        const id = "#" + visible.target.id;
        navLinks.forEach((a) => a.classList.remove("is-active"));
        const link = map.get(id);
        if (link) link.classList.add("is-active");
      },
      { threshold: [0.25, 0.5, 0.75] }
    );

    sections.forEach((s) => obs.observe(s));
  }
})();