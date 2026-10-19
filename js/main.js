// NBTI 前端入口：把各 ES Module 装配起来，串联初始化，
// 并把需要被 HTML 内联 onclick 调用的函数挂到 window 上。

import { loadConfig } from './api.js';
import {
  bindFlowHandlers,
  loadThemesAndStyles,
  selectTheme,
  selectStyle,
  goBackToTheme,
  goBackToStyle,
  refreshAvatar,
  downloadAvatar,
  showFirstQuestion
} from './render.js';
import {
  selectOption,
  preloadNextQuestions,
  updatePreloadStatusUI,
  restart
} from './preload.js';
import { parseResponse, processFinalAnswer, startTest } from './stream.js';
import { restoreSessionSnapshot, clearSessionSnapshot } from './session.js';
import { warmupFirstQuestion, resetWarmup } from './warmup.js';
import { initFastMode, bindFastModeToggle, setFastMode, isFastMode } from './fastmode.js';

// 装配点：render 层需要的流程回调由这里注入，避免 render 与 preload/stream 循环 import
bindFlowHandlers({
  selectOption,
  preloadNextQuestions,
  updatePreloadStatusUI,
  clearSessionSnapshot,
  warmupFirstQuestion,
  resetWarmup
});

// 挂到 window，供 HTML 内联 onclick / 动态生成的 onclick 调用
window.selectTheme = selectTheme;
window.selectStyle = selectStyle;
window.goBackToTheme = goBackToTheme;
window.goBackToStyle = goBackToStyle;
window.startTest = startTest;
window.showFirstQuestion = showFirstQuestion;
window.refreshAvatar = refreshAvatar;
window.downloadAvatar = downloadAvatar;
window.restart = restart;
// 供内联 onclick（快速模式提示条）调用
window.setFastMode = setFastMode;
window.isFastMode = isFastMode;

// 页面明暗主题切换（与测试主题无关）
function initTheme() {
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
}

// ---- 初始化 ----
loadConfig();
initTheme();
initFastMode();
bindFastModeToggle();
loadThemesAndStyles();
restoreSessionSnapshot({ parseResponse, processFinalAnswer, restart });
