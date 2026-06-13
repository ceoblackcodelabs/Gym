/* =============================================
   LOOPSTER — Shared HTML Components (components.js)
   ============================================= */

LOOPSTER.components = {};

// ── Header ──────────────────────────────────────
LOOPSTER.components.header = (activePage = '') => `
  <!-- Ticker -->
  <div class="ticker-bar">
    <div class="ticker-bar__label">
      <span class="dot"></span>
      LIVE
    </div>
    <div class="ticker-wrap">
      <div class="ticker-track">
        <span class="ticker-item">Geneva Climate Accord signed by 140 nations</span>
        <span class="ticker-item">Nairobi tech startups raise record $1.4B in 2025</span>
        <span class="ticker-item">Electric flights now operational on three European routes</span>
        <span class="ticker-item">AI adoption reshapes 85M jobs globally, ILO report finds</span>
        <span class="ticker-item">Democracy index shows backsliding in 28 countries</span>
        <span class="ticker-item">Sleep disorders reclassified as primary disease risk factors</span>
      </div>
    </div>
  </div>

  <!-- Header -->
  <header class="site-header">
    <div class="container">
      <div class="header-inner">
        <a href="index.html" class="site-logo">
          <span class="site-logo__wordmark">Loop<span>ster</span></span>
          <span class="site-logo__tag">News &amp; Views</span>
        </a>
        <nav class="main-nav" aria-label="Main navigation">
          <a href="index.html" ${activePage==='home'?'class="active"':''}>Home</a>
          <a href="blog-list.html" ${activePage==='list'?'class="active"':''}>News</a>
          <a href="blog-list.html?cat=world" ${activePage==='world'?'class="active"':''}>World</a>
          <a href="blog-list.html?cat=technology" ${activePage==='tech'?'class="active"':''}>Tech</a>
          <a href="blog-list.html?cat=business" ${activePage==='business'?'class="active"':''}>Business</a>
          <a href="blog-list.html?cat=health" ${activePage==='health'?'class="active"':''}>Health</a>
          <a href="blog-list.html?cat=opinion" ${activePage==='opinion'?'class="active"':''}>Opinion</a>
        </nav>
        <div class="header-actions">
          <button class="btn-search" id="searchBtn" aria-label="Search">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          </button>
          <a href="#" class="btn-subscribe">Subscribe</a>
          <button class="btn-menu" id="menuBtn" aria-label="Menu">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>
    </div>
    <nav class="mobile-nav" id="mobileNav" aria-label="Mobile navigation">
      <a href="index.html" ${activePage==='home'?'class="active"':''}>Home</a>
      <a href="blog-list.html" ${activePage==='list'?'class="active"':''}>All News</a>
      <a href="blog-list.html?cat=world">World</a>
      <a href="blog-list.html?cat=technology">Technology</a>
      <a href="blog-list.html?cat=business">Business</a>
      <a href="blog-list.html?cat=health">Health</a>
      <a href="blog-list.html?cat=politics">Politics</a>
      <a href="blog-list.html?cat=opinion">Opinion</a>
    </nav>
  </header>

  <!-- Category Strip -->
  <div class="category-strip">
    <div class="category-strip__inner">
      <a href="blog-list.html">All</a>
      ${LOOPSTER.categories.map(c =>
        `<a href="blog-list.html?cat=${c.toLowerCase()}">${c}</a>`
      ).join('')}
    </div>
  </div>

  <!-- Search Overlay -->
  <div class="search-overlay" id="searchOverlay" role="dialog" aria-label="Search">
    <div class="search-box">
      <div class="search-box__inner">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#8892A4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
        <input type="text" id="searchInput" placeholder="Search articles, topics, authors…" autocomplete="off" />
        <button id="searchClose" aria-label="Close">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#8892A4" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <p class="search-close">Press <kbd>Esc</kbd> to close &nbsp;·&nbsp; <kbd>Enter</kbd> to search</p>
    </div>
  </div>
`;

// ── Footer ──────────────────────────────────────
LOOPSTER.components.footer = () => `
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <div class="footer-brand__logo">Loop<span>ster</span></div>
          <p>Independent journalism that keeps you ahead. Trusted analysis, verified reporting, and perspectives that matter — delivered daily.</p>
          <div class="social-links">
            <a href="#" class="social-link" aria-label="Twitter">𝕏</a>
            <a href="#" class="social-link" aria-label="Instagram">◎</a>
            <a href="#" class="social-link" aria-label="LinkedIn">in</a>
            <a href="#" class="social-link" aria-label="YouTube">▶</a>
            <a href="#" class="social-link" aria-label="RSS">⊕</a>
          </div>
        </div>
        <div class="footer-col">
          <h4>Sections</h4>
          <ul>
            <li><a href="blog-list.html?cat=world">World</a></li>
            <li><a href="blog-list.html?cat=politics">Politics</a></li>
            <li><a href="blog-list.html?cat=technology">Technology</a></li>
            <li><a href="blog-list.html?cat=business">Business</a></li>
            <li><a href="blog-list.html?cat=health">Health</a></li>
            <li><a href="blog-list.html?cat=opinion">Opinion</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Company</h4>
          <ul>
            <li><a href="#">About Us</a></li>
            <li><a href="#">Our Team</a></li>
            <li><a href="#">Careers</a></li>
            <li><a href="#">Advertise</a></li>
            <li><a href="#">Press</a></li>
            <li><a href="#">Contact</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Support</h4>
          <ul>
            <li><a href="#">Subscribe</a></li>
            <li><a href="#">Newsletter</a></li>
            <li><a href="#">RSS Feed</a></li>
            <li><a href="#">Corrections</a></li>
            <li><a href="#">Ethics Policy</a></li>
            <li><a href="#">Accessibility</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2026 Loopster Media Ltd. All rights reserved.</p>
        <div class="footer-bottom-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Use</a>
          <a href="#">Cookie Settings</a>
        </div>
      </div>
    </div>
  </footer>

  <!-- Back to Top -->
  <button class="back-to-top" id="backToTop" aria-label="Back to top">
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 15l-6-6-6 6"/></svg>
  </button>
`;

// ── Article Card ─────────────────────────────────
LOOPSTER.components.articleCard = (article) => {
  const liked = LOOPSTER.isLiked(article.id);
  return `
    <article class="article-card" onclick="window.location='blog-detail.html?id=${article.id}'" tabindex="0" role="button" onkeydown="if(event.key==='Enter')window.location='blog-detail.html?id=${article.id}'">
      <div class="article-card__img-wrap">
        <img src="${article.image}" alt="${article.title}" class="article-card__img" loading="lazy">
        <span class="badge article-card__cat-badge">${article.category}</span>
      </div>
      <div class="article-card__body">
        <h3 class="article-card__title">${article.title}</h3>
        <p class="article-card__excerpt">${article.excerpt}</p>
        <div class="article-card__footer">
          <div class="article-card__byline">
            <strong>${article.author}</strong> · ${article.date}
          </div>
          <div class="article-card__stats">
            <span class="stat-pill">
              <svg viewBox="0 0 24 24" fill="${liked?'#E63946':'none'}" stroke="${liked?'#E63946':'currentColor'}" stroke-width="2" stroke-linecap="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
              ${LOOPSTER.formatNum(article.likes + (liked ? 1 : 0))}
            </span>
            <span class="stat-pill">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              ${article.comments}
            </span>
          </div>
        </div>
      </div>
    </article>
  `;
};

// ── Sidebar ──────────────────────────────────────
LOOPSTER.components.sidebar = () => {
  const trending = LOOPSTER.getTrending(5);
  return `
    <aside class="sidebar">
      <!-- Trending -->
      <div class="sidebar-widget">
        <div class="sidebar-widget__head">
          <span class="accent-dot"></span>
          <h3>Trending Now</h3>
        </div>
        <div class="sidebar-widget__body">
          <ol class="trending-list">
            ${trending.map((a, i) => `
              <li class="trending-item" onclick="window.location='blog-detail.html?id=${a.id}'" tabindex="0" role="button" onkeydown="if(event.key==='Enter')window.location='blog-detail.html?id=${a.id}'">
                <span class="trending-item__rank">${i+1}</span>
                <div class="trending-item__info">
                  <p class="trending-item__title">${a.title}</p>
                  <span class="trending-item__meta">${a.category} · ${a.readTime}</span>
                </div>
              </li>
            `).join('')}
          </ol>
        </div>
      </div>

      <!-- Newsletter -->
      <div class="newsletter-widget">
        <div class="newsletter-widget__icon">📬</div>
        <h3>Stay in the Loop</h3>
        <p>Daily briefings, breaking stories, and essential reads — straight to your inbox.</p>
        <div class="newsletter-form">
          <input type="email" class="newsletter-input" placeholder="your@email.com" id="sidebarEmail">
          <button class="newsletter-submit" onclick="LOOPSTER.handleNewsletter('sidebarEmail')">Subscribe Free</button>
        </div>
      </div>

      <!-- Tags -->
      <div class="sidebar-widget">
        <div class="sidebar-widget__head">
          <span class="accent-dot"></span>
          <h3>Explore Topics</h3>
        </div>
        <div class="sidebar-widget__body">
          <div class="tags-cloud">
            ${["AI","Climate","Africa","Economy","Health","Politics","Innovation","Space","Culture","Science","Democracy","Energy","Finance","Education","Sports"].map(t =>
              `<button class="tag-btn" onclick="window.location='blog-list.html?q=${encodeURIComponent(t)}'">${t}</button>`
            ).join('')}
          </div>
        </div>
      </div>
    </aside>
  `;
};

// ── Newsletter handler ────────────────────────────
LOOPSTER.handleNewsletter = (inputId) => {
  const input = document.getElementById(inputId);
  if (!input) return;
  const val = input.value.trim();
  if (!val || !val.includes('@')) {
    LOOPSTER.toast('Please enter a valid email address.', 'error');
    return;
  }
  input.value = '';
  LOOPSTER.toast('🎉 You\'re subscribed! Welcome to Loopster.', 'success');
};
