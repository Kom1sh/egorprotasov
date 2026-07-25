(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Год в подвале
  const yearEl = $("[data-year]");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Тост
  const toastEl = $("[data-toast]");
  let toastTimer = null;
  const toast = (msg) => {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toastEl.classList.remove("show"), 2200);
  };

  // Высота шапки в переменную: герой считает от неё свою высоту, и без
  // уточнения по факту он не дотягивает до края экрана на несколько пикселей.
  const hdr = $(".hdr");
  if (hdr) {
    const syncHdr = () =>
      document.documentElement.style.setProperty(
        "--hdr",
        hdr.getBoundingClientRect().height + "px"
      );
    syncHdr();
    if ("ResizeObserver" in window) new ResizeObserver(syncHdr).observe(hdr);
    else window.addEventListener("resize", syncHdr, { passive: true });
  }

  // Мобильное меню
  const navBtn = $("[data-nav-toggle]");
  const nav = $("[data-nav]");
  if (navBtn && nav) {
    const close = () => {
      nav.classList.remove("open");
      navBtn.setAttribute("aria-expanded", "false");
    };

    navBtn.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      navBtn.setAttribute("aria-expanded", String(open));
    });

    $$("a", nav).forEach((a) => a.addEventListener("click", close));

    document.addEventListener("click", (e) => {
      if (!nav.classList.contains("open")) return;
      if (!nav.contains(e.target) && !navBtn.contains(e.target)) close();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  }

  // Копирование почты
  const copyBtn = $("[data-copy]");
  if (copyBtn) {
    copyBtn.addEventListener("click", async () => {
      const text = copyBtn.getAttribute("data-copy") || "";
      try {
        await navigator.clipboard.writeText(text);
        toast("Email скопирован");
      } catch (e) {
        // clipboard API недоступен без https или при отказе в правах
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.cssText = "position:fixed;left:-9999px";
        document.body.appendChild(ta);
        ta.select();
        try {
          document.execCommand("copy");
          toast("Email скопирован");
        } catch (err) {
          toast("Не удалось скопировать");
        }
        document.body.removeChild(ta);
      }
    });
  }
})();
