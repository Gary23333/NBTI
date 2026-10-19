// NBTI 通用纯函数工具
// 这些函数被 render / stream / preload 多个模块共用，放在叶子模块中，
// 以保证依赖图无环（render 与 stream 之间不能互相 import）。

// HTML 转义
export function escHtml(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// 统一把选项规范成最多 4 条纯文本数组
export function normalizeOptions(value) {
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

// 简单的延时
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
