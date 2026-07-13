(function () {
  'use strict';
  class AdminLayout {
    constructor() {
      this.sidebar = document.getElementById('sidebar');
      this.overlay = document.getElementById('sidebarOverlay');
      this.toggleBtn = document.getElementById('sidebarToggle');
      this.closeBtn = document.getElementById('sidebarClose');
      this.filterInput = document.getElementById('menuFilter');
      this._init();
    }
    _init() {
      this._bindSidebarToggle();
      this._bindModuleToggle();
      this._bindFilter();
      this._highlightActive();
      this._openCurrentModule();
    }
    _bindSidebarToggle() {
      this.toggleBtn?.addEventListener('click', () => this.sidebar?.classList.add('open') || this.overlay?.classList.add('active'));
      this.closeBtn?.addEventListener('click', () => this._close());
      this.overlay?.addEventListener('click', () => this._close());
    }
    _close() { this.sidebar?.classList.remove('open'); this.overlay?.classList.remove('active'); }
    _bindModuleToggle() {
      document.querySelectorAll('.module-header').forEach(el => {
        el.addEventListener('click', (e) => {
          e.stopPropagation();
          const children = el.nextElementSibling;
          if (!children?.classList.contains('module-children')) return;
          children.classList.toggle('open');
          el.classList.toggle('open');
        });
      });
    }
    _bindFilter() {
      this.filterInput?.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase().trim();
        document.querySelectorAll('.sidebar-module').forEach(mod => {
          const name = mod.querySelector('.module-name')?.textContent?.toLowerCase() || '';
          const children = mod.querySelectorAll('.child-link');
          let match = name.includes(q);
          children.forEach(ch => {
            const text = ch.textContent.toLowerCase();
            ch.style.display = text.includes(q) || !q ? '' : 'none';
            if (text.includes(q) && q) match = true;
          });
          mod.style.display = match || !q ? '' : 'none';
        });
      });
    }
    _highlightActive() {
      const current = window.location.pathname;
      document.querySelectorAll('.child-link').forEach(link => {
        if (link.getAttribute('href') === current) link.classList.add('active');
      });
    }
    _openCurrentModule() {
      const active = document.querySelector('.child-link.active');
      if (!active) return;
      const children = active.closest('.module-children');
      const header = children?.previousElementSibling;
      if (children && header) { children.classList.add('open'); header.classList.add('open'); }
    }
  }
  document.addEventListener('DOMContentLoaded', () => { new AdminLayout(); });
})();