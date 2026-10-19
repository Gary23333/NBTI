// NBTI 流式问答：SSE 解析、增量 JSON 解析、答题流程编排
// （发送消息 → 流式 / 非流式响应 → 最终答案处理 → 渲染）
// 本模块依赖 render 做界面更新、依赖 session 保存断点快照，方向单一，无循环。

import { state, MAX_INCOMPLETE_RETRIES } from './state.js';
import { apiFetch } from './api.js';
import { escHtml, normalizeOptions, sleep } from './util.js';
import {
  renderQuestionIncremental,
  renderIntroIncremental,
  showStreamingIntroShell,
  showStreamingQuestionShell,
  showResult,
  renderIntro,
  renderQuestion,
  updateProgress,
  showPage,
  completeFakeProgressStage
} from './render.js';
import { saveSessionSnapshot } from './session.js';
import { resolveWarmupDraft } from './warmup.js';

// ---------- JSON 抽取与增量解析 ----------

export function extractJsonFromText(text) {
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

export function isCompleteAssess(tags, body, options, expectedQ = null) {
  if (tags.PHASE !== 'ASSESS') return false;
  if (expectedQ !== null && parseInt(tags.Q) !== expectedQ) return false;
  const scene = typeof body === 'object' ? body.scene : body;
  return typeof scene === 'string' && scene.trim().length > 0 && normalizeOptions(options).length >= 2 && normalizeOptions(options).length <= 4;
}

export function parseIncrementalJson(text) {
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

export function decodeJsonString(value) {
  try {
    return JSON.parse(`"${value}"`);
  } catch (e) {
    return value;
  }
}

export function readJsonStringFrom(text, quoteIndex) {
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

export function extractPartialStringField(text, key) {
  const keyIndex = text.indexOf(`"${key}"`);
  if (keyIndex < 0) return null;

  const colonIndex = text.indexOf(':', keyIndex);
  if (colonIndex < 0) return null;

  const quoteIndex = text.indexOf('"', colonIndex);
  if (quoteIndex < 0) return null;

  return readJsonStringFrom(text, quoteIndex);
}

export function extractPartialOptions(text) {
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

export function buildPartialObject(incompleteJson) {
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

export function parseResponse(text) {
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

// ---------- 答题流程 ----------

let startInFlight = false;

export async function startTest() {
  // 防重复进入：连点“开始测试”会并发发出多个 init 请求，
  // 产生孤儿会话并浪费 LLM 调用（conversationId 尚未回填时每个请求都会新建会话）
  if (startInFlight) return;
  startInFlight = true;
  try {
    showPage('page-test');

    // 首题预热命中：直接消费后端草稿（无需再等首请求的模型生成）。
    // 预热端点未就绪时草稿为空 → 自动回退到既有 /api/chat/stream 流程。
    const draft = await resolveWarmupDraft();
    if (draft && consumeWarmupDraft(draft)) return;

    await sendMessage('开始测试');
  } finally {
    startInFlight = false;
  }
}

// 直接消费首题预热草稿：先渲染已有内容（缓存优先，无骨架屏闪烁），
// 后续答题仍走既有 /api/chat/stream 流程，保证完全兼容。
function consumeWarmupDraft(draft) {
  const answer = draft && draft.answer;
  if (typeof answer !== 'string' || !answer) return false;

  const { tags, body, options } = parseResponse(answer);
  const finalOptions = normalizeOptions(options);
  if (!isCompleteAssess(tags, body, finalOptions, 1)) return false;

  const requestId = ++state.activeQuestionRequestId;
  if (draft.conversationId) state.conversationId = draft.conversationId;
  state.warmupDraft = null;
  processFinalAnswer(answer, finalOptions, requestId, {});
  return true;
}

export async function sendMessage(message) {
  const requestId = ++state.activeQuestionRequestId;

  if (state.canConclude) {
    message = '[CAN_CONCLUDE:true] ' + message;
    state.canConclude = false;
  }

  if (state.currentQuestion === 0) {
    showStreamingIntroShell();
  } else {
    showStreamingQuestionShell();
  }

  try {
    const response = await apiFetch('/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        conversation_id: state.conversationId,
        theme: state.selectedTheme,
        style: state.selectedStyle
      })
    });

    if (requestId !== state.activeQuestionRequestId) return;

    if (response.headers.get('content-type')?.includes('text/event-stream') || response.headers.get('content-type')?.includes('application/stream+json')) {
      await handleStreamResponse(response, requestId, message);
    } else {
      await handleNonStreamResponse(response, requestId, message);
    }

  } catch (error) {
    try {
      await sendMessageNonStream(message, requestId);
    } catch (fallbackError) {
      state.answerLocked = false;
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

export async function sendMessageNonStream(message, requestId) {
  const response = await apiFetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      conversation_id: state.conversationId,
      theme: state.selectedTheme,
      style: state.selectedStyle
    })
  });

  await handleNonStreamResponse(response, requestId, message);
}

export async function handleStreamResponse(response, requestId, originalMessage) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let fullAnswer = '';
  let receivedFirstToken = false;
  let options = [];
  let conversationIdFromStream = state.conversationId;
  const expectedQuestion = state.currentQuestion > 0 ? state.currentQuestion + 1 : 1;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    if (requestId !== state.activeQuestionRequestId) return;

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
          // 收到首 token：等待期的假进度补满并淡出
          completeFakeProgressStage();
          if (state.currentQuestion === 0 && !document.getElementById('incremental-intro')) {
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
        if (state.currentQuestion === 0 && partialObj.comment) {
          renderIntroIncremental(partialObj.comment);
        } else if (partialObj.comment || partialObj.scene || partialOptions.length) {
          renderQuestionIncremental(partialObj, partialOptions, { enableOptions: false });
        }

        if (data.options) {
          options = data.options;
          if (state.currentQuestion === 0 && partialObj.comment) {
            renderIntroIncremental(partialObj.comment);
          } else if (partialObj.comment || partialObj.scene || options.length) {
            renderQuestionIncremental(partialObj, options, { enableOptions: false });
          }
        }
      }
    }
  }

  if (requestId !== state.activeQuestionRequestId) return;
  state.conversationId = conversationIdFromStream;

  if (fullAnswer) {
    processFinalAnswer(fullAnswer, options, requestId, { skipIntro: state.currentQuestion > 0, retryMessage: originalMessage });
  }
}

export async function handleNonStreamResponse(response, requestId, originalMessage) {
  const data = await response.json();

  if (data.error) {
    throw new Error(data.error);
  }

  if (requestId !== state.activeQuestionRequestId) return;

  state.conversationId = data.conversation_id;

  const parsed = parseResponse(data.answer);
  if (parsed.tags.PHASE === 'ASSESS') {
    await playAnswerTypewriter(data.answer, requestId);
  }

  processFinalAnswer(data.answer, data.options || [], requestId, { retryMessage: originalMessage });
}

export function processFinalAnswer(answerText, options, requestId, settings = {}) {
  if (requestId !== state.activeQuestionRequestId) return;

  const { tags, options: parsedOptions, body } = parseResponse(answerText);
  const finalOptions = normalizeOptions(options && options.length > 0 ? options : parsedOptions);

  if (tags.PHASE === 'RESULT') {
    state.incompleteRetryCount = 0;
    showResult(answerText, tags);
    state.answerLocked = false;
    return;
  }

  const expectedQuestion = state.currentQuestion > 0 ? state.currentQuestion + 1 : 1;
  if (!isCompleteAssess(tags, body, finalOptions, expectedQuestion)) {
    state.answerLocked = false;
    state.incompleteRetryCount++;
    const questionArea = document.getElementById('question-area');
    if (state.incompleteRetryCount > MAX_INCOMPLETE_RETRIES) {
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
        state.incompleteRetryCount = 0;
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
    if (requestId === state.activeQuestionRequestId) {
      sendMessage(settings.retryMessage || '请重新生成这一题');
    }
    return;
  }

  state.incompleteRetryCount = 0;

  state.canConclude = tags.CAN_CONCLUDE === 'true';

  state.currentQuestion = parseInt(tags.Q) || state.currentQuestion + 1;
  updateProgress();

  state.scores.nb = parseInt(tags.NB) || state.scores.nb;
  state.scores.bh = parseInt(tags.BH) || state.scores.bh;
  state.scores.tf = parseInt(tags.TF) || state.scores.tf;
  state.scores.ip = parseInt(tags.IP) || state.scores.ip;
  state.nextDim = tags.NEXT_DIM || state.nextDim;

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
  state.answerLocked = false;
  saveSessionSnapshot(answerText);
}

export async function playAnswerTypewriter(answerText, requestId) {
  const expectedQuestion = state.currentQuestion > 0 ? state.currentQuestion + 1 : 1;

  if (state.currentQuestion === 0 && !document.getElementById('incremental-intro')) {
    showStreamingIntroShell();
  } else if (state.currentQuestion > 0 || !document.getElementById('incremental-card')) {
    showStreamingQuestionShell();
  }

  for (let i = 1; i <= answerText.length; i += 2) {
    if (requestId !== state.activeQuestionRequestId) return;

    const partialObj = buildPartialObject(answerText.slice(0, i));
    if (partialObj.phase === 'ASSESS') {
      partialObj.q = expectedQuestion;
    }

    const partialOptions = partialObj.options || [];
    if (state.currentQuestion === 0 && partialObj.comment) {
      renderIntroIncremental(partialObj.comment);
    } else if (partialObj.comment || partialObj.scene || partialOptions.length) {
      renderQuestionIncremental(partialObj, partialOptions, { enableOptions: false });
    }

    await sleep(8);
  }
}
