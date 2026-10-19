// NBTI 首题预热：进入 ready 步骤时提前向后端申请「首题草稿」，
// 用户点击「开始测试」时若草稿可用则直接消费，省去首请求的模型等待时间。
//
// 关键：该端点由后端并行开发，可能尚未就绪。这里必须“优雅降级”——
// 任何 404 / 4xx / 5xx / 网络异常 / 非法响应都只静默跳过，绝不抛出、
// 绝不影响既有主流程（与之前的行为完全一致）。
//
// 依赖方向：state / api / util，均为叶子或下层模块，无循环。

import { state } from './state.js';
import { apiFetch } from './api.js';
import { sleep } from './util.js';

// 触发首题预热请求（幂等：已有草稿或请求在飞行中则直接返回）
export function warmupFirstQuestion() {
  if (state.warmupDraft || state.warmupInFlight) return state.warmupPromise;

  state.warmupInFlight = true;

  state.warmupPromise = (async () => {
    try {
      const resp = await apiFetch('/chat/warmup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: state.conversationId || undefined,
          theme: state.selectedTheme,
          style: state.selectedStyle
        })
      });

      // 端点未就绪（404）或任何非成功响应：静默跳过
      if (!resp || !resp.ok) return;

      const data = await resp.json().catch(() => null);
      if (!data || typeof data.answer !== 'string' || !data.answer) return;

      state.warmupDraft = {
        conversationId: data.conversation_id || '',
        answer: data.answer
      };
    } catch (e) {
      // 网络异常 / JSON 解析异常：静默跳过，不影响主流程
    } finally {
      state.warmupInFlight = false;
      state.warmupPromise = null;
    }
  })();

  return state.warmupPromise;
}

// 在「开始测试」时解析可用草稿：若预热仍在飞行中则等待一小段时间（带超时）
export async function resolveWarmupDraft(timeoutMs = 1500) {
  if (state.warmupDraft) return state.warmupDraft;
  if (!state.warmupPromise) return null;
  try {
    await Promise.race([state.warmupPromise, sleep(timeoutMs)]);
  } catch (e) {}
  return state.warmupDraft;
}

// 丢弃草稿（换主题 / 换风格 / 重开一轮时调用）
export function resetWarmup() {
  state.warmupDraft = null;
  state.warmupPromise = null;
  state.warmupInFlight = false;
}
