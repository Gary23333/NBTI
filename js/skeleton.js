// NBTI 骨架屏：进入测试页 / 切题瞬间先渲染“结构化 shimmer 占位”，
// 而不是空白或仅一个 spinner。
//
// 设计要点：骨架直接内嵌在流式外壳（streaming shell）内部——
//   * 卡片区：真实卡片 + shimmer 线条；
//   * 选项区：真实选项容器 + 四条选项骨架；
// 这样 AI 首 token 到达时，只需移除对应骨架节点并写入真实内容，
// 骨架与真实内容不会同时叠加，避免布局跳动，切换平滑。
//
// 本模块只负责生成 HTML 字符串与占位节点，无副作用、无外部依赖。

// 选项字母，与 render 层保持一致
const LETTERS = ['A', 'B', 'C', 'D'];

// 生成题目区骨架线条（卡片内 shimmer）
export function skeletonLines(count = 2) {
  const widths = ['sk-line-90', 'sk-line-70', 'sk-line-50', 'sk-line-80'];
  let html = '';
  for (let i = 0; i < count; i++) {
    html += `<div class="sk-line ${widths[i % widths.length]}"></div>`;
  }
  return html;
}

// 生成选项骨架（每条含字母圆点 + 线条）
export function skeletonOptions(count = 4) {
  let html = '';
  for (let i = 0; i < count; i++) {
    html += `
      <div class="skeleton-option">
        <span class="sk-letter">${LETTERS[i % LETTERS.length]}</span>
        <div class="sk-line sk-line-60"></div>
      </div>`;
  }
  return html;
}

// 卡片内的骨架块（用于“正在生成题目”阶段）；caption 为可选的等待文案
export function skeletonCardBlock(caption) {
  const c = caption ? `<div class="skeleton-caption">${caption}<span class="typing-dots"></span></div>` : '';
  return `<div id="incremental-skeleton" class="skeleton-block">${skeletonLines(2)}${c}</div>`;
}

// 独立运行时（非流式）也可复用的整块题目骨架 HTML
export function questionSkeletonHtml(nextQuestion) {
  const n = nextQuestion || 1;
  return `
    <div class="comment-bubble skeleton-comment">
      <div class="sk-line sk-line-40"></div>
    </div>
    <div class="question-card skeleton-card">
      <div class="question-label">第 ${n} 题</div>
      ${skeletonLines(2)}
    </div>
    <div class="options skeleton-options">${skeletonOptions(4)}</div>
    <div class="preload-status-container"></div>
  `;
}
