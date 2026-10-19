// NBTI API 基址、fetch 封装与运行配置加载

import { state } from './state.js';

// API 基址（前端服务会把 /api/* 代理到后端）
export const API_URL = '/api';

// fetch 封装：统一拼上 API 基址
export function apiFetch(path, options) {
  return fetch(`${API_URL}${path}`, options);
}

// 加载后端运行配置（min/max 题目数、是否开启预载）
export async function loadConfig() {
  if (state.configLoaded) return;
  state.configLoaded = true;
  try {
    const resp = await apiFetch('/config');
    const cfg = await resp.json();
    if (typeof cfg.min_questions === 'number' && cfg.min_questions > 0) state.minQuestions = cfg.min_questions;
    if (typeof cfg.max_questions === 'number' && cfg.max_questions > 0) state.maxQuestions = cfg.max_questions;
    if (typeof cfg.preload_enabled === 'boolean') state.preloadEnabled = cfg.preload_enabled;
  } catch (e) {}
}
