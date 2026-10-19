// NBTI「快速模式」：默认开启的前端编排开关。
//   * 开启时：强制尝试预载下一题（即使后端 preload_enabled 为 false）、
//             优先走预载 / 缓存命中路径，并在 ready 步骤给出状态提示；
//   * 关闭时：回到既有默认行为（是否预载完全由后端配置决定）。
// 仅影响前端编排，不要求任何后端改动；用 localStorage 持久化。

import { state } from './state.js';

export const FAST_MODE_STORAGE_KEY = 'nbti-fast-mode';

// 读取持久化的开关值（默认 true）
export function readFastMode() {
  try {
    const raw = localStorage.getItem(FAST_MODE_STORAGE_KEY);
    if (raw === null || raw === undefined) return true;
    return raw === '1' || raw === 'true';
  } catch (e) {
    return true;
  }
}

export function isFastMode() {
  return state.fastMode !== false;
}

// 设置开关并持久化，同时刷新 UI
export function setFastMode(on) {
  state.fastMode = !!on;
  try {
    localStorage.setItem(FAST_MODE_STORAGE_KEY, on ? '1' : '0');
  } catch (e) {}
  updateFastModeUI();
}

// 刷新 ready 步骤中的开关与状态提示
export function updateFastModeUI() {
  const toggle = document.getElementById('fast-mode-toggle');
  if (toggle) toggle.checked = isFastMode();

  const status = document.getElementById('fast-mode-status');
  if (status) {
    if (isFastMode()) {
      status.classList.add('on');
      status.textContent = '⚡ 已开启快速模式 · 优先预载下一题';
    } else {
      status.classList.remove('on');
      status.textContent = '已关闭：使用默认加载方式';
    }
  }
}

// 绑定开关事件（由 main.js 在入口调用）
export function bindFastModeToggle() {
  const toggle = document.getElementById('fast-mode-toggle');
  if (toggle && !toggle.dataset.bound) {
    toggle.dataset.bound = '1';
    toggle.addEventListener('change', () => setFastMode(toggle.checked));
  }
}

// 入口初始化：读持久化值 → 写入状态 → 刷新 UI
export function initFastMode() {
  state.fastMode = readFastMode();
  updateFastModeUI();
}
