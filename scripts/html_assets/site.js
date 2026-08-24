(() => {
  const root = document.documentElement;
  const body = document.body;
  const themeButton = document.querySelector('.theme-toggle');
  const focusButton = document.querySelector('.focus-toggle');
  const navButton = document.querySelector('.nav-toggle');
  const navBackdrop = document.querySelector('.nav-backdrop');
  const progress = document.querySelector('.reading-progress span');

  const preferredTheme = localStorage.getItem('frontier-theme');
  if (preferredTheme === 'dark') root.dataset.theme = 'dark';
  if (!preferredTheme && matchMedia('(prefers-color-scheme: dark)').matches) root.dataset.theme = 'dark';
  const updateThemeState = () => {
    const dark = root.dataset.theme === 'dark';
    themeButton?.setAttribute('aria-pressed', String(dark));
    themeButton?.setAttribute('title', dark ? '切换到浅色主题' : '切换到深色主题');
  };
  updateThemeState();

  themeButton?.addEventListener('click', () => {
    const dark = root.dataset.theme !== 'dark';
    if (dark) root.dataset.theme = 'dark';
    else delete root.dataset.theme;
    localStorage.setItem('frontier-theme', dark ? 'dark' : 'light');
    updateThemeState();
  });

  focusButton?.addEventListener('click', () => {
    const active = body.classList.toggle('focus-mode');
    focusButton.setAttribute('aria-pressed', String(active));
  });

  const closeNav = () => {
    body.classList.remove('nav-open');
    navButton?.setAttribute('aria-expanded', 'false');
  };
  navButton?.addEventListener('click', () => {
    const active = body.classList.toggle('nav-open');
    navButton.setAttribute('aria-expanded', String(active));
  });
  navBackdrop?.addEventListener('click', closeNav);
  document.querySelectorAll('.suite-nav a').forEach((link) => link.addEventListener('click', closeNav));

  const updateProgress = () => {
    if (!progress) return;
    const total = document.documentElement.scrollHeight - innerHeight;
    const ratio = total > 0 ? Math.min(1, scrollY / total) : 0;
    progress.style.width = `${(ratio * 100).toFixed(2)}%`;
  };
  addEventListener('scroll', updateProgress, { passive: true });
  addEventListener('resize', updateProgress);
  updateProgress();

  document.querySelectorAll('.copy-code').forEach((button) => {
    button.addEventListener('click', async () => {
      const code = button.closest('.code-block')?.querySelector('code')?.textContent || '';
      try {
        await navigator.clipboard.writeText(code);
        button.textContent = '已复制';
      } catch {
        button.textContent = '复制失败';
      }
      setTimeout(() => { button.textContent = '复制'; }, 1400);
    });
  });

  document.querySelectorAll('.table-wrap tbody tr').forEach((row) => {
    row.addEventListener('click', () => row.classList.toggle('selected'));
  });

  document.querySelectorAll('.flow-node').forEach((node) => {
    const select = () => {
      const figure = node.closest('.flow-figure');
      figure?.querySelectorAll('.flow-node').forEach((item) => item.classList.toggle('selected', item === node));
      const live = figure?.querySelector('.diagram-live');
      if (live) live.textContent = node.dataset.detail && node.dataset.detail !== node.dataset.label
        ? `${node.dataset.label}：${node.dataset.detail}`
        : `${node.dataset.label}：流程中的一个关键对象。`;
    };
    node.addEventListener('click', select);
    node.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        select();
      }
    });
  });

  const outlineLinks = [...document.querySelectorAll('.page-outline a')];
  const outlineSections = outlineLinks.map((link) => document.getElementById(decodeURIComponent(link.hash.slice(1)))).filter(Boolean);
  if ('IntersectionObserver' in window && outlineSections.length) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (!visible) return;
      outlineLinks.forEach((link) => link.classList.toggle('active', link.hash === `#${visible.target.id}`));
    }, { rootMargin: '-18% 0px -72% 0px', threshold: [0, 0.1, 0.4] });
    outlineSections.forEach((section) => observer.observe(section));
  }

  const dialog = document.getElementById('search-dialog');
  const input = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const triggers = document.querySelectorAll('.search-trigger');
  const index = Array.isArray(window.__FRONTIER_SEARCH_INDEX__) ? window.__FRONTIER_SEARCH_INDEX__ : [];
  let activeResult = -1;
  let matches = [];

  const normalize = (value) => value.normalize('NFKC').toLocaleLowerCase('zh-CN').trim();
  const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));
  const typeLabels = {
    landing: '阅读入口', overview: '领域总览', architecture: '架构模型', landscape: '方案全景',
    trends: '近期变化', radar: 'GitHub 雷达', consensus: '共识与问题', mechanism: '技术机制',
    scenario: '场景视图', project: '工程案例', 'cross-cutting': '横切问题', method: '方法与范围',
    audit: '审计材料', review: '人工评审', boundary: '相邻边界', report: '专题报告', about: '研究套件'
  };
  const siteRoot = (() => {
    const script = document.querySelector('script[src$="search-index.js"]');
    if (!script) return './';
    return new URL('../', script.src).href;
  })();
  const resultHref = (path) => new URL(path, siteRoot).href;

  const excerpt = (text, query) => {
    const normalizedText = normalize(text);
    const position = normalizedText.indexOf(query);
    const start = Math.max(0, position >= 0 ? position - 46 : 0);
    const value = text.slice(start, start + 150);
    return `${start ? '…' : ''}${value}${start + 150 < text.length ? '…' : ''}`;
  };

  const score = (row, terms, query) => {
    const title = normalize(row.title);
    const section = normalize(row.section);
    const text = normalize(row.text);
    if (!terms.every((term) => title.includes(term) || section.includes(term) || text.includes(term))) return -1;
    let value = 0;
    for (const term of terms) {
      if (title.includes(term)) value += 14;
      if (section.includes(term)) value += 8;
      if (text.includes(term)) value += 2;
    }
    if (title.includes(query)) value += 8;
    if (section.includes(query)) value += 5;
    return value;
  };

  const renderResults = () => {
    if (!results) return;
    const query = normalize(input?.value || '');
    activeResult = -1;
    if (!query) {
      results.innerHTML = '<div class="search-empty">输入一个概念；例如“主动检索”“权限”“Codex”或项目名。</div>';
      matches = [];
      return;
    }
    const terms = query.split(/\s+/).filter(Boolean);
    const ranked = index.map((row) => ({ row, score: score(row, terms, query) }))
      .filter((item) => item.score >= 0)
      .sort((a, b) => b.score - a.score || a.row.title.localeCompare(b.row.title, 'zh-CN'));
    const perPage = new Map();
    matches = ranked.filter(({ row }) => {
      const count = perPage.get(row.title) || 0;
      perPage.set(row.title, count + 1);
      return count < 3;
    }).slice(0, 18);
    if (!matches.length) {
      results.innerHTML = '<div class="search-empty">没有匹配。试试更短的术语，或使用项目原名。</div>';
      return;
    }
    results.innerHTML = matches.map(({ row }, idx) => `
      <a class="search-result" role="option" data-result="${idx}" href="${escapeHtml(resultHref(row.path))}">
        <small><span>${escapeHtml(typeLabels[row.type] || row.type)}</span><span>${escapeHtml(row.section)}</span></small>
        <strong>${escapeHtml(row.title)}</strong>
        <p>${escapeHtml(excerpt(row.text, query))}</p>
      </a>`).join('');
  };

  const setActive = (next) => {
    const items = [...results.querySelectorAll('.search-result')];
    if (!items.length) return;
    activeResult = (next + items.length) % items.length;
    items.forEach((item, index) => {
      const active = index === activeResult;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
    });
    items[activeResult].scrollIntoView({ block: 'nearest' });
  };

  const openSearch = () => {
    if (!dialog?.showModal) return;
    dialog.showModal();
    renderResults();
    requestAnimationFrame(() => input?.focus());
  };
  triggers.forEach((trigger) => trigger.addEventListener('click', openSearch));
  input?.addEventListener('input', renderResults);
  input?.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') { event.preventDefault(); setActive(activeResult + 1); }
    if (event.key === 'ArrowUp') { event.preventDefault(); setActive(activeResult - 1); }
    if (event.key === 'Enter' && activeResult >= 0) {
      event.preventDefault();
      location.href = results.querySelectorAll('.search-result')[activeResult].href;
    }
  });
  addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      if (dialog?.open) dialog.close(); else openSearch();
    }
  });
})();
