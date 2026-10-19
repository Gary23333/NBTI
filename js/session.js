// NBTI 断点续测：把会话快照写入 localStorage，刷新后恢复继续答题。
// saveSessionSnapshot / clearSessionSnapshot 是纯存储操作，可被 stream/preload 直接引用；
// restoreSessionSnapshot 需要用到 stream 的解析/流程函数以及 preload 的 restart，
// 这些由 main.js 通过参数注入，避免 session 反向 import 造成循环依赖。

import { state } from './state.js';
import { showPage } from './render.js';

export const SESSION_STORAGE_KEY = 'nbti-session';

export function saveSessionSnapshot(lastAnswer) {
  try {
    if (!state.conversationId || typeof lastAnswer !== 'string' || !lastAnswer) return;
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
      conversationId: state.conversationId,
      currentQuestion: state.currentQuestion,
      scores: state.scores,
      nextDim: state.nextDim,
      canConclude: state.canConclude,
      lastAnswer,
      selectedTheme: state.selectedTheme,
      selectedStyle: state.selectedStyle
    }));
  } catch (e) {}
}

export function clearSessionSnapshot() {
  try {
    localStorage.removeItem(SESSION_STORAGE_KEY);
  } catch (e) {}
}

export function restoreSessionSnapshot(handlers = {}) {
  const { parseResponse, processFinalAnswer, restart } = handlers;

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
    state.conversationId = snapshot.conversationId;
    state.currentQuestion = Math.max((parseInt(snapshot.currentQuestion) || 1) - 1, 0);
    state.scores = { nb: 0, bh: 0, tf: 0, ip: 0, ...(snapshot.scores || {}) };
    state.nextDim = snapshot.nextDim || 'NB';
    state.canConclude = snapshot.canConclude === true;
    state.answerLocked = false;
    if (snapshot.selectedTheme) state.selectedTheme = snapshot.selectedTheme;
    if (snapshot.selectedStyle) state.selectedStyle = snapshot.selectedStyle;
    showPage('page-test');
    processFinalAnswer(snapshot.lastAnswer, [], ++state.activeQuestionRequestId, { skipIntro: true });
  } catch (e) {
    clearSessionSnapshot();
    restart();
  }
}
