const API_URL = '/api';

let conversationId = '';
let currentQuestion = 0;
let totalQuestions = 25;
let scores = { nb: 0, bh: 0, tf: 0, ip: 0 };
let currentResult = null;
let nextDim = 'NB';
let canConclude = false;
let answerLocked = false;
let incompleteRetryCount = 0;
const MAX_INCOMPLETE_RETRIES = 3;

let selectedTheme = 'workplace';
let selectedStyle = '暴躁老油条';
let themesList = [];
let stylesList = [];
let welcomeStep = 'theme';

let minQuestions = 12;
let maxQuestions = 16;
let configLoaded = false;
let preloadEnabled = true;

const STYLE_EMOJIS = {
  '暴躁老油条': '😤',
  '冷面纪录片': '🎬',
  '戏精闺蜜': '💅',
  '霸总文学': '👑',
  '玄学算命': '🔮',
  '二次元萌系': '🌸',
  '官方MBTI': '🧠'
};

async function loadConfig() {
  if (configLoaded) return;
  configLoaded = true;
  try {
    const resp = await fetch(`${API_URL}/config`);
    const cfg = await resp.json();
    if (typeof cfg.min_questions === 'number' && cfg.min_questions > 0) minQuestions = cfg.min_questions;
    if (typeof cfg.max_questions === 'number' && cfg.max_questions > 0) maxQuestions = cfg.max_questions;
    if (typeof cfg.preload_enabled === 'boolean') preloadEnabled = cfg.preload_enabled;
  } catch (e) {}
}
loadConfig();

async function loadThemesAndStyles() {
  try {
    const [themesResp, stylesResp] = await Promise.all([
      fetch(`${API_URL}/themes`),
      fetch(`${API_URL}/styles`)
    ]);
    themesList = await themesResp.json();
    stylesList = await stylesResp.json();
    renderThemeGrid();
  } catch (e) {
    themesList = [
      { id: 'workplace', name: '职场人格', description: '经典职场人格测试，16种职场角色定位', icon: '💼' }
    ];
    stylesList = ['暴躁老油条'];
    renderThemeGrid();
  }
}

function renderThemeGrid() {
  const grid = document.getElementById('theme-grid');
  if (!grid) return;

  const supportedThemes = ['workplace', 'animal', 'color'];

  grid.innerHTML = themesList.map(theme => {
    const isSupported = supportedThemes.includes(theme.id);
    const isSelected = theme.id === selectedTheme;
    return `
      <div class="theme-card ${isSelected ? 'selected' : ''}" 
           data-theme-id="${theme.id}"
           ${isSupported ? 'onclick="selectTheme(\'' + theme.id + '\')"' : ''}>
        ${!isSupported ? '<span class="theme-coming-soon">敬请期待</span>' : ''}
        <span class="theme-icon">${theme.icon}</span>
        <div class="theme-name">${escHtml(theme.name)}</div>
        <div class="theme-desc">${escHtml(theme.description)}</div>
      </div>
    `;
  }).join('');
}

function selectTheme(themeId) {
  selectedTheme = themeId;
  document.querySelectorAll('.theme-card').forEach(card => {
    card.classList.toggle('selected', card.dataset.themeId === themeId);
  });
  setTimeout(() => goToStep('style'), 200);
}

function renderStyleGrid() {
  const grid = document.getElementById('style-grid');
  if (!grid) return;

  grid.innerHTML = stylesList.map(style => {
    const isSelected = style === selectedStyle;
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

function selectStyle(styleName) {
  selectedStyle = styleName;
  document.querySelectorAll('.style-card').forEach(card => {
    card.classList.toggle('selected', card.dataset.styleName === styleName);
  });
  setTimeout(() => goToStep('ready'), 200);
}

function updateReadyStep() {
  const themeBadge = document.getElementById('selected-theme-badge');
  const styleBadge = document.getElementById('selected-style-badge');
  const readyEmoji = document.getElementById('ready-emoji');
  const readyTitle = document.getElementById('ready-title');

  const theme = themesList.find(t => t.id === selectedTheme);
  if (theme) {
    themeBadge.innerHTML = `${theme.icon} ${escHtml(theme.name)}`;
    readyEmoji.textContent = theme.icon;
  }
  styleBadge.textContent = selectedStyle;
}

function goToStep(step) {
  const steps = ['theme', 'style', 'ready'];
  const currentIdx = steps.indexOf(welcomeStep);
  const targetIdx = steps.indexOf(step);
  const direction = targetIdx > currentIdx ? 'forward' : 'backward';

  welcomeStep = step;

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
  }
}

function updateStepper(activeStep) {
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

function goBackToTheme() {
  goToStep('theme');
}

function goBackToStyle() {
  goToStep('style');
}

function escHtml(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function extractJsonFromText(text) {
  if (typeof text !== 'string') return null;
  text = text.trim();
  if (!text) return null;

  if (text.startsWith('{')) {
    try { const obj = JSON.parse(text); if (obj.phase) return obj; } catch(e) {}
  }

  const codeBlock = text.match(/```(?:json)?\s*\n([\s\S]*?)\n\s*```/);
  if (codeBlock) {
    try { const obj = JSON.parse(codeBlock[1].trim()); if (obj.phase) return obj; } catch(e) {}
  }

  const phaseMatch = text.match(/\{\s*"phase"\s*:\s*"(?:ASSESS|RESULT)"[\s\S]*?\}/);
  if (phaseMatch) {
    try { const obj = JSON.parse(phaseMatch[0]); if (obj.phase) return obj; } catch(e) {}
  }

  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start >= 0 && end > start) {
    try { const obj = JSON.parse(text.substring(start, end + 1)); if (obj.phase) return obj; } catch(e) {}
  }

  return null;
}

function normalizeOptions(value) {
  let raw = value;

  if (typeof raw === 'string') {
    const trimmed = raw.trim();
    if (trimmed.startsWith('[')) {
      try {
        raw = JSON.parse(trimmed);
      } catch (e) {
        raw = [];
      }
    } else {
      raw = trimmed.split(/[、,，|/]/).map(item => item.trim()).filter(Boolean);
    }
  }

  if (!Array.isArray(raw)) return [];

  return raw
    .flat(Infinity)
    .filter(item => typeof item === 'string')
    .map(item => item.replace(/^[A-D][.、\s]+/i, '').trim())
    .filter(Boolean)
    .slice(0, 4);
}

function isCompleteAssess(tags, body, options, expectedQ = null) {
  if (tags.PHASE !== 'ASSESS') return false;
  if (expectedQ !== null && parseInt(tags.Q) !== expectedQ) return false;
  const scene = typeof body === 'object' ? body.scene : body;
  return typeof scene === 'string' && scene.trim().length > 0 && normalizeOptions(options).length >= 2 && normalizeOptions(options).length <= 4;
}

function parseIncrementalJson(text) {
  if (typeof text !== 'string' || !text.trim()) return null;
  let cleanText = text.trim();

  if (cleanText.startsWith('data: ')) {
    cleanText = cleanText.slice(6).trim();
  }

  if (!cleanText || cleanText === '[DONE]') return null;

  try {
    const data = JSON.parse(cleanText);
    return data;
  } catch (e) {
    return null;
  }
}

function decodeJsonString(value) {
  try {
    return JSON.parse(`"${value}"`);
  } catch (e) {
    return value;
  }
}

function readJsonStringFrom(text, quoteIndex) {
  let raw = '';
  let closed = false;
  let endIndex = text.length;

  for (let i = quoteIndex + 1; i < text.length; i++) {
    const ch = text[i];

    if (ch === '\\') {
      if (i + 1 < text.length) {
        raw += ch + text[i + 1];
        i++;
      }
      continue;
    }

    if (ch === '"') {
      closed = true;
      endIndex = i;
      break;
    }

    raw += ch;
  }

  return { value: decodeJsonString(raw), closed, endIndex };
}

function extractPartialStringField(text, key) {
  const keyIndex = text.indexOf(`"${key}"`);
  if (keyIndex < 0) return null;

  const colonIndex = text.indexOf(':', keyIndex);
  if (colonIndex < 0) return null;

  const quoteIndex = text.indexOf('"', colonIndex);
  if (quoteIndex < 0) return null;

  return readJsonStringFrom(text, quoteIndex);
}

function extractPartialOptions(text) {
  const optionsStart = text.indexOf('"options"');
  if (optionsStart < 0) return [];

  const bracketStart = text.indexOf('[', optionsStart);
  if (bracketStart < 0) return [];

  const options = [];
  let index = bracketStart + 1;

  while (index < text.length && options.length < 4) {
    while (index < text.length && /[\s,]/.test(text[index])) index++;
    if (index >= text.length || text[index] === ']') break;
    if (text[index] !== '"') break;

    const option = readJsonStringFrom(text, index);
    if (option.value) {
      options.push(option.value);
    }

    if (!option.closed) break;
    index = option.endIndex + 1;
    while (index < text.length && text[index] !== ',' && text[index] !== ']') index++;
    if (text[index] === ']') break;
    index++;
  }

  return options;
}

function buildPartialObject(incompleteJson) {
  const result = {};
  let buffer = incompleteJson.trim();

  if (!buffer.startsWith('{')) {
    const braceIndex = buffer.indexOf('{');
    if (braceIndex === -1) return result;
    buffer = buffer.substring(braceIndex);
  }

  const commentField = extractPartialStringField(buffer, 'comment');
  if (commentField) result.comment = commentField.value;

  const sceneField = extractPartialStringField(buffer, 'scene');
  if (sceneField) result.scene = sceneField.value;

  const phaseMatch = buffer.match(/"phase"\s*:\s*"([^"]*)"/);
  if (phaseMatch) result.phase = phaseMatch[1];

  const qMatch = buffer.match(/"q"\s*:\s*(\d+)/);
  if (qMatch) result.q = parseInt(qMatch[1]);

  const nbMatch = buffer.match(/"nb"\s*:\s*(-?\d+)/);
  if (nbMatch) result.nb = parseInt(nbMatch[1]);

  const bhMatch = buffer.match(/"bh"\s*:\s*(-?\d+)/);
  if (bhMatch) result.bh = parseInt(bhMatch[1]);

  const tfMatch = buffer.match(/"tf"\s*:\s*(-?\d+)/);
  if (tfMatch) result.tf = parseInt(tfMatch[1]);

  const ipMatch = buffer.match(/"ip"\s*:\s*(-?\d+)/);
  if (ipMatch) result.ip = parseInt(ipMatch[1]);

  const nextDimMatch = buffer.match(/"next_dim"\s*:\s*"([^"]*)"/);
  if (nextDimMatch) result.next_dim = nextDimMatch[1];

  const canConcludeMatch = buffer.match(/"can_conclude"\s*:\s*(true|false)/);
  if (canConcludeMatch) result.can_conclude = canConcludeMatch[1] === 'true';

  result.options = extractPartialOptions(buffer);
  return result;
}

function renderQuestionIncremental(partialData, options = [], settings = {}) {
  const questionArea = document.getElementById('question-area');
  options = normalizeOptions(options);
  let commentBubble = document.getElementById('incremental-comment');
  let questionCard = document.getElementById('incremental-card');
  let optionsContainer = document.getElementById('incremental-options');

  if (!commentBubble || !questionCard || !optionsContainer) {
    questionArea.innerHTML = `
      <div id="incremental-comment" class="comment-bubble" style="opacity:0;transition:opacity 0.3s;"></div>
      <div id="incremental-card" class="question-card" style="opacity:1;transition:opacity 0.3s;">
        <div id="incremental-label" class="question-label">第 ${partialData.q || currentQuestion || 1} 题</div>
        <div id="incremental-scene" class="question-text stream-placeholder">正在生成题目<span class="typing-dots"></span></div>
      </div>
      <div id="incremental-options" class="options" style="opacity:0;transition:opacity 0.3s;"></div>
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
    sceneEl.classList.remove('stream-placeholder');
    sceneEl.textContent = partialData.scene;
    if (questionCard.style.opacity === '0') {
      setTimeout(() => questionCard.style.opacity = '1', 50);
    }
  }

  if (options.length > 0) {
    const letters = ['A', 'B', 'C', 'D'];
    options.slice(0, 4).forEach((opt, i) => {
      const optText = typeof opt === 'string' ? opt : '';
      const existingBtn = optionsContainer.children[i];
      const optionText = escHtml(optText);
      if (existingBtn) {
        existingBtn.dataset.optionText = optText;
        existingBtn.disabled = !settings.enableOptions;
        existingBtn.innerHTML = `<span class="letter">${letters[i]}</span>${optionText}`;
        existingBtn.onclick = () => selectOption(letters[i], optText);
        return;
      }

      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.dataset.optionText = optText;
      btn.disabled = !settings.enableOptions;
      btn.innerHTML = `<span class="letter">${letters[i]}</span>${optionText}`;
      btn.addEventListener('click', () => selectOption(letters[i], optText));
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

function parseResponse(text) {
  const json = extractJsonFromText(text);
  if (json) {
    if (json.phase === 'RESULT') {
      const tags = {
        PHASE: 'RESULT',
        TYPE: json.type || 'UNKNOWN',
        NAME: json.name || '未知人格',
        ONELINE: json.oneline || '',
        SCENE: json.scene || '',
        ADAPT: json.adapt || '',
        CRASH: json.crash || ''
      };
      return { tags, options: [], body: json, isJson: true };
    }

    if (json.phase === 'ASSESS') {
      const normalizedOptions = normalizeOptions(json.options);
      const tags = {
        PHASE: 'ASSESS',
        Q: String(json.q || 0),
        NB: String(json.nb || 0),
        BH: String(json.bh || 0),
        TF: String(json.tf || 0),
        IP: String(json.ip || 0),
        NEXT_DIM: json.next_dim || 'NB',
        CAN_CONCLUDE: json.can_conclude ? 'true' : 'false'
      };
      return {
        tags,
        options: normalizedOptions,
        body: { ...json, options: normalizedOptions },
        isJson: true
      };
    }
  }

  return { tags: { PHASE: 'ERROR' }, options: [], body: 'AI 回复格式异常，请重试', isJson: false };
}

function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const page = document.getElementById(pageId);
  if (page) {
    page.classList.add('active');
  }

  if (pageId === 'page-test') {
    updateStepper('test');
  }
}

async function startTest() {
  showPage('page-test');
  await sendMessage('开始测试');
}

let preloadCache = {};
let preloadMessageMap = {};
let preloadVersion = 0;
let activeQuestionRequestId = 0;

let preloadStatus = 'idle';
let preloadCount = 0;
let preloadTotal = 0;

function clearPreloadCache() {
  Object.keys(preloadCache).forEach(k => delete preloadCache[k]);
  Object.keys(preloadMessageMap).forEach(k => delete preloadMessageMap[k]);
  preloadVersion++;
  preloadStatus = 'idle';
  preloadCount = 0;
  preloadTotal = 0;
}

function showLoadingAnimation() {
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

function preloadNextQuestions(options) {
  if (!preloadEnabled) return;
  options = normalizeOptions(options);
  if (!conversationId || !options.length) return;

  clearPreloadCache();
  const requestPreloadVersion = preloadVersion;

  preloadStatus = 'loading';
  preloadCount = 0;
  preloadTotal = options.length;
  updatePreloadStatusUI();

  options.forEach(opt => {
    const preloadMessage = canConclude ? `[CAN_CONCLUDE:true] ${opt}` : opt;
    fetch(`${API_URL}/chat/preload`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: preloadMessage,
        conversation_id: conversationId,
        theme: selectedTheme,
        style: selectedStyle
      })
    })
    .then(r => r.json())
    .then(data => {
      if (requestPreloadVersion !== preloadVersion) return;
      if (!data.error && data.answer !== null && data.answer !== undefined) {
        preloadCache[opt] = data.answer;
        preloadMessageMap[opt] = preloadMessage;
      }
      preloadCount++;
      updatePreloadStatusUI();
      if (preloadCount >= preloadTotal) {
        preloadStatus = 'ready';
        updatePreloadStatusUI();
      }
    })
    .catch(() => {
      if (requestPreloadVersion === preloadVersion) {
        preloadCount++;
        updatePreloadStatusUI();
        if (preloadCount >= preloadTotal) {
          preloadStatus = 'ready';
          updatePreloadStatusUI();
        }
      }
    });
  });
}

function updatePreloadStatusUI() {
  const statusEl = document.getElementById('preload-status');
  if (!statusEl) return;

  if (preloadStatus === 'loading') {
    statusEl.innerHTML = `<div class="preload-indicator loading"><div class="preload-spinner"></div>下一题准备中 (${preloadCount}/${preloadTotal})...</div>`;
  } else if (preloadStatus === 'ready') {
    statusEl.innerHTML = '<div class="preload-indicator ready"><span class="check-icon">✓</span> 下一题已就绪</div>';
  } else {
    statusEl.innerHTML = '';
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function showStreamingQuestionShell() {
  const questionArea = document.getElementById('question-area');
  const nextQuestion = currentQuestion > 0 ? currentQuestion + 1 : 1;
  const progressText = document.getElementById('progress-text');
  const progressFill = document.getElementById('progress-fill');

  if (progressText) {
    progressText.textContent = `第 ${nextQuestion} 题`;
  }
  if (progressFill) {
    progressFill.style.width = `${Math.min(nextQuestion / maxQuestions * 100, 100)}%`;
  }

  questionArea.innerHTML = `
    <div id="incremental-comment" class="comment-bubble" style="opacity:0;transition:opacity 0.3s;"></div>
    <div id="incremental-card" class="question-card" style="opacity:1;transition:opacity 0.3s;">
      <div id="incremental-label" class="question-label">第 ${nextQuestion} 题</div>
      <div id="incremental-scene" class="question-text stream-placeholder">正在生成题目<span class="typing-dots"></span></div>
    </div>
    <div id="incremental-options" class="options" style="opacity:0;transition:opacity 0.3s;"></div>
    <div id="preload-status" class="preload-status-container" data-streaming="true"></div>
  `;
}

function showStreamingIntroShell() {
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
      <div style="font-size: 3.5rem; margin-bottom: 20px;">🎭</div>
      <div id="incremental-intro" class="question-text stream-placeholder" style="font-size: 1.15rem; line-height: 1.9; margin-bottom: 40px; color: var(--text-primary);">
        正在酝酿开场白<span class="typing-dots"></span>
      </div>
      <button class="btn btn-primary" disabled style="padding: 14px 48px; font-size: 1.05rem; opacity:0.55;">
        开始答题 →
      </button>
    </div>
  `;
}

function renderIntroIncremental(comment) {
  const introEl = document.getElementById('incremental-intro');
  if (!introEl || !comment) return;

  introEl.classList.remove('stream-placeholder');
  introEl.textContent = comment;
}

async function playAnswerTypewriter(answerText, requestId) {
  const expectedQuestion = currentQuestion > 0 ? currentQuestion + 1 : 1;

  if (currentQuestion === 0 && !document.getElementById('incremental-intro')) {
    showStreamingIntroShell();
  } else if (currentQuestion > 0 || !document.getElementById('incremental-card')) {
    showStreamingQuestionShell();
  }

  for (let i = 1; i <= answerText.length; i += 2) {
    if (requestId !== activeQuestionRequestId) return;

    const partialObj = buildPartialObject(answerText.slice(0, i));
    if (partialObj.phase === 'ASSESS') {
      partialObj.q = expectedQuestion;
    }

    const partialOptions = partialObj.options || [];
    if (currentQuestion === 0 && partialObj.comment) {
      renderIntroIncremental(partialObj.comment);
    } else if (partialObj.comment || partialObj.scene || partialOptions.length) {
      renderQuestionIncremental(partialObj, partialOptions, { enableOptions: false });
    }

    await sleep(8);
  }
}

async function sendMessage(message) {
  const requestId = ++activeQuestionRequestId;

  if (canConclude) {
    message = '[CAN_CONCLUDE:true] ' + message;
    canConclude = false;
  }

  if (currentQuestion === 0) {
    showStreamingIntroShell();
  } else {
    showStreamingQuestionShell();
  }

  try {
    const response = await fetch(`${API_URL}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        conversation_id: conversationId,
        theme: selectedTheme,
        style: selectedStyle
      })
    });

    if (requestId !== activeQuestionRequestId) return;

    if (response.headers.get('content-type')?.includes('text/event-stream') || response.headers.get('content-type')?.includes('application/stream+json')) {
      await handleStreamResponse(response, requestId, message);
    } else {
      await handleNonStreamResponse(response, requestId, message);
    }

  } catch (error) {
    try {
      await sendMessageNonStream(message, requestId);
    } catch (fallbackError) {
      answerLocked = false;
      const questionArea = document.getElementById('question-area');
      questionArea.innerHTML = `
        <div class="question-card">
          <p style="color: var(--accent-rose);">❌ 加载失败: ${escHtml(fallbackError.message || error.message || '未知错误')}</p>
        </div>
      `;
      const retryBtn = document.createElement('button');
      retryBtn.className = 'btn btn-outline';
      retryBtn.style.marginTop = '12px';
      retryBtn.textContent = '重试';
      retryBtn.addEventListener('click', () => sendMessage(message));
      questionArea.querySelector('.question-card').appendChild(retryBtn);
    }
  }
}

async function sendMessageNonStream(message, requestId) {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      conversation_id: conversationId,
      theme: selectedTheme,
      style: selectedStyle
    })
  });

  await handleNonStreamResponse(response, requestId, message);
}

async function handleStreamResponse(response, requestId, originalMessage) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let fullAnswer = '';
  let receivedFirstToken = false;
  let options = [];
  let conversationIdFromStream = conversationId;
  const expectedQuestion = currentQuestion > 0 ? currentQuestion + 1 : 1;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    if (requestId !== activeQuestionRequestId) return;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      const data = parseIncrementalJson(trimmed);
      if (!data) continue;

      if (data.conversation_id) {
        conversationIdFromStream = data.conversation_id;
      }

      if (data.event === 'done' || data.type === 'done' || data.done) {
        if (data.answer) {
          fullAnswer = data.answer;
        }
        if (data.options) {
          options = data.options;
        }
        break;
      }

      if (data.event === 'error' || data.error) {
        throw new Error(data.error || '流式输出失败');
      }

      if (data.event === 'first_token' || data.type === 'first_token' || (!receivedFirstToken && data)) {
        if (!receivedFirstToken) {
          receivedFirstToken = true;
          if (currentQuestion === 0 && !document.getElementById('incremental-intro')) {
            showStreamingIntroShell();
          }
        }
      }

      if (data.event === 'chunk' || data.type === 'chunk' || data.answer || data.content) {
        const chunk = data.answer || data.content || data.chunk || '';
        fullAnswer += chunk;

        const partialObj = buildPartialObject(fullAnswer);
        if (partialObj.phase === 'ASSESS') {
          partialObj.q = expectedQuestion;
        }
        const partialOptions = partialObj.options && partialObj.options.length ? partialObj.options : options;
        if (currentQuestion === 0 && partialObj.comment) {
          renderIntroIncremental(partialObj.comment);
        } else if (partialObj.comment || partialObj.scene || partialOptions.length) {
          renderQuestionIncremental(partialObj, partialOptions, { enableOptions: false });
        }

        if (data.options) {
          options = data.options;
          if (currentQuestion === 0 && partialObj.comment) {
            renderIntroIncremental(partialObj.comment);
          } else if (partialObj.comment || partialObj.scene || options.length) {
            renderQuestionIncremental(partialObj, options, { enableOptions: false });
          }
        }
      }
    }
  }

  if (requestId !== activeQuestionRequestId) return;
  conversationId = conversationIdFromStream;

  if (fullAnswer) {
    processFinalAnswer(fullAnswer, options, requestId, { skipIntro: currentQuestion > 0, retryMessage: originalMessage });
  }
}

async function handleNonStreamResponse(response, requestId, originalMessage) {
  const data = await response.json();

  if (data.error) {
    throw new Error(data.error);
  }

  if (requestId !== activeQuestionRequestId) return;

  conversationId = data.conversation_id;

  const parsed = parseResponse(data.answer);
  if (parsed.tags.PHASE === 'ASSESS') {
    await playAnswerTypewriter(data.answer, requestId);
  }

  processFinalAnswer(data.answer, data.options || [], requestId, { retryMessage: originalMessage });
}

function processFinalAnswer(answerText, options, requestId, settings = {}) {
  if (requestId !== activeQuestionRequestId) return;

  const { tags, options: parsedOptions, body } = parseResponse(answerText);
  const finalOptions = normalizeOptions(options && options.length > 0 ? options : parsedOptions);

  if (tags.PHASE === 'RESULT') {
    incompleteRetryCount = 0;
    showResult(answerText, tags);
    answerLocked = false;
    return;
  }

  const expectedQuestion = currentQuestion > 0 ? currentQuestion + 1 : 1;
  if (!isCompleteAssess(tags, body, finalOptions, expectedQuestion)) {
    answerLocked = false;
    incompleteRetryCount++;
    const questionArea = document.getElementById('question-area');
    if (incompleteRetryCount > MAX_INCOMPLETE_RETRIES) {
      questionArea.innerHTML = `
        <div class="question-card">
          <p style="color: var(--accent-rose);">AI 状态不佳，请稍后重试</p>
        </div>
      `;
      const retryBtn = document.createElement('button');
      retryBtn.className = 'btn btn-outline';
      retryBtn.style.marginTop = '12px';
      retryBtn.textContent = '重试';
      retryBtn.addEventListener('click', () => {
        incompleteRetryCount = 0;
        sendMessage(settings.retryMessage || '请重新生成这一题');
      });
      questionArea.querySelector('.question-card').appendChild(retryBtn);
      return;
    }
    questionArea.innerHTML = `
      <div class="question-card">
        <p style="color: var(--accent-amber);">题目生成不完整，正在重试...</p>
      </div>
    `;
    if (requestId === activeQuestionRequestId) {
      sendMessage(settings.retryMessage || '请重新生成这一题');
    }
    return;
  }

  incompleteRetryCount = 0;

  canConclude = tags.CAN_CONCLUDE === 'true';

  currentQuestion = parseInt(tags.Q) || currentQuestion + 1;
  updateProgress();

  scores.nb = parseInt(tags.NB) || scores.nb;
  scores.bh = parseInt(tags.BH) || scores.bh;
  scores.tf = parseInt(tags.TF) || scores.tf;
  scores.ip = parseInt(tags.IP) || scores.ip;
  nextDim = tags.NEXT_DIM || nextDim;

  if (parseInt(tags.Q) === 1 && !settings.skipIntro) {
    if (typeof body === 'object' && body.comment) {
      renderIntro(body.comment, body.scene, finalOptions, tags);
    } else {
      const idx = typeof body === 'string' ? body.indexOf('\n\n') : -1;
      if (idx > 0) {
        const intro = body.substring(0, idx).trim();
        const scene = body.substring(idx + 2).trim();
        renderIntro(intro, scene, finalOptions, tags);
      } else {
        renderQuestion(body, finalOptions, tags);
      }
    }
  } else {
    renderQuestion(body, finalOptions, tags);
  }
  answerLocked = false;
  saveSessionSnapshot(answerText);
}

let firstQuestionCache = null;

function renderIntro(intro, scene, options, tags) {
  firstQuestionCache = { scene, options, tags };
  const questionArea = document.getElementById('question-area');
  questionArea.innerHTML = `
    <div class="question-card intro-card">
      <div style="font-size: 3.5rem; margin-bottom: 20px;">🎉</div>
      <div class="question-text" style="font-size: 1.15rem; line-height: 1.9; margin-bottom: 40px; color: var(--text-primary);">${escHtml(intro).replace(/\n/g, '<br>')}</div>
      <button class="btn btn-primary btn-glow" onclick="showFirstQuestion()" style="padding: 14px 48px; font-size: 1.05rem;">
        开始答题 →
      </button>
      <div id="preload-status" class="preload-status-container" style="margin-top: 20px;"></div>
    </div>
  `;

  preloadNextQuestions(options);
}

function showFirstQuestion() {
  if (!firstQuestionCache) return;
  const { scene, options, tags } = firstQuestionCache;
  firstQuestionCache = null;
  renderQuestion(scene, options, tags, { skipPreload: true });
}

function renderQuestion(body, options, tags, settings = {}) {
  const questionArea = document.getElementById('question-area');
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
      <div class="question-label">第 ${currentQuestion} 题</div>
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
    btn.addEventListener('click', () => selectOption(letters[i], optText));
    optionsContainer.appendChild(btn);
  });

  if (!settings.skipPreload) {
    preloadNextQuestions(normalizedOptions);
  } else {
    updatePreloadStatusUI();
  }
}

async function selectOption(letter, text) {
  if (answerLocked) return;
  answerLocked = true;

  if (preloadCache[text]) {
    const requestId = ++activeQuestionRequestId;
    const cachedAnswer = preloadCache[text];
    const committedMessage = preloadMessageMap[text] || text;
    clearPreloadCache();

    const { tags, options, body } = parseResponse(cachedAnswer);

    if (tags.PHASE === 'RESULT') {
      showResult(cachedAnswer, tags);
      fetch(`${API_URL}/chat/preload/commit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: committedMessage, conversation_id: conversationId })
      }).then(r => r.json()).then(d => { if (d.conversation_id) conversationId = d.conversation_id; }).catch(() => {});
      return;
    }

    if (!isCompleteAssess(tags, body, options, currentQuestion + 1)) {
      answerLocked = false;
      await sendMessage(text);
      return;
    }

    canConclude = tags.CAN_CONCLUDE === 'true';

    currentQuestion = parseInt(tags.Q) || currentQuestion + 1;
    updateProgress();
    scores.nb = parseInt(tags.NB) || scores.nb;
    scores.bh = parseInt(tags.BH) || scores.bh;
    scores.tf = parseInt(tags.TF) || scores.tf;
    scores.ip = parseInt(tags.IP) || scores.ip;
    nextDim = tags.NEXT_DIM || nextDim;

    renderQuestion(body, options, tags, { skipPreload: true });
    saveSessionSnapshot(cachedAnswer);

    try {
      const response = await fetch(`${API_URL}/chat/preload/commit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: committedMessage, conversation_id: conversationId })
      });

      if (response.status === 409) {
        console.warn('预加载提交失败（草稿过期），回退到流式路径');
        answerLocked = false;
        preloadCache = {};
        preloadMessageMap = {};
        await sendMessage(committedMessage);
        return;
      }

      const data = await response.json();
      if (requestId !== activeQuestionRequestId) return;
      if (data.conversation_id) conversationId = data.conversation_id;
      if (!data.error && normalizeOptions(options).length) {
        preloadNextQuestions(options);
      }
    } catch (e) {
      console.warn('预加载提交网络异常，回退到流式路径', e);
      answerLocked = false;
      preloadCache = {};
      preloadMessageMap = {};
      await sendMessage(committedMessage);
      return;
    }
    answerLocked = false;
    return;
  }

  await sendMessage(text);
}

function updateProgress() {
  const percent = Math.min(currentQuestion / maxQuestions * 100, 100);
  const fill = document.getElementById('progress-fill');
  const text = document.getElementById('progress-text');
  if (fill) fill.style.width = `${percent}%`;
  if (text) text.textContent = `第 ${currentQuestion} 题`;
}

const SESSION_STORAGE_KEY = 'nbti-session';

function saveSessionSnapshot(lastAnswer) {
  try {
    if (!conversationId || typeof lastAnswer !== 'string' || !lastAnswer) return;
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
      conversationId,
      currentQuestion,
      scores,
      nextDim,
      canConclude,
      lastAnswer,
      selectedTheme,
      selectedStyle
    }));
  } catch (e) {}
}

function clearSessionSnapshot() {
  try {
    localStorage.removeItem(SESSION_STORAGE_KEY);
  } catch (e) {}
}

function restoreSessionSnapshot() {
  let snapshot = null;
  try {
    snapshot = JSON.parse(localStorage.getItem(SESSION_STORAGE_KEY) || 'null');
  } catch (e) {
    snapshot = null;
  }

  if (!snapshot || !snapshot.conversationId || typeof snapshot.lastAnswer !== 'string' || !snapshot.lastAnswer) {
    clearSessionSnapshot();
    return;
  }

  try {
    if (parseResponse(snapshot.lastAnswer).tags.PHASE !== 'ASSESS') {
      clearSessionSnapshot();
      return;
    }
    conversationId = snapshot.conversationId;
    currentQuestion = Math.max((parseInt(snapshot.currentQuestion) || 1) - 1, 0);
    scores = { nb: 0, bh: 0, tf: 0, ip: 0, ...(snapshot.scores || {}) };
    nextDim = snapshot.nextDim || 'NB';
    canConclude = snapshot.canConclude === true;
    answerLocked = false;
    if (snapshot.selectedTheme) selectedTheme = snapshot.selectedTheme;
    if (snapshot.selectedStyle) selectedStyle = snapshot.selectedStyle;
    showPage('page-test');
    processFinalAnswer(snapshot.lastAnswer, [], ++activeQuestionRequestId, { skipIntro: true });
  } catch (e) {
    clearSessionSnapshot();
    restart();
  }
}

function showResult(answer, tags) {
  clearSessionSnapshot();
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

  currentResult = {
    type, name, oneline, scene, adapt, crash,
    interpretation, pseudo_science: pseudoScience, closing
  };

  const themeMap = {
    workplace: { id: 'workplace', name: '职场人格', icon: '💼' },
    animal: { id: 'animal', name: '动物系人格', icon: '🐾' },
    color: { id: 'color', name: '色彩人格', icon: '🎨' }
  };
  const currentThemeInfo = themeMap[selectedTheme] || themeMap.workplace;

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
    window.NBTIRadar.renderRadar('radar-chart', scores);
  }
}

let toastTimer = null;
function showToast(msg) {
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

function setBtnLoading(btn, loading, loadingText) {
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

function openPosterModal(canvas) {
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
      if (window.NBTIPoster && currentResult) {
        const themeMap = {
          workplace: { id: 'workplace', name: '职场人格', icon: '💼' },
          animal: { id: 'animal', name: '动物系人格', icon: '🐾' },
          color: { id: 'color', name: '色彩人格', icon: '🎨' }
        };
        const themeInfo = themeMap[selectedTheme] || themeMap.workplace;
        window.NBTIPoster.download(currentResult, scores, {
          theme: selectedTheme,
          themeInfo: themeInfo,
          slogan: themeInfo.name
        }).catch(() => showToast('下载失败，请重试'));
      }
    });
  }
  modal.querySelector('img').src = canvas.toDataURL('image/png');
  modal.classList.add('open');
}

async function sharePoster() {
  if (!window.NBTIPoster) {
    alert('海报模块未加载，无法生成分享海报');
    return;
  }
  if (!currentResult) {
    showToast('还没有生成结果');
    return;
  }
  const btn = document.getElementById('btn-share-poster');
  setBtnLoading(btn, true, '生成中…');
  try {
    const themeMap = {
      workplace: { id: 'workplace', name: '职场人格', icon: '💼' },
      animal: { id: 'animal', name: '动物系人格', icon: '🐾' },
      color: { id: 'color', name: '色彩人格', icon: '🎨' }
    };
    const themeInfo = themeMap[selectedTheme] || themeMap.workplace;
    const canvas = await window.NBTIPoster.generate(currentResult, scores, {
      theme: selectedTheme,
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

async function copyResultText() {
  if (!window.NBTIPoster || !currentResult) {
    showToast('还没有生成结果');
    return;
  }
  const btn = document.getElementById('btn-copy-text');
  setBtnLoading(btn, true, '复制中…');
  try {
    const themeNameMap = {
      workplace: '职场人格',
      animal: '动物人格',
      color: '色彩人格'
    };
    const hashtagMap = {
      workplace: ['#人格测试', '#NBTI', '#职场人格'],
      animal: ['#动物人格', '#人格测试', '#NBTI'],
      color: ['#色彩人格', '#人格测试', '#NBTI']
    };
    const themeName = themeNameMap[selectedTheme] || 'NBTI';
    const hashtags = hashtagMap[selectedTheme] || ['#人格测试', '#NBTI'];
    const text = window.NBTIPoster.generateCopyText(currentResult, themeName, hashtags);
    await copyText(text);
    showToast('文案已复制，快去发朋友圈！');
  } catch (e) {
    console.error('复制失败', e);
    showToast('复制失败，请手动复制');
  } finally {
    setBtnLoading(btn, false);
  }
}

async function copyText(text) {
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

async function shareLink() {
  if (!currentResult) {
    showToast('还没有生成结果');
    return;
  }
  const btn = document.getElementById('btn-share-link');
  setBtnLoading(btn, true, '复制中…');
  try {
    const resp = await fetch(`${API_URL}/share`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ result: currentResult, scores })
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

function drawAvatar(elementId, personality) {
  const container = document.getElementById(elementId);
  if (!container) return;
  if (!window.NBTIAvatar) {
    container.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;color:var(--text-secondary);font-size:0.9rem;">头像生成器加载失败</div>';
    return;
  }
  container.innerHTML = window.NBTIAvatar.generateSvgAvatar(personality);
}

function refreshAvatar() {
  const container = document.getElementById('result-avatar');
  if (!container) return;
  const codeEl = document.querySelector('.code');
  const personality = codeEl ? codeEl.textContent.trim() : 'NBTI';
  drawAvatar('result-avatar', personality);
}

function downloadAvatar() {
  if (!window.NBTIAvatar) {
    alert('头像生成器未加载，无法下载');
    return;
  }
  const container = document.getElementById('result-avatar');
  if (!container) return;
  const codeEl = document.querySelector('.code');
  const personality = codeEl ? codeEl.textContent.trim() : 'NBTI';

  const svg = window.NBTIAvatar.generateSvgAvatar(personality);
  const svgBlob = new Blob([svg], { type: 'image/svg+xml;charset=utf-8' });
  const url = URL.createObjectURL(svgBlob);

  const link = document.createElement('a');
  link.download = `nbti-avatar-${personality}.svg`;
  link.href = url;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 100);
}

function restart() {
  conversationId = '';
  currentQuestion = 0;
  scores = { nb: 0, bh: 0, tf: 0, ip: 0 };
  nextDim = 'NB';
  canConclude = false;
  answerLocked = false;
  incompleteRetryCount = 0;
  firstQuestionCache = null;
  clearSessionSnapshot();
  clearPreloadCache();
  updateProgress();
  welcomeStep = 'theme';
  document.getElementById('progress-stepper').style.display = 'none';
  showPage('page-welcome');
  goToStep('theme');
}

(function initTheme() {
  const STORAGE_KEY = 'nbti-theme';
  const root = document.documentElement;
  const iconEl = document.getElementById('theme-icon');
  const toggleBtn = document.getElementById('theme-toggle');

  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function applyTheme(theme) {
    if (theme === 'light') {
      root.setAttribute('data-theme', 'light');
      if (iconEl) iconEl.textContent = '☀️';
    } else {
      root.setAttribute('data-theme', 'dark');
      if (iconEl) iconEl.textContent = '🌙';
    }
  }

  function getEffectiveTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored || getSystemTheme();
  }

  applyTheme(getEffectiveTheme());

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function() {
      const current = root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem(STORAGE_KEY, next);
      applyTheme(next);
    });
  }

  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', function(e) {
    if (!localStorage.getItem(STORAGE_KEY)) {
      applyTheme(e.matches ? 'light' : 'dark');
    }
  });
})();

loadThemesAndStyles();
restoreSessionSnapshot();
