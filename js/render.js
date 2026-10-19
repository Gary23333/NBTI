// NBTI 渲染层：题目 / 开场 / 结果渲染，以及主题风格选择步骤、
// 进度条、toast、按钮 loading、海报弹窗等 UI。
// 本模块只负责“画界面”，不直接驱动答题流程；
// 需要外部流程（选择选项 / 预载 / 预载状态 UI）时通过 bindFlowHandlers 注入，
// 以避免 render 与 preload/stream 之间出现循环 import。

import { state, getThemeInfo, STYLE_EMOJIS, CORE_THEME_IDS, NEW_THEME_IDS, THEME_INFO_MAP, THEME_CARD_COLORS } from './state.js';
import { apiFetch } from './api.js';
import { escHtml, normalizeOptions } from './util.js';
import { skeletonCardBlock, skeletonOptions } from './skeleton.js';

// 由 main.js 注入的流程回调（打破循环依赖的装配点）
let flow = {
  selectOption: () => {},
  preloadNextQuestions: () => {},
  updatePreloadStatusUI: () => {},
  clearSessionSnapshot: () => {},
  warmupFirstQuestion: () => {},
  resetWarmup: () => {}
};

export function bindFlowHandlers(handlers) {
  flow = Object.assign(flow, handlers || {});
}

// ---------- 主题 / 风格 ----------

export async function loadThemesAndStyles() {
  try {
    const [themesResp, stylesResp] = await Promise.all([
      apiFetch('/themes'),
      apiFetch('/styles')
    ]);
    state.themesList = await themesResp.json();
    state.stylesList = await stylesResp.json();
    renderThemeGrid();
  } catch (e) {
    state.themesList = Object.keys(THEME_INFO_MAP).map(id => ({
      id,
      name: THEME_INFO_MAP[id].name,
      icon: THEME_INFO_MAP[id].icon,
      description: THEME_INFO_MAP[id].description
    }));
    state.stylesList = ['暴躁老油条'];
    renderThemeGrid();
  }
}

export function renderThemeGrid() {
  const grid = document.getElementById('theme-grid');
  if (!grid) return;

  const renderCard = (theme) => {
    const isSelected = theme.id === state.selectedTheme;
    const isNew = NEW_THEME_IDS.includes(theme.id);
    const accent = THEME_CARD_COLORS[theme.id];
    return `
      <div class="theme-card ${isSelected ? 'selected' : ''}"
           data-theme-id="${theme.id}"
           ${accent ? `style="--card-accent:${accent}"` : ''}
           onclick="selectTheme('${theme.id}')">
        ${isNew ? '<span class="theme-new-badge">NEW</span>' : ''}
        <span class="theme-icon">${theme.icon}</span>
        <div class="theme-name">${escHtml(theme.name)}</div>
        <div class="theme-desc">${escHtml(theme.description)}</div>
      </div>
    `;
  };

  const knownIds = [...CORE_THEME_IDS, ...NEW_THEME_IDS];
  const pickThemes = ids => ids.map(id => state.themesList.find(t => t.id === id)).filter(Boolean);
  const coreThemes = pickThemes(CORE_THEME_IDS);
  const hotThemes = [...pickThemes(NEW_THEME_IDS), ...state.themesList.filter(t => !knownIds.includes(t.id))];

  let html = '';
  if (coreThemes.length) {
    html += `<div class="theme-group-title">核心主题</div>${coreThemes.map(renderCard).join('')}`;
  }
  if (hotThemes.length) {
    html += `<div class="theme-group-title">热门主题</div>${hotThemes.map(renderCard).join('')}`;
  }
  grid.innerHTML = html;
}

export function selectTheme(themeId) {
  state.selectedTheme = themeId;
  // 主题变化会让已预热的首题草稿失效
  flow.resetWarmup();
  document.querySelectorAll('.theme-card').forEach(card => {
    card.classList.toggle('selected', card.dataset.themeId === themeId);
  });
  setTimeout(() => goToStep('style'), 200);
}

export function renderStyleGrid() {
  const grid = document.getElementById('style-grid');
  if (!grid) return;

  grid.innerHTML = state.stylesList.map(style => {
    const isSelected = style === state.selectedStyle;
    const emoji = STYLE_EMOJIS[style] || '✨';
    return `
      <div class="style-card ${isSelected ? 'selected' : ''}" 
           data-style-name="${escHtml(style)}"
           onclick="selectStyle('${escHtml(style).replace(/'/g, "\\'")}')">
        <span class="style-card-emoji">${emoji}</span>
        ${escHtml(style)}
      </div>
    `;
  }).join('');
}

export function selectStyle(styleName) {
  state.selectedStyle = styleName;
  // 风格变化会让已预热的首题草稿失效
  flow.resetWarmup();
  document.querySelectorAll('.style-card').forEach(card => {
    card.classList.toggle('selected', card.dataset.styleName === styleName);
  });
  setTimeout(() => goToStep('ready'), 200);
}

export function updateReadyStep() {
  const themeBadge = document.getElementById('selected-theme-badge');
  const styleBadge = document.getElementById('selected-style-badge');
  const readyEmoji = document.getElementById('ready-emoji');
  const readyTitle = document.getElementById('ready-title');

  const theme = state.themesList.find(t => t.id === state.selectedTheme);
  if (theme) {
    themeBadge.innerHTML = `${theme.icon} ${escHtml(theme.name)}`;
    readyEmoji.textContent = theme.icon;
  }
  styleBadge.textContent = state.selectedStyle;
}

export function goToStep(step) {
  const steps = ['theme', 'style', 'ready'];
  const currentIdx = steps.indexOf(state.welcomeStep);
  const targetIdx = steps.indexOf(step);
  const direction = targetIdx > currentIdx ? 'forward' : 'backward';

  state.welcomeStep = step;

  document.querySelectorAll('.welcome-step').forEach(el => {
    el.classList.remove('active', 'prev');
  });

  const targetEl = document.getElementById(`step-${step}`);
  if (targetEl) {
    targetEl.classList.add('active');
    if (direction === 'backward') {
      targetEl.classList.add('prev');
    }
  }

  updateStepper(step);

  if (step === 'style') {
    renderStyleGrid();
  } else if (step === 'ready') {
    updateReadyStep();
    // 进入 ready 步骤即预热首题（后端未就绪时会静默跳过，不影响主流程）
    flow.warmupFirstQuestion();
  }
}

export function updateStepper(activeStep) {
  const stepper = document.getElementById('progress-stepper');
  if (!stepper) return;

  const stepMap = { theme: 1, style: 2, ready: 3, test: 3 };
  const activeNum = stepMap[activeStep] || 1;

  stepper.style.display = 'flex';

  document.querySelectorAll('.step').forEach(stepEl => {
    const num = parseInt(stepEl.dataset.step);
    stepEl.classList.remove('active', 'completed');
    if (num < activeNum) {
      stepEl.classList.add('completed');
    } else if (num === activeNum) {
      stepEl.classList.add('active');
    }
  });

  document.querySelectorAll('.step-line').forEach((line, idx) => {
    line.classList.remove('completed');
    if (idx < activeNum - 1) {
      line.classList.add('completed');
    }
  });
}

export function goBackToTheme() {
  goToStep('theme');
}

export function goBackToStyle() {
  goToStep('style');
}

// ---------- 页面切换与进度 ----------

export function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const page = document.getElementById(pageId);
  if (page) {
    page.classList.add('active');
  }

  if (pageId === 'page-test') {
    updateStepper('test');
  }
}

export function updateProgress() {
  const percent = Math.min(state.currentQuestion / state.maxQuestions * 100, 100);
  const fill = document.getElementById('progress-fill');
  const text = document.getElementById('progress-text');
  if (fill) fill.style.width = `${percent}%`;
  if (text) text.textContent = `第 ${state.currentQuestion} 题`;
}

// ---------- 等待期假进度（0 → ~90%，收到首 token 后补满） ----------

let fakeProgressTimer = null;

// 启动平滑假进度：先快后慢逼近 cap，给等待期更明确的反馈
export function startFakeProgressStage(cap = 90) {
  stopFakeProgressStage();
  const fill = document.getElementById('fake-progress-fill');
  if (!fill) return;
  let p = 0;
  fill.style.width = '0%';
  const track = document.getElementById('fake-progress-track');
  if (track) track.classList.remove('done');

  fakeProgressTimer = setInterval(() => {
    const el = document.getElementById('fake-progress-fill');
    if (!el) {
      stopFakeProgressStage();
      return;
    }
    // 前段推进快、后段减速，避免长时间停在原地
    const step = p < 55 ? 3 + Math.random() * 4 : 0.6 + Math.random() * 1.2;
    p = Math.min(p + step, cap);
    el.style.width = `${p}%`;
  }, 220);
}

// 收到首 token / 内容就绪：补满并淡出进度条
export function completeFakeProgressStage() {
  stopFakeProgressStage();
  const fill = document.getElementById('fake-progress-fill');
  const track = document.getElementById('fake-progress-track');
  if (fill) fill.style.width = '100%';
  if (track) {
    track.classList.add('done');
    setTimeout(() => {
      if (track && track.parentElement) track.style.display = 'none';
    }, 420);
  }
}

function stopFakeProgressStage() {
  if (fakeProgressTimer) {
    clearInterval(fakeProgressTimer);
    fakeProgressTimer = null;
  }
}

// ---------- 题目 / 开场渲染 ----------

export function renderQuestionIncremental(partialData, options = [], settings = {}) {
  const questionArea = document.getElementById('question-area');
  options = normalizeOptions(options);
  let commentBubble = document.getElementById('incremental-comment');
  let questionCard = document.getElementById('incremental-card');
  let optionsContainer = document.getElementById('incremental-options');

  if (!commentBubble || !questionCard || !optionsContainer) {
    // 兜底：外壳缺失时重建（同样先给骨架占位）
    questionArea.innerHTML = `
      <div id="incremental-comment" class="comment-bubble" style="opacity:0;transition:opacity 0.3s;"></div>
      <div id="incremental-card" class="question-card" style="opacity:1;transition:opacity 0.3s;">
        <div id="incremental-label" class="question-label">第 ${partialData.q || state.currentQuestion || 1} 题</div>
        ${skeletonCardBlock('正在生成题目')}
        <div id="incremental-scene" class="question-text stream-placeholder" style="display:none;"></div>
      </div>
      <div id="incremental-options" class="options" style="opacity:1;transition:opacity 0.3s;">${skeletonOptions(4)}</div>
      <div id="preload-status" class="preload-status-container"></div>
    `;
    commentBubble = document.getElementById('incremental-comment');
    questionCard = document.getElementById('incremental-card');
    optionsContainer = document.getElementById('incremental-options');
  }

  const labelEl = document.getElementById('incremental-label');
  if (partialData.q && labelEl) {
    labelEl.textContent = `第 ${partialData.q} 题`;
  }

  if (partialData.comment && commentBubble.textContent !== partialData.comment) {
    commentBubble.textContent = partialData.comment;
    if (commentBubble.style.opacity === '0') {
      setTimeout(() => commentBubble.style.opacity = '1', 50);
    }
  }

  const sceneEl = document.getElementById('incremental-scene');
  if (partialData.scene && sceneEl && sceneEl.textContent !== partialData.scene) {
    // 真实题干到达：移除骨架块、显示题干（避免骨架与内容叠加导致跳动）
    const skel = document.getElementById('incremental-skeleton');
    if (skel) skel.remove();
    sceneEl.classList.remove('stream-placeholder');
    sceneEl.style.display = '';
    sceneEl.textContent = partialData.scene;
    if (questionCard.style.opacity === '0') {
      setTimeout(() => questionCard.style.opacity = '1', 50);
    }
  }

  if (options.length > 0) {
    // 真实选项到达：先清掉选项骨架，再写入真实按钮
    if (optionsContainer.querySelector('.skeleton-option')) {
      optionsContainer.innerHTML = '';
    }
    const letters = ['A', 'B', 'C', 'D'];
    options.slice(0, 4).forEach((opt, i) => {
      const optText = typeof opt === 'string' ? opt : '';
      const existingBtn = optionsContainer.children[i];
      const optionText = escHtml(optText);
      if (existingBtn) {
        existingBtn.dataset.optionText = optText;
        existingBtn.disabled = !settings.enableOptions;
        existingBtn.innerHTML = `<span class="letter">${letters[i]}</span>${optionText}`;
        existingBtn.onclick = () => flow.selectOption(letters[i], optText);
        return;
      }

      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.dataset.optionText = optText;
      btn.disabled = !settings.enableOptions;
      btn.innerHTML = `<span class="letter">${letters[i]}</span>${optionText}`;
      btn.addEventListener('click', () => flow.selectOption(letters[i], optText));
      optionsContainer.appendChild(btn);
    });
    setTimeout(() => optionsContainer.style.opacity = '1', 100);
  }

  if (settings.enableOptions) {
    Array.from(optionsContainer.children).forEach(btn => btn.disabled = false);
  }

  if (partialData.comment || partialData.scene || options.length > 0) {
    const statusEl = document.getElementById('preload-status');
    if (statusEl && statusEl.dataset.streaming === 'true') {
      statusEl.innerHTML = '';
      delete statusEl.dataset.streaming;
    }
  }
}

export function showLoadingAnimation() {
  const questionArea = document.getElementById('question-area');

  const loadingTexts = [
    { text: "AI 正在观察你的摸鱼姿势...", style: "" },
    { text: "分析你的职场DNA中...", style: "" },
    { text: "正在生成让你破防的题目...", style: "" },
    { text: "读取你的老板雷达信号...", style: "" },
    { text: "计算你的卷王指数...", style: "" },
    { text: "探测你的甩锅防御力...", style: "" },
    { text: "扫描你的加班耐受度...", style: "" },
    { text: "正在偷看你和HR的聊天记录", style: "font-size:0.6rem;color:var(--text-secondary);letter-spacing:2px;font-family:'Courier New',monospace;" },
    { text: "你的简历已被标记为「高危」", style: "font-size:1.6rem;color:var(--accent-violet);font-weight:900;" },
    { text: "警告：检测到反骨浓度过高", style: "font-size:0.7rem;color:var(--accent-pink);text-transform:uppercase;letter-spacing:4px;" },
    { text: "你的考勤记录正在自我删除", style: "font-size:1.4rem;color:var(--accent-blue);font-style:italic;font-family:'Times New Roman',serif;" },
    { text: "系统在犹豫要不要告发你", style: "font-size:0.65rem;color:var(--text-secondary);text-decoration:line-through;" },
    { text: "别动，AI在数你有几根反骨", style: "font-size:1.3rem;color:#fbbf24;font-weight:bold;transform:rotate(-2deg);display:inline-block;" },
    { text: "正在给你的PPT添加错别字", style: "font-size:0.55rem;color:var(--accent-emerald);font-family:'Comic Sans MS',cursive;" },
    { text: "你的离职信已自动生成", style: "font-size:1.5rem;color:var(--accent-pink);text-shadow:0 0 10px rgba(236,72,153,0.4);" },
    { text: "系统在给你的工位装摄像头", style: "font-size:0.75rem;color:var(--text-secondary);border:1px dashed var(--border-glass);padding:4px 8px;border-radius:4px;display:inline-block;" },
    { text: "正在向全公司广播你的测试结果", style: "font-size:1.2rem;color:var(--accent-violet);font-weight:700;letter-spacing:-1px;" },
    { text: "你的OKR正在被AI重写", style: "font-size:0.6rem;color:var(--accent-cyan);writing-mode:vertical-rl;display:inline-block;height:80px;" },
    { text: "警告：你已被列入「重点观察名单」", style: "font-size:0.9rem;color:#fbbf24;background:rgba(251,191,36,0.1);padding:4px 12px;border-radius:4px;font-family:'Courier New',monospace;" },
    { text: "系统正在偷笑", style: "font-size:2rem;color:var(--accent-pink);font-weight:900;line-height:1;" },
    { text: "正在把你的头像P成表情包", style: "font-size:0.7rem;color:var(--text-secondary);font-style:italic;opacity:0.6;" },
    { text: "AI已经看透你了", style: "font-size:1.8rem;color:var(--accent-violet);font-weight:900;letter-spacing:2px;transform:scale(1.1);display:inline-block;" },
    { text: "正在把你的周报翻译成火星文", style: "font-size:0.65rem;color:var(--accent-emerald);text-decoration:wavy underline;" },
    { text: "正在调用摸鱼探测模块...", style: "" },
    { text: "加载毒舌数据库...", style: "" },
    { text: "校准吐槽精准度...", style: "" },
    { text: "准备释放灵魂拷问...", style: "" },
    { text: "你的工位正在被AI扫描...", style: "font-size:0.8rem;color:var(--text-secondary);" },
    { text: "警告：你的聊天记录已被AI读取", style: "font-size:0.7rem;color:#ef4444;" },
    { text: "正在生成让你血压升高的问题", style: "" },
    { text: "AI正在编排你的职场段子...", style: "" },
    { text: "加载杠精模式...", style: "" }
  ];

  questionArea.innerHTML = `
    <div class="loading" style="padding: 60px 20px;">
      <div class="spinner"></div>
      <p id="loading-text" style="margin-top: 20px; min-height: 2.5em; transition: all 0.3s;">正在连接AI...</p>
      <div class="fake-progress" style="width: 200px; height: 6px; background: var(--surface-glass); border-radius: var(--radius-full); margin: 24px auto 0; overflow: hidden; backdrop-filter: var(--blur-sm); border: 1px solid var(--border-glass);">
        <div id="fake-progress-fill" style="width: 0%; height: 100%; background: var(--gradient-primary); transition: width 0.3s; border-radius: var(--radius-full);"></div>
      </div>
    </div>
  `;

  let idx = 0;
  const textInterval = setInterval(() => {
    const el = document.getElementById('loading-text');
    if (el) {
      const item = loadingTexts[idx % loadingTexts.length];
      el.textContent = item.text;
      el.style.cssText = `margin-top: 20px; min-height: 2.5em; transition: all 0.3s; ${item.style}`;
      idx++;
    } else {
      clearInterval(textInterval);
    }
  }, 600);

  let progress = 0;
  const progressInterval = setInterval(() => {
    const el = document.getElementById('fake-progress-fill');
    if (el) {
      progress += Math.random() * 10;
      if (progress > 88) progress = 88;
      el.style.width = `${progress}%`;
    } else {
      clearInterval(progressInterval);
    }
  }, 280);
}

// 切题 / 生成中的题目外壳：内置结构化骨架（shimmer 卡片 + 选项骨架）
export function showStreamingQuestionShell() {
  const questionArea = document.getElementById('question-area');
  const nextQuestion = state.currentQuestion > 0 ? state.currentQuestion + 1 : 1;
  const progressText = document.getElementById('progress-text');
  const progressFill = document.getElementById('progress-fill');

  if (progressText) {
    progressText.textContent = `第 ${nextQuestion} 题`;
  }
  if (progressFill) {
    progressFill.style.width = `${Math.min(nextQuestion / state.maxQuestions * 100, 100)}%`;
  }

  questionArea.innerHTML = `
    <div id="incremental-comment" class="comment-bubble" style="opacity:0;transition:opacity 0.3s;"></div>
    <div id="incremental-card" class="question-card" style="opacity:1;transition:opacity 0.3s;">
      <div id="incremental-label" class="question-label">第 ${nextQuestion} 题</div>
      ${skeletonCardBlock('正在生成题目')}
      <div id="incremental-scene" class="question-text stream-placeholder" style="display:none;"></div>
    </div>
    <div id="incremental-options" class="options" style="opacity:1;transition:opacity 0.3s;">${skeletonOptions(4)}</div>
    <div class="fake-progress" id="fake-progress-track">
      <div class="fake-progress-fill" id="fake-progress-fill"></div>
    </div>
    <div id="preload-status" class="preload-status-container" data-streaming="true"></div>
  `;

  startFakeProgressStage();
}

// 开场（首题）外壳：骨架 + 假进度，等待期给出更明确的推进反馈
export function showStreamingIntroShell() {
  const questionArea = document.getElementById('question-area');
  const progressText = document.getElementById('progress-text');
  const progressFill = document.getElementById('progress-fill');

  if (progressText) {
    progressText.textContent = '开场';
  }
  if (progressFill) {
    progressFill.style.width = '2%';
  }

  questionArea.innerHTML = `
    <div class="question-card intro-card">
      <div class="intro-emoji">🎭</div>
      <div id="incremental-skeleton" class="skeleton-block center">
        <div class="sk-line sk-line-90"></div>
        <div class="sk-line sk-line-80"></div>
        <div class="sk-line sk-line-50"></div>
        <div class="skeleton-caption">正在酝酿开场白<span class="typing-dots"></span></div>
      </div>
      <div id="incremental-intro" class="question-text stream-placeholder" style="display:none;font-size: 1.15rem; line-height: 1.9; margin-bottom: 28px; color: var(--text-primary);"></div>
      <div class="fake-progress" id="fake-progress-track">
        <div class="fake-progress-fill" id="fake-progress-fill"></div>
      </div>
      <button class="btn btn-primary" disabled style="padding: 14px 48px; font-size: 1.05rem; opacity:0.55;">
        开始答题 →
      </button>
    </div>
  `;

  startFakeProgressStage();
}

export function renderIntroIncremental(comment) {
  const introEl = document.getElementById('incremental-intro');
  if (!introEl || !comment) return;

  // 开场文案到达：移除骨架、显示正文（平滑替换，无叠加）
  const skel = document.getElementById('incremental-skeleton');
  if (skel) skel.remove();
  introEl.classList.remove('stream-placeholder');
  introEl.style.display = '';
  introEl.textContent = comment;
}

export function renderIntro(intro, scene, options, tags) {
  state.firstQuestionCache = { scene, options, tags };
  completeFakeProgressStage();
  const questionArea = document.getElementById('question-area');
  questionArea.innerHTML = `
    <div class="question-card intro-card">
      <div class="intro-emoji">🎉</div>
      <div class="question-text" style="font-size: 1.15rem; line-height: 1.9; margin-bottom: 40px; color: var(--text-primary);">${escHtml(intro).replace(/\n/g, '<br>')}</div>
      <button class="btn btn-primary btn-glow" onclick="showFirstQuestion()" style="padding: 14px 48px; font-size: 1.05rem;">
        开始答题 →
      </button>
      <div id="preload-status" class="preload-status-container" style="margin-top: 20px;"></div>
    </div>
  `;

  flow.preloadNextQuestions(options);
}

export function showFirstQuestion() {
  if (!state.firstQuestionCache) return;
  const { scene, options, tags } = state.firstQuestionCache;
  state.firstQuestionCache = null;
  renderQuestion(scene, options, tags, { skipPreload: true });
}

export function renderQuestion(body, options, tags, settings = {}) {
  const questionArea = document.getElementById('question-area');
  completeFakeProgressStage();
  const normalizedOptions = normalizeOptions(options);

  let commentHtml = '';
  let sceneText = '';

  if (typeof body === 'object') {
    sceneText = body.scene || '';
    if (body.comment) {
      commentHtml = `<div class="comment-bubble">${escHtml(body.comment)}</div>`;
    }
  } else {
    const parts = body.split('\n\n');
    if (parts.length >= 2) {
      commentHtml = `<div class="comment-bubble">${escHtml(parts[0])}</div>`;
      sceneText = parts[parts.length - 1];
    } else {
      sceneText = parts[0] || body;
    }
  }

  questionArea.innerHTML = `
    ${commentHtml}
    <div class="question-card">
      <div class="question-label">第 ${state.currentQuestion} 题</div>
      <div class="question-text">${escHtml(sceneText)}</div>
    </div>
    <div class="options" id="final-options"></div>
    <div id="preload-status" class="preload-status-container"></div>
  `;

  const letters = ['A', 'B', 'C', 'D'];
  const optionsContainer = document.getElementById('final-options');
  normalizedOptions.forEach((opt, i) => {
    const optText = typeof opt === 'string' ? opt : '';
    const btn = document.createElement('button');
    btn.className = 'option-btn';
    btn.dataset.optionText = optText;
    btn.innerHTML = `<span class="letter">${letters[i]}</span>${escHtml(optText)}`;
    btn.addEventListener('click', () => flow.selectOption(letters[i], optText));
    optionsContainer.appendChild(btn);
  });

  if (!settings.skipPreload) {
    flow.preloadNextQuestions(normalizedOptions);
  } else {
    flow.updatePreloadStatusUI();
  }
}

// ---------- 结果页 ----------

export function showResult(answer, tags) {
  flow.clearSessionSnapshot();
  showPage('page-result');

  const resultArea = document.getElementById('result-area');

  let type = tags.TYPE || 'UNKNOWN';
  let name = tags.NAME || '未知人格';
  let oneline = tags.ONELINE || '';
  let interpretation = '';
  let pseudoScience = '';
  let closing = '';
  let scene = '';
  let adapt = '';
  let crash = '';

  if (typeof answer === 'object') {
    type = answer.type || type;
    name = answer.name || name;
    oneline = answer.oneline || oneline;
    interpretation = answer.interpretation || '';
    pseudoScience = answer.pseudo_science || '';
    closing = answer.closing || '';
    scene = answer.scene || '';
    adapt = answer.adapt || '';
    crash = answer.crash || '';
  } else if (typeof answer === 'string') {
    try {
      const json = JSON.parse(answer.trim());
      type = json.type || type;
      name = json.name || name;
      oneline = json.oneline || oneline;
      interpretation = json.interpretation || '';
      pseudoScience = json.pseudo_science || '';
      closing = json.closing || '';
      scene = json.scene || '';
      adapt = json.adapt || '';
      crash = json.crash || '';
    } catch (e) {}
  }

  state.currentResult = {
    type, name, oneline, scene, adapt, crash,
    interpretation, pseudo_science: pseudoScience, closing
  };

  const currentThemeInfo = getThemeInfo(state.selectedTheme);

  const fmt = (text) => escHtml(text).replace(/\n/g, '<br>');

  let metaHtml = '';
  if (scene) metaHtml += `<div class="result-meta"><span class="meta-label">🎬 名场面</span><span>${escHtml(scene)}</span></div>`;
  if (adapt) metaHtml += `<div class="result-meta"><span class="meta-label">🎯 适配</span><span>${escHtml(adapt)}</span></div>`;
  if (crash) metaHtml += `<div class="result-meta"><span class="meta-label">⚠️ 翻车</span><span>${escHtml(crash)}</span></div>`;

  resultArea.innerHTML = `
    <div style="display:inline-flex;align-items:center;gap:6px;padding:6px 16px;background:var(--surface-glass);backdrop-filter:var(--blur-sm);-webkit-backdrop-filter:var(--blur-sm);border:1px solid var(--border-glass);border-radius:var(--radius-full);font-size:0.85rem;color:var(--accent-violet);font-weight:600;margin-bottom:20px;">
      ${currentThemeInfo.icon} ${currentThemeInfo.name}
    </div>
    <div class="avatar-container" id="result-avatar">
    </div>
    <div class="code">${escHtml(type)}</div>
    <h2>${escHtml(name)}</h2>
    <div class="oneline">"${escHtml(oneline)}"</div>
    ${metaHtml}

    <div class="radar-section">
      <h3>📊 维度画像</h3>
      <div class="radar-chart" id="radar-chart"></div>
    </div>

    <div class="report">
      ${interpretation ? `<div class="report-section"><h3>🔍 毒舌解读</h3><p>${fmt(interpretation)}</p></div>` : ''}
      ${pseudoScience ? `<div class="report-section"><h3>🧪 伪科学分析</h3><p>${fmt(pseudoScience)}</p></div>` : ''}
      ${closing ? `<div class="report-section closing"><p>${fmt(closing)}</p></div>` : ''}
    </div>

    <div class="actions">
      <button class="btn btn-primary" id="btn-share-poster">📮 分享海报</button>
      <button class="btn btn-outline" id="btn-copy-text">📋 复制文案</button>
      <button class="btn btn-outline" id="btn-share-link">🔗 复制链接</button>
      <button class="btn btn-outline" onclick="refreshAvatar()">🎲 换一换</button>
      <button class="btn btn-outline" onclick="downloadAvatar()">📥 下载头像</button>
      <button class="btn btn-outline" onclick="restart()">🔄 再来一次</button>
    </div>
  `;

  const posterBtn = document.getElementById('btn-share-poster');
  if (posterBtn) posterBtn.addEventListener('click', sharePoster);
  const linkBtn = document.getElementById('btn-share-link');
  if (linkBtn) linkBtn.addEventListener('click', shareLink);
  const copyTextBtn = document.getElementById('btn-copy-text');
  if (copyTextBtn) copyTextBtn.addEventListener('click', copyResultText);

  drawAvatar('result-avatar', type);

  if (window.NBTIRadar) {
    window.NBTIRadar.renderRadar('radar-chart', state.scores, { theme: state.selectedTheme });
  }
}

// ---------- UI 工具 ----------

let toastTimer = null;
export function showToast(msg) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.className = 'toast';
    toast.setAttribute('role', 'status');
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('show');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
}

export function setBtnLoading(btn, loading, loadingText) {
  if (!btn) return;
  if (loading) {
    btn.dataset.originalText = btn.textContent;
    btn.textContent = loadingText;
    btn.disabled = true;
  } else {
    btn.textContent = btn.dataset.originalText || btn.textContent;
    btn.disabled = false;
  }
}

export function openPosterModal(canvas) {
  let modal = document.getElementById('poster-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'poster-modal';
    modal.className = 'poster-modal';
    modal.innerHTML = `
      <div class="poster-modal-inner">
        <img alt="NBTI 分享海报预览">
        <p class="poster-modal-hint">长按图片可保存到相册</p>
        <div class="poster-modal-actions">
          <button class="btn btn-primary" id="poster-download-btn">📥 下载 PNG</button>
          <button class="btn btn-outline" id="poster-close-btn">关闭</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('open');
    });
    document.getElementById('poster-close-btn').addEventListener('click', () => {
      modal.classList.remove('open');
    });
    document.getElementById('poster-download-btn').addEventListener('click', () => {
      if (window.NBTIPoster && state.currentResult) {
        const themeInfo = getThemeInfo(state.selectedTheme);
        window.NBTIPoster.download(state.currentResult, state.scores, {
          theme: state.selectedTheme,
          themeInfo: themeInfo,
          slogan: themeInfo.name
        }).catch(() => showToast('下载失败，请重试'));
      }
    });
  }
  modal.querySelector('img').src = canvas.toDataURL('image/png');
  modal.classList.add('open');
}

export async function sharePoster() {
  if (!window.NBTIPoster) {
    alert('海报模块未加载，无法生成分享海报');
    return;
  }
  if (!state.currentResult) {
    showToast('还没有生成结果');
    return;
  }
  const btn = document.getElementById('btn-share-poster');
  setBtnLoading(btn, true, '生成中…');
  try {
    const themeInfo = getThemeInfo(state.selectedTheme);
    const canvas = await window.NBTIPoster.generate(state.currentResult, state.scores, {
      theme: state.selectedTheme,
      themeInfo: themeInfo,
      slogan: themeInfo.name
    });
    openPosterModal(canvas);
  } catch (e) {
    console.error('海报生成失败', e);
    showToast('海报生成失败，请重试');
  } finally {
    setBtnLoading(btn, false);
  }
}

export async function copyResultText() {
  if (!window.NBTIPoster || !state.currentResult) {
    showToast('还没有生成结果');
    return;
  }
  const btn = document.getElementById('btn-copy-text');
  setBtnLoading(btn, true, '复制中…');
  try {
    const hashtagMap = {
      workplace: ['#人格测试', '#NBTI', '#职场人格'],
      animal: ['#动物人格', '#人格测试', '#NBTI'],
      color: ['#色彩人格', '#人格测试', '#NBTI'],
      love: ['#恋爱人格', '#人格测试', '#NBTI'],
      social: ['#社交人格', '#人格测试', '#NBTI'],
      mbti: ['#MBTI', '#16型人格', '#NBTI'],
      brainhol: ['#脑洞人格', '#人格测试', '#NBTI'],
      money: ['#搞钱人格', '#人格测试', '#NBTI'],
      spirit: ['#精神状态检测', '#人格测试', '#NBTI']
    };
    const themeName = getThemeInfo(state.selectedTheme).name;
    const hashtags = hashtagMap[state.selectedTheme] || ['#人格测试', '#NBTI'];
    const text = window.NBTIPoster.generateCopyText(state.currentResult, themeName, hashtags);
    await copyText(text);
    showToast('文案已复制，快去发朋友圈！');
  } catch (e) {
    console.error('复制失败', e);
    showToast('复制失败，请手动复制');
  } finally {
    setBtnLoading(btn, false);
  }
}

export async function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.select();
  document.execCommand('copy');
  document.body.removeChild(ta);
}

export async function shareLink() {
  if (!state.currentResult) {
    showToast('还没有生成结果');
    return;
  }
  const btn = document.getElementById('btn-share-link');
  setBtnLoading(btn, true, '复制中…');
  try {
    const resp = await apiFetch('/share', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ result: state.currentResult, scores: state.scores })
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok || !data.id || !/^[A-Za-z0-9_-]{1,32}$/.test(data.id)) {
      throw new Error(data.error || `HTTP ${resp.status}`);
    }
    await copyText(window.location.origin + '/share/' + data.id);
    showToast('链接已复制，快去朋友圈装逼');
  } catch (e) {
    console.error('分享链接失败', e);
    showToast('分享失败：' + (e.message || '网络异常'));
  } finally {
    setBtnLoading(btn, false);
  }
}

export function drawAvatar(elementId, personality) {
  const container = document.getElementById(elementId);
  if (!container) return;
  if (!window.NBTIAvatar) {
    container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;color:var(--text-secondary);font-size:0.9rem;">头像生成器加载失败</div>';
    return;
  }
  container.innerHTML = window.NBTIAvatar.generateSvgAvatar(personality, { theme: state.selectedTheme });
}

export function refreshAvatar() {
  const container = document.getElementById('result-avatar');
  if (!container) return;
  const codeEl = document.querySelector('.code');
  const personality = codeEl ? codeEl.textContent.trim() : 'NBTI';
  drawAvatar('result-avatar', personality);
}

export function downloadAvatar() {
  if (!window.NBTIAvatar) {
    alert('头像生成器未加载，无法下载');
    return;
  }
  const container = document.getElementById('result-avatar');
  if (!container) return;
  const codeEl = document.querySelector('.code');
  const personality = codeEl ? codeEl.textContent.trim() : 'NBTI';

  const svg = window.NBTIAvatar.generateSvgAvatar(personality, { theme: state.selectedTheme });
  const svgBlob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  const link = document.createElement('a');
  link.download = `nbti-avatar-${personality}.svg`;
  link.href = url;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 100);
}
