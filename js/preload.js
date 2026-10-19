// NBTI 预载编排：预取下一题候选答案、命中时直接提交，以及整轮重置 restart。
// 本模块依赖 render（渲染）、session（快照）、stream（解析与发送），处于依赖图上层。

import { state } from './state.js';
import { apiFetch } from './api.js';
import { normalizeOptions } from './util.js';
import { showResult, renderQuestion, updateProgress, showPage, goToStep } from './render.js';
import { saveSessionSnapshot, clearSessionSnapshot } from './session.js';
import { parseResponse, isCompleteAssess, sendMessage } from './stream.js';
import { isFastMode } from './fastmode.js';
import { resetWarmup } from './warmup.js';

export function updatePreloadStatusUI() {
  const statusEl = document.getElementById('preload-status');
  if (!statusEl) return;

  const fast = isFastMode() ? '<span class="preload-fast-tag">⚡ 快速模式</span>' : '';

  if (state.preloadStatus === 'loading') {
    statusEl.innerHTML = `<div class="preload-indicator loading"><div class="preload-spinner"></div>正在预载下一题 (${state.preloadCount}/${state.preloadTotal})…${fast}</div>`;
  } else if (state.preloadStatus === 'ready') {
    statusEl.innerHTML = `<div class="preload-indicator ready"><span class="check-icon">✓</span> 下一题已就绪${fast}</div>`;
  } else {
    statusEl.innerHTML = '';
  }
}

export function clearPreloadCache() {
  Object.keys(state.preloadCache).forEach(k => delete state.preloadCache[k]);
  Object.keys(state.preloadMessageMap).forEach(k => delete state.preloadMessageMap[k]);
  state.preloadVersion++;
  state.preloadStatus = 'idle';
  state.preloadCount = 0;
  state.preloadTotal = 0;
}

export function preloadNextQuestions(options) {
  // 默认由后端配置决定是否预载；快速模式开启时即使后端关闭也强制尝试预载
  if (!state.preloadEnabled && !isFastMode()) return;
  options = normalizeOptions(options);
  if (!state.conversationId || !options.length) return;

  clearPreloadCache();
  const requestPreloadVersion = state.preloadVersion;

  state.preloadStatus = 'loading';
  state.preloadCount = 0;
  state.preloadTotal = options.length;
  updatePreloadStatusUI();

  options.forEach(opt => {
    const preloadMessage = state.canConclude ? `[CAN_CONCLUDE:true] ${opt}` : opt;
    apiFetch('/chat/preload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: preloadMessage,
        conversation_id: state.conversationId,
        theme: state.selectedTheme,
        style: state.selectedStyle
      })
    })
    .then(r => r.json())
    .then(data => {
      if (requestPreloadVersion !== state.preloadVersion) return;
      if (!data.error && data.answer !== null && data.answer !== undefined) {
        state.preloadCache[opt] = data.answer;
        state.preloadMessageMap[opt] = preloadMessage;
      }
      state.preloadCount++;
      updatePreloadStatusUI();
      if (state.preloadCount >= state.preloadTotal) {
        state.preloadStatus = 'ready';
        updatePreloadStatusUI();
      }
    })
    .catch(() => {
      if (requestPreloadVersion === state.preloadVersion) {
        state.preloadCount++;
        updatePreloadStatusUI();
        if (state.preloadCount >= state.preloadTotal) {
          state.preloadStatus = 'ready';
          updatePreloadStatusUI();
        }
      }
    });
  });
}

export async function selectOption(letter, text) {
  if (state.answerLocked) return;
  state.answerLocked = true;

  if (state.preloadCache[text]) {
    const requestId = ++state.activeQuestionRequestId;
    const cachedAnswer = state.preloadCache[text];
    const committedMessage = state.preloadMessageMap[text] || text;
    clearPreloadCache();

    const { tags, options, body } = parseResponse(cachedAnswer);

    if (tags.PHASE === 'RESULT') {
      showResult(cachedAnswer, tags);
      apiFetch('/chat/preload/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: committedMessage, conversation_id: state.conversationId })
      }).then(r => r.json()).then(d => { if (d.conversation_id) state.conversationId = d.conversation_id; }).catch(() => {});
      return;
    }

    if (!isCompleteAssess(tags, body, options, state.currentQuestion + 1)) {
      state.answerLocked = false;
      await sendMessage(text);
      return;
    }

    state.canConclude = tags.CAN_CONCLUDE === 'true';

    state.currentQuestion = parseInt(tags.Q) || state.currentQuestion + 1;
    updateProgress();
    state.scores.nb = parseInt(tags.NB) || state.scores.nb;
    state.scores.bh = parseInt(tags.BH) || state.scores.bh;
    state.scores.tf = parseInt(tags.TF) || state.scores.tf;
    state.scores.ip = parseInt(tags.IP) || state.scores.ip;
    state.nextDim = tags.NEXT_DIM || state.nextDim;

    renderQuestion(body, options, tags, { skipPreload: true });
    saveSessionSnapshot(cachedAnswer);

    try {
      const response = await apiFetch('/chat/preload/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: committedMessage, conversation_id: state.conversationId })
      });

      if (response.status === 409) {
        console.warn('预加载提交失败（草稿过期），回退到流式路径');
        state.answerLocked = false;
        state.preloadCache = {};
        state.preloadMessageMap = {};
        await sendMessage(committedMessage);
        return;
      }

      const data = await response.json();
      if (requestId !== state.activeQuestionRequestId) return;
      if (data.conversation_id) state.conversationId = data.conversation_id;
      if (!data.error && normalizeOptions(options).length) {
        preloadNextQuestions(options);
      }
    } catch (e) {
      console.warn('预加载提交网络异常，回退到流式路径', e);
      state.answerLocked = false;
      state.preloadCache = {};
      state.preloadMessageMap = {};
      await sendMessage(committedMessage);
      return;
    }
    state.answerLocked = false;
    return;
  }

  await sendMessage(text);
}

// 整轮重置：清空会话、分数、缓存并回到主题选择步骤
export function restart() {
  state.conversationId = '';
  state.currentQuestion = 0;
  state.scores = { nb: 0, bh: 0, tf: 0, ip: 0 };
  state.nextDim = 'NB';
  state.canConclude = false;
  state.answerLocked = false;
  state.incompleteRetryCount = 0;
  state.firstQuestionCache = null;
  clearSessionSnapshot();
  clearPreloadCache();
  resetWarmup();
  updateProgress();
  state.welcomeStep = 'theme';
  document.getElementById('progress-stepper').style.display = 'none';
  showPage('page-welcome');
  goToStep('theme');
}
