"use strict";

const STORAGE_KEY = "moon-window-save-v1";
const SAVE_VERSION = 2;
const MAX_MEMORIES = 24;
const MAX_MEMORY_CHARS = 240;
const MAX_MEMORY_TOTAL_CHARS = 2000;
const DEFAULT_SETTINGS = {
  chinesePreferred: true,
  matureVisuals: false,
  temperature: 0.78,
  maxLength: 180
};

const ui = {
  appShell: document.querySelector("#appShell"),
  stage: document.querySelector(".stage"),
  portraitLayerA: document.querySelector("#portraitLayerA"),
  portraitLayerB: document.querySelector("#portraitLayerB"),
  sceneToolbar: document.querySelector("#sceneToolbar"),
  sceneLabel: document.querySelector("#sceneLabel"),
  previousSceneButton: document.querySelector("#previousSceneButton"),
  nextSceneButton: document.querySelector("#nextSceneButton"),
  pauseSceneButton: document.querySelector("#pauseSceneButton"),
  messages: document.querySelector("#messages"),
  choiceDock: document.querySelector("#choiceDock"),
  choiceList: document.querySelector("#choiceList"),
  quickPrompts: document.querySelector("#quickPrompts"),
  form: document.querySelector("#composerForm"),
  input: document.querySelector("#composerInput"),
  rememberDraft: document.querySelector("#rememberDraft"),
  charCount: document.querySelector("#charCount"),
  sendButton: document.querySelector("#sendButton"),
  stopButton: document.querySelector("#stopButton"),
  statusDot: document.querySelector("#statusDot"),
  connectionText: document.querySelector("#connectionText"),
  turnCount: document.querySelector("#turnCount"),
  bondFill: document.querySelector("#bondFill"),
  bondValue: document.querySelector("#bondValue"),
  presenceState: document.querySelector("#presenceState"),
  stageQuote: document.querySelector("#stageQuote"),
  settingsButton: document.querySelector("#settingsButton"),
  closeSettingsButton: document.querySelector("#closeSettingsButton"),
  settingsDialog: document.querySelector("#settingsDialog"),
  settingsForm: document.querySelector("#settingsForm"),
  chinesePreferred: document.querySelector("#chinesePreferred"),
  matureVisuals: document.querySelector("#matureVisuals"),
  temperature: document.querySelector("#temperature"),
  temperatureValue: document.querySelector("#temperatureValue"),
  maxLength: document.querySelector("#maxLength"),
  maxLengthValue: document.querySelector("#maxLengthValue"),
  newChatButton: document.querySelector("#newChatButton"),
  chatButton: document.querySelector("#chatButton"),
  archiveButton: document.querySelector("#archiveButton"),
  importInput: document.querySelector("#importInput"),
  importButton: document.querySelector("#importButton"),
  clearDataButton: document.querySelector("#clearDataButton"),
  memoryList: document.querySelector("#memoryList"),
  memoryCount: document.querySelector("#memoryCount"),
  clearMemoriesButton: document.querySelector("#clearMemoriesButton"),
  storyButton: document.querySelector("#storyButton"),
  installButton: document.querySelector("#installButton"),
  toast: document.querySelector("#toast")
};

let story = null;
let isSending = false;
let deferredInstallPrompt = null;
let toastTimer = null;
let activeRequestController = null;
let scenes = [];
let activeSceneIndex = 0;
let activePortraitLayer = 0;
let sceneRotationPaused = false;
let sceneSwapToken = 0;
let lastSceneNode = null;
let activeStreamMessageId = null;

const DELIVERY_STATUS_LABELS = {
  streaming: "正在回复",
  stopped: "已停止",
  timedOut: "生成超时",
  failed: "生成中断"
};

class StreamUnavailableError extends Error {
  constructor(message = "当前服务不支持流式回复") {
    super(message);
    this.name = "StreamUnavailableError";
  }
}

function freshState() {
  return {
    version: SAVE_VERSION,
    messages: [],
    memories: [],
    affinity: 12,
    trust: 0,
    flags: [],
    completedChoices: [],
    currentNode: "arrival",
    view: "story",
    sceneId: "moon-window-calm",
    motionPaused: false,
    visual: {
      variantId: "moon-window-calm",
      mood: "calm",
      history: []
    },
    settings: { ...DEFAULT_SETTINGS },
    updatedAt: new Date().toISOString()
  };
}

function clampNumber(value, minimum, maximum, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(minimum, Math.min(maximum, number)) : fallback;
}

function normalizeMemories(rawMemories) {
  if (!Array.isArray(rawMemories)) return [];
  const selected = [];
  const seen = new Set();
  let usedChars = 0;
  for (const raw of rawMemories.slice(-256).reverse()) {
    if (selected.length >= MAX_MEMORIES || !raw || typeof raw.content !== "string") continue;
    const content = raw.content.trim().slice(0, MAX_MEMORY_CHARS);
    const sourceMessageId = typeof raw.sourceMessageId === "string"
      ? raw.sourceMessageId.slice(0, 160)
      : "";
    const dedupeKey = sourceMessageId || content;
    if (!content || seen.has(dedupeKey) || usedChars + content.length > MAX_MEMORY_TOTAL_CHARS) continue;
    selected.push({
      id: typeof raw.id === "string" && raw.id
        ? raw.id.slice(0, 160)
        : crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`,
      content,
      createdAt: Number.isNaN(Date.parse(raw.createdAt)) ? new Date().toISOString() : raw.createdAt,
      sourceMessageId
    });
    seen.add(dedupeKey);
    usedChars += content.length;
  }
  return selected.reverse();
}

function normalizeState(raw) {
  if (!raw || ![1, SAVE_VERSION].includes(raw.version) || !Array.isArray(raw.messages)) return freshState();
  const messages = raw.messages
    .slice(-80)
    .filter((message) => message && ["user", "assistant", "error"].includes(message.role))
    .filter((message) => typeof message.content === "string" && message.content.trim())
    .map((message) => ({
      id: typeof message.id === "string" ? message.id.slice(0, 160) : `${Date.now()}-${Math.random()}`,
      role: message.role,
      content: message.content.trim().slice(0, 12000),
      timestamp: Number.isNaN(Date.parse(message.timestamp)) ? new Date().toISOString() : message.timestamp,
      languageFallback: Boolean(message.languageFallback),
      backend: message.backend === "ollama" ? "ollama" : "koboldcpp",
      deliveryStatus: message.deliveryStatus === "streaming"
        ? "failed"
        : ["stopped", "timedOut", "failed"].includes(message.deliveryStatus)
          ? message.deliveryStatus
          : "completed"
    }));
  const currentNode = raw.currentNode === null || typeof raw.currentNode === "string"
    ? raw.currentNode
    : "arrival";
  return {
    ...freshState(),
    ...raw,
    version: SAVE_VERSION,
    messages,
    memories: normalizeMemories(raw.memories),
    affinity: clampNumber(raw.affinity, 0, 100, 12),
    trust: clampNumber(raw.trust, 0, 100, 0),
    flags: Array.isArray(raw.flags)
      ? raw.flags.filter((flag) => typeof flag === "string").slice(0, 200)
      : [],
    completedChoices: Array.isArray(raw.completedChoices)
      ? raw.completedChoices.filter((choice) => typeof choice === "string").slice(0, 500)
      : [],
    currentNode,
    view: raw.view === "chat" ? "chat" : "story",
    sceneId: typeof raw.sceneId === "string" ? raw.sceneId : "moon-window-calm",
    motionPaused: Boolean(raw.motionPaused),
    visual: {
      variantId: typeof raw.visual?.variantId === "string"
        ? raw.visual.variantId
        : typeof raw.sceneId === "string" ? raw.sceneId : "moon-window-calm",
      mood: typeof raw.visual?.mood === "string" ? raw.visual.mood : "calm",
      history: Array.isArray(raw.visual?.history)
        ? raw.visual.history.filter((id) => typeof id === "string").slice(-3)
        : []
    },
    settings: {
      chinesePreferred: raw.settings?.chinesePreferred !== false,
      matureVisuals: Boolean(raw.settings?.matureVisuals),
      temperature: Number(raw.settings?.temperature) === 0.62
        ? DEFAULT_SETTINGS.temperature
        : clampNumber(raw.settings?.temperature, 0.3, 1, DEFAULT_SETTINGS.temperature),
      maxLength: [260, 420].includes(Number(raw.settings?.maxLength))
        ? DEFAULT_SETTINGS.maxLength
        : clampNumber(raw.settings?.maxLength, 80, 360, DEFAULT_SETTINGS.maxLength)
    }
  };
}

function loadState() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return normalizeState(parsed);
  } catch {
    return freshState();
  }
}

let state = loadState();
sceneRotationPaused = state.motionPaused;
document.documentElement.classList.toggle("motion-paused", sceneRotationPaused);

function saveState() {
  state.updatedAt = new Date().toISOString();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function showToast(message) {
  ui.toast.textContent = message;
  ui.toast.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ui.toast.classList.remove("is-visible"), 2800);
}

function formatTime(timestamp) {
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(new Date(timestamp || Date.now()));
}

function appendFormattedContent(element, text) {
  const parts = String(text).split(/(\*[^*\n]{1,180}\*)/g);
  for (const part of parts) {
    if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
      const emphasis = document.createElement("em");
      emphasis.textContent = part.slice(1, -1);
      element.append(emphasis);
    } else {
      element.append(document.createTextNode(part));
    }
  }
}

function makeMessageElement(message) {
  const wrapper = document.createElement("article");
  const isUser = message.role === "user";
  const isError = message.role === "error";
  wrapper.className = `message${isUser ? " is-user" : ""}${isError ? " is-error" : ""}`;
  wrapper.dataset.messageId = message.id;

  if (!isUser) {
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = isError ? "!" : "S";
    avatar.setAttribute("aria-hidden", "true");
    wrapper.append(avatar);
  }

  const body = document.createElement("div");
  body.className = "message-body";
  const meta = document.createElement("p");
  meta.className = "message-meta";
  const speaker = document.createElement("strong");
  speaker.textContent = isUser ? "你" : isError ? "月窗" : "Sydney";
  const time = document.createElement("span");
  time.textContent = formatTime(message.timestamp);
  meta.append(speaker, time);
  if (message.languageFallback) {
    const warning = document.createElement("span");
    warning.className = "language-warning";
    warning.textContent = "中文重写仍不稳定";
    meta.append(warning);
  }
  if (message.backend === "ollama") {
    const route = document.createElement("span");
    route.className = "route-tag";
    route.textContent = "本地生成";
    meta.append(route);
  }
  if (DELIVERY_STATUS_LABELS[message.deliveryStatus]) {
    const status = document.createElement("span");
    status.className = `generation-status is-${message.deliveryStatus}`;
    status.textContent = DELIVERY_STATUS_LABELS[message.deliveryStatus];
    meta.append(status);
  }
  if (isUser) {
    const remembered = state.memories.some((memory) => memory.sourceMessageId === message.id);
    const memoryButton = document.createElement("button");
    memoryButton.type = "button";
    memoryButton.className = "memory-toggle";
    memoryButton.dataset.action = "toggle-memory";
    memoryButton.dataset.messageId = message.id;
    memoryButton.setAttribute("aria-pressed", String(remembered));
    memoryButton.setAttribute("aria-label", remembered ? "取消记住这条消息" : "把这条消息加入长期记忆");
    memoryButton.textContent = remembered ? "已记住" : "记住";
    meta.append(memoryButton);
  }

  const content = document.createElement("div");
  content.className = "message-content";
  appendFormattedContent(content, message.content);
  body.append(meta, content);
  wrapper.append(body);
  if (message.deliveryStatus && message.deliveryStatus !== "completed") {
    wrapper.classList.add(`is-${message.deliveryStatus}`);
  }
  return wrapper;
}

function refreshRenderedMessage(message, { scroll = false } = {}) {
  document.querySelector("#typingMessage")?.remove();
  const existing = [...ui.messages.querySelectorAll(".message")]
    .find((element) => element.dataset.messageId === message.id);
  const replacement = makeMessageElement(message);
  if (existing) existing.replaceWith(replacement);
  else ui.messages.append(replacement);
  if (scroll) requestAnimationFrame(() => ui.messages.scrollTo({ top: ui.messages.scrollHeight }));
}

function typingElement() {
  const message = document.createElement("article");
  message.className = "message";
  message.id = "typingMessage";
  message.innerHTML =
    '<div class="message-avatar" aria-hidden="true">S</div>' +
    '<div class="message-body"><p class="message-meta"><strong>Sydney</strong><span>正在组织心事…</span></p>' +
    '<div class="message-content"><span class="typing-dots" aria-label="正在输入"><i></i><i></i><i></i></span></div></div>';
  return message;
}

function renderMessages({ scroll = false, reset = false } = {}) {
  document.querySelector("#typingMessage")?.remove();
  let rendered = [...ui.messages.querySelectorAll(".message")];
  const prefixMatches = rendered.every(
    (element, index) => element.dataset.messageId === state.messages[index]?.id
  );
  if (reset || !prefixMatches || rendered.length > state.messages.length) {
    rendered.forEach((element) => element.remove());
    rendered = [];
  }
  state.messages.slice(rendered.length).forEach((message) => ui.messages.append(makeMessageElement(message)));
  if (isSending && !activeStreamMessageId) ui.messages.append(typingElement());
  const turns = state.messages.filter((message) => message.role === "assistant").length;
  ui.turnCount.textContent = String(turns);
  ui.quickPrompts.hidden = state.messages.filter((message) => message.role === "user").length > 2;
  if (scroll) requestAnimationFrame(() => ui.messages.scrollTo({ top: ui.messages.scrollHeight, behavior: "smooth" }));
}

function nodeForState() {
  return story?.nodes?.[state.currentNode] || null;
}

function resolveAffinityBand() {
  if (state.affinity >= 70) return "bonded";
  if (state.affinity >= 40) return "close";
  if (state.affinity >= 20) return "familiar";
  return "distant";
}

function resolveTrustBand() {
  if (state.trust >= 8) return "trusted";
  if (state.trust >= 3) return "opening";
  return "guarded";
}

function conversationContext() {
  return {
    mode: state.view,
    storyNode: state.currentNode,
    storyMood: nodeForState()?.mood || "",
    affinityBand: resolveAffinityBand(),
    trustBand: resolveTrustBand(),
    flags: state.flags.slice(-20),
    visualState: state.visual.mood
  };
}

function intimateVisualUnlocked() {
  return state.settings.matureVisuals
    && state.affinity >= 28
    && state.trust >= 6
    && state.flags.includes("mutual_intimacy");
}

function sceneIsAllowed(scene) {
  if (state.affinity < Number(scene.affinityMin || 0)) return false;
  if (state.trust < Number(scene.trustMin || 0)) return false;
  if (scene.requiredFlag && !state.flags.includes(scene.requiredFlag)) return false;
  return Number(scene.intimacyLevel || 0) === 0 || intimateVisualUnlocked();
}

function moodFromStoryNode() {
  const node = nodeForState();
  if (node?.visualState) return node.visualState;
  const mood = node?.mood || "";
  if (/欣喜|开心|愉快/.test(mood)) return "joy";
  if (/脆弱|低落|犹豫/.test(mood)) return "vulnerable";
  if (/认真|期待|关切/.test(mood)) return "attentive";
  return "calm";
}

function deriveMoodFromTurn(userText, replyText) {
  const user = String(userText || "");
  const reply = String(replyText || "");
  if (intimateVisualUnlocked() && nodeForState()?.visualState === "intimate") return "intimate";
  if (/哈哈|好笑|开心|高兴|惊喜|太棒|喜欢|可爱|逗|笑死/.test(user)) return "joy";
  if (/难受|误解|委屈|伤心|失望|害怕|焦虑|孤独|生气|崩溃|疲惫|累|哭|痛苦/.test(user)) return "attentive";
  if (/(你|Sydney).{0,8}(害怕|孤独|难过|秘密|脆弱|后悔|遗憾)/i.test(user)
      && /害怕|孤独|不确定|失去|遗憾|沉默/.test(reply)) return "vulnerable";
  if (/谢谢|懂了|原来|安心|平静/.test(user)) return "calm";
  return resolveAffinityBand() === "distant" ? "calm" : "attentive";
}

async function applyVisualMood(mood, { force = false } = {}) {
  if (!scenes.length) return;
  const safeMood = mood === "intimate" && !intimateVisualUnlocked() ? "attentive" : mood;
  const candidates = scenes.filter((scene) => sceneIsAllowed(scene) && scene.moods?.includes(safeMood));
  const pool = candidates.length ? candidates : scenes.filter((scene) => sceneIsAllowed(scene) && scene.moods?.includes("calm"));
  if (!pool.length) return;
  const recent = state.visual.history || [];
  const scene = pool.find((candidate) => !recent.includes(candidate.id)) || pool[0];
  if (!force && scene.id === state.visual.variantId) return;
  const index = scenes.findIndex((candidate) => candidate.id === scene.id);
  if (index < 0) return;
  state.visual = {
    variantId: scene.id,
    mood: safeMood,
    history: [...recent, scene.id].slice(-3)
  };
  await showScene(index);
  ui.stage.classList.remove("is-reacting");
  requestAnimationFrame(() => ui.stage.classList.add("is-reacting"));
  saveState();
}

function renderChoices() {
  const choices = nodeForState()?.choices || [];
  ui.choiceList.replaceChildren();
  if (state.view !== "story" || !choices.length || isSending) {
    ui.choiceDock.hidden = true;
    return;
  }
  choices.forEach((choice, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${String(index + 1).padStart(2, "0")}  ${choice.label}`;
    button.addEventListener("click", () => selectChoice(choice));
    ui.choiceList.append(button);
  });
  ui.choiceDock.hidden = false;
}

function updateSceneControls() {
  ui.pauseSceneButton.textContent = sceneRotationPaused ? "▶" : "Ⅱ";
  ui.pauseSceneButton.setAttribute("aria-pressed", String(sceneRotationPaused));
  ui.pauseSceneButton.setAttribute(
    "aria-label",
    sceneRotationPaused ? "继续环境动效" : "暂停环境动效"
  );
}

function stepScene(direction) {
  if (!scenes.length) return;
  let index = activeSceneIndex;
  for (let count = 0; count < scenes.length; count += 1) {
    index = (index + direction + scenes.length) % scenes.length;
    if (sceneIsAllowed(scenes[index])) {
      state.visual.mood = scenes[index].moods?.[0] || "calm";
      showScene(index, { userInitiated: true });
      return;
    }
  }
}

function setSceneRotationPaused(paused) {
  sceneRotationPaused = paused;
  state.motionPaused = paused;
  document.documentElement.classList.toggle("motion-paused", paused);
  updateSceneControls();
  saveState();
}

async function showScene(index, { userInitiated = false } = {}) {
  if (!scenes.length) return;
  const normalizedIndex = (index + scenes.length) % scenes.length;
  let scene = scenes[normalizedIndex];
  if (!sceneIsAllowed(scene)) {
    scene = scenes.find((candidate) => sceneIsAllowed(candidate) && candidate.moods?.includes("calm"));
    if (!scene) return;
  }
  const resolvedIndex = scenes.findIndex((candidate) => candidate.id === scene.id);
  const token = ++sceneSwapToken;
  const preload = new Image();
  preload.src = scene.src;
  try { await preload.decode(); } catch { return; }
  if (token !== sceneSwapToken) return;

  const currentLayer = activePortraitLayer === 0 ? ui.portraitLayerA : ui.portraitLayerB;
  const nextLayer = activePortraitLayer === 0 ? ui.portraitLayerB : ui.portraitLayerA;
  nextLayer.src = scene.src;
  nextLayer.alt = scene.alt;
  nextLayer.style.objectPosition = scene.objectPosition || "50% 34%";
  nextLayer.classList.add("is-active");
  currentLayer.classList.remove("is-active");
  currentLayer.alt = "";
  activePortraitLayer = activePortraitLayer === 0 ? 1 : 0;
  activeSceneIndex = resolvedIndex;
  ui.sceneLabel.textContent = scene.label;
  ui.stage.style.setProperty("--scene-accent", scene.accent || "#68d9ff");
  ui.stage.style.setProperty("--scene-warm", scene.warm || "#e45dcc");
  state.sceneId = scene.id;
  state.visual.variantId = scene.id;
  if (userInitiated) {
    saveState();
  }
}

async function loadScenes() {
  try {
    const response = await fetch("/content/scenes.json");
    if (!response.ok) throw new Error("场景清单加载失败");
    const data = await response.json();
    scenes = Array.isArray(data.scenes) ? data.scenes : [];
  } catch {
    scenes = [];
  }
  if (!scenes.length) return;
  const preferredScene = state.visual.variantId || state.sceneId;
  const savedIndex = scenes.findIndex((scene) => scene.id === preferredScene);
  await showScene(savedIndex >= 0 ? savedIndex : 0);
  lastSceneNode = state.currentNode;
  updateSceneControls();
}

function renderView() {
  const storyActive = state.view === "story";
  ui.appShell.classList.toggle("is-story-view", storyActive);
  ui.storyButton.classList.toggle("is-active", storyActive);
  ui.storyButton.setAttribute("aria-selected", String(storyActive));
  ui.chatButton.classList.toggle("is-active", !storyActive);
  ui.chatButton.setAttribute("aria-selected", String(!storyActive));
}

function renderStage() {
  const affinity = Math.max(0, Math.min(100, state.affinity));
  ui.bondValue.textContent = String(affinity);
  ui.bondFill.style.width = `${affinity}%`;
  const visualLabels = {
    calm: "安静地陪着你",
    attentive: "在认真听你说",
    joy: "被你逗亮了眼睛",
    vulnerable: "向你露出真实的一面",
    intimate: "与你共享更近的距离"
  };
  ui.presenceState.textContent = isSending ? "正认真想着你的话" : visualLabels[state.visual.mood] || "安静地陪着你";
  const lastReply = [...state.messages].reverse().find((message) => message.role === "assistant");
  if (lastReply) {
    const compact = lastReply.content.replace(/\*/g, "").replace(/\s+/g, " ").trim();
    ui.stageQuote.textContent = `“${compact.length > 54 ? `${compact.slice(0, 54)}…` : compact}”`;
  }
  if (state.view === "story" && state.currentNode !== lastSceneNode) {
    lastSceneNode = state.currentNode;
    applyVisualMood(moodFromStoryNode(), { force: true });
  }
}

function renderAll(options) {
  renderMessages(options);
  renderChoices();
  renderView();
  renderStage();
}

function addMessage(role, content, extras = {}) {
  const message = {
    id: crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`,
    role,
    content: content.trim(),
    timestamp: new Date().toISOString(),
    ...extras
  };
  state.messages.push(message);
  if (state.messages.length > 80) state.messages = state.messages.slice(-80);
  saveState();
  return message;
}

function rememberMessage(message, { quiet = false } = {}) {
  if (!message || message.role !== "user") return false;
  if (state.memories.some((memory) => memory.sourceMessageId === message.id)) return true;
  if (message.content.length > MAX_MEMORY_CHARS) {
    if (!quiet) showToast(`这条消息超过 ${MAX_MEMORY_CHARS} 字，请另发一条更简洁的事实再标记。`);
    return false;
  }
  if (state.memories.length >= MAX_MEMORIES) {
    if (!quiet) showToast(`长期记忆已满（${MAX_MEMORIES} 条），请先在设置中删除一条。`);
    return false;
  }
  const usedChars = state.memories.reduce((sum, memory) => sum + memory.content.length, 0);
  if (usedChars + message.content.length > MAX_MEMORY_TOTAL_CHARS) {
    if (!quiet) showToast("长期记忆文字已达上限，请先在设置中删减。 ");
    return false;
  }
  state.memories.push({
    id: crypto.randomUUID?.() || `${Date.now()}-${Math.random()}`,
    content: message.content,
    createdAt: new Date().toISOString(),
    sourceMessageId: message.id
  });
  saveState();
  if (!quiet) showToast("已加入长期记忆；你随时可以在设置中查看或删除。 ");
  return true;
}

function forgetMemory(memoryId) {
  const previousLength = state.memories.length;
  state.memories = state.memories.filter((memory) => memory.id !== memoryId);
  if (state.memories.length === previousLength) return false;
  saveState();
  renderMemorySettings();
  renderMessages({ reset: true });
  return true;
}

function toggleMemoryForMessage(messageId) {
  const existing = state.memories.find((memory) => memory.sourceMessageId === messageId);
  if (existing) {
    forgetMemory(existing.id);
    showToast("已从长期记忆中移除。 ");
    return;
  }
  const message = state.messages.find((candidate) => candidate.id === messageId && candidate.role === "user");
  if (rememberMessage(message)) {
    refreshRenderedMessage(message);
    renderMemorySettings();
  }
}

function renderMemorySettings() {
  if (!ui.memoryList || !ui.memoryCount) return;
  ui.memoryCount.textContent = `${state.memories.length} / ${MAX_MEMORIES}`;
  ui.memoryList.replaceChildren();
  ui.clearMemoriesButton.disabled = state.memories.length === 0;
  if (!state.memories.length) {
    const empty = document.createElement("p");
    empty.className = "memory-empty";
    empty.textContent = "还没有长期记忆。只有你明确标记的用户消息会出现在这里。";
    ui.memoryList.append(empty);
    return;
  }
  for (const memory of [...state.memories].reverse()) {
    const item = document.createElement("article");
    item.className = "memory-item";
    const content = document.createElement("p");
    content.textContent = memory.content;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.dataset.memoryId = memory.id;
    remove.setAttribute("aria-label", `删除长期记忆：${memory.content.slice(0, 40)}`);
    remove.textContent = "删除";
    item.append(content, remove);
    ui.memoryList.append(item);
  }
}

function applyEffects(effects = {}) {
  state.affinity = Math.min(100, state.affinity + (Number(effects.affinity) || 0));
  state.trust = Math.min(100, Math.max(0, state.trust + (Number(effects.trust) || 0)));
  for (const flag of effects.flags || []) {
    if (!state.flags.includes(flag)) state.flags.push(flag);
  }
}

async function selectChoice(choice) {
  const succeeded = await sendMessage(choice.prompt);
  if (!succeeded) return;
  if (!state.completedChoices.includes(choice.id)) {
    applyEffects(choice.effects);
    state.completedChoices.push(choice.id);
  }
  state.currentNode = choice.next;
  saveState();
  renderAll({ scroll: true });
}

function metadataFromStreamEvent(event = {}) {
  const data = event.data && typeof event.data === "object" ? event.data : {};
  const backend = event.backend ?? data.backend;
  const hasLanguageFallback = Object.hasOwn(event, "languageFallback")
    || Object.hasOwn(data, "languageFallback");
  return {
    ...(backend ? { backend } : {}),
    ...(hasLanguageFallback
      ? { languageFallback: Boolean(event.languageFallback ?? data.languageFallback) }
      : {})
  };
}

function mergeReplyMetadata(target, event) {
  const metadata = metadataFromStreamEvent(event);
  if (metadata.backend) target.backend = metadata.backend;
  if (Object.hasOwn(metadata, "languageFallback")) {
    target.languageFallback = metadata.languageFallback;
  }
}

function updateStreamingMessage(content, metadata, status = "streaming") {
  const cleanContent = String(content || "").trimStart();
  if (!cleanContent) return null;
  let message = state.messages.find((candidate) => candidate.id === activeStreamMessageId);
  if (!message) {
    message = addMessage("assistant", cleanContent, {
      deliveryStatus: status,
      languageFallback: Boolean(metadata.languageFallback),
      backend: metadata.backend
    });
    activeStreamMessageId = message.id;
  } else {
    message.content = cleanContent;
    message.deliveryStatus = status;
    message.languageFallback = Boolean(metadata.languageFallback);
    if (metadata.backend) message.backend = metadata.backend;
  }
  refreshRenderedMessage(message, { scroll: true });
  return message;
}

function finishStreamingMessage(content, metadata) {
  const message = updateStreamingMessage(String(content || "").trim(), metadata, "completed");
  if (!message) throw new Error("模型没有返回可显示的内容。");
  message.deliveryStatus = "completed";
  message.languageFallback = Boolean(metadata.languageFallback);
  if (metadata.backend) message.backend = metadata.backend;
  activeStreamMessageId = null;
  saveState();
  refreshRenderedMessage(message, { scroll: true });
  return message;
}

function interruptStreamingMessage(status) {
  const message = state.messages.find((candidate) => candidate.id === activeStreamMessageId);
  activeStreamMessageId = null;
  if (!message) return false;
  message.content = message.content.trimEnd();
  message.deliveryStatus = status;
  saveState();
  refreshRenderedMessage(message, { scroll: true });
  return true;
}

function streamEventType(event) {
  const explicit = event?.type ?? event?.event;
  if (typeof explicit === "string") return explicit.toLowerCase();
  if (typeof event?.delta === "string") return "delta";
  if (typeof event?.reply === "string") return "done";
  return "";
}

function streamErrorMessage(event) {
  const detail = event?.error ?? event?.message ?? event?.data?.error ?? event?.data?.message;
  if (typeof detail === "string" && detail.trim()) return detail.trim();
  if (detail && typeof detail.message === "string") return detail.message;
  return "本地模型生成失败。";
}

async function requestStreamingReply(payload, signal, handlers) {
  if (typeof ReadableStream === "undefined" || typeof TextDecoder === "undefined") {
    throw new StreamUnavailableError("当前浏览器不支持流式回复");
  }
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/x-ndjson" },
    body: JSON.stringify(payload),
    signal
  });
  if ([404, 405, 501].includes(response.status)) {
    throw new StreamUnavailableError();
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || `请求失败（${response.status}）`);
  }
  const contentType = response.headers.get("Content-Type") || "";
  if (!contentType.toLowerCase().includes("application/x-ndjson")) {
    throw new StreamUnavailableError("当前服务返回了非流式响应");
  }
  if (!response.body || typeof response.body.getReader !== "function") {
    throw new StreamUnavailableError("当前浏览器无法读取流式回复");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let sawEvent = false;
  let doneEvent = null;

  const consumeLine = (line) => {
    const cleanLine = line.trim();
    if (!cleanLine) return;
    let event;
    try {
      event = JSON.parse(cleanLine);
    } catch {
      throw new Error("流式响应格式错误。");
    }
    const type = streamEventType(event);
    if (!type) return;
    sawEvent = true;
    if (type === "meta") handlers.onMeta(event);
    else if (type === "delta") {
      const delta = event.delta ?? event.text ?? event.content
        ?? (typeof event.data === "string" ? event.data : "");
      if (typeof delta === "string" && delta) handlers.onDelta(delta, event);
    } else if (type === "done") {
      doneEvent = event;
    } else if (type === "error") {
      throw new Error(streamErrorMessage(event));
    }
  };

  try {
    while (!doneEvent) {
      const { value, done } = await reader.read();
      if (done) {
        buffer += decoder.decode();
        if (buffer.trim()) consumeLine(buffer);
        break;
      }
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split(/\r?\n/);
      buffer = lines.pop() || "";
      for (const line of lines) {
        consumeLine(line);
        if (doneEvent) break;
      }
    }
  } finally {
    try { await reader.cancel(); } catch {}
    reader.releaseLock();
  }

  if (!sawEvent) throw new Error("本地服务没有返回有效的流式事件。");
  if (!doneEvent) throw new Error("流式回复意外中断。");
  return doneEvent;
}

async function requestCompatibleReply(payload, signal) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `请求失败（${response.status}）`);
  return data;
}

async function sendMessage(rawText) {
  const text = String(rawText ?? ui.input.value).trim();
  if (!text || isSending) return;

  const rememberDraft = Boolean(ui.rememberDraft?.checked);
  const userMessage = addMessage("user", text);
  if (rememberDraft) rememberMessage(userMessage);
  state.affinity = Math.min(100, state.affinity + 1);
  ui.input.value = "";
  if (ui.rememberDraft) ui.rememberDraft.checked = false;
  resizeComposer();
  isSending = true;
  ui.sendButton.disabled = true;
  ui.stopButton.hidden = false;
  renderAll({ scroll: true });
  applyVisualMood("attentive");

  const messages = state.messages
    .filter((message) => message.role === "user"
      || (message.role === "assistant"
        && !["stopped", "timedOut", "failed", "streaming"].includes(message.deliveryStatus)))
    .slice(-24)
    .map(({ role, content }) => ({ role, content }));

  const payload = {
    messages,
    memories: state.memories.map(({ id, content }) => ({ id, content })),
    settings: state.settings,
    conversationContext: conversationContext()
  };

  let succeeded = false;
  let timedOut = false;
  let streamedText = "";
  const replyMetadata = { languageFallback: false };
  activeRequestController = new AbortController();
  const timeout = setTimeout(() => {
    timedOut = true;
    activeRequestController?.abort();
  }, 120000);
  try {
    let finalReply = "";
    try {
      const done = await requestStreamingReply(payload, activeRequestController.signal, {
        onMeta(event) {
          mergeReplyMetadata(replyMetadata, event);
          const message = state.messages.find((candidate) => candidate.id === activeStreamMessageId);
          if (message) updateStreamingMessage(streamedText, replyMetadata);
        },
        onDelta(delta, event) {
          mergeReplyMetadata(replyMetadata, event);
          streamedText += delta;
          updateStreamingMessage(streamedText, replyMetadata);
        }
      });
      mergeReplyMetadata(replyMetadata, done);
      const doneData = done.data && typeof done.data === "object" ? done.data : {};
      finalReply = done.reply ?? done.text ?? doneData.reply ?? doneData.text ?? streamedText;
    } catch (error) {
      if (!(error instanceof StreamUnavailableError)) throw error;
      showToast("当前服务暂不支持流式输出，已切换到兼容模式。");
      const data = await requestCompatibleReply(payload, activeRequestController.signal);
      mergeReplyMetadata(replyMetadata, data);
      replyMetadata.backend ||= data.backend || "koboldcpp";
      finalReply = data.reply;
    }

    const replyMessage = finishStreamingMessage(finalReply, replyMetadata);
    applyVisualMood(deriveMoodFromTurn(text, replyMessage.content));
    succeeded = true;
    state.affinity = Math.min(100, state.affinity + 1);
    if (replyMetadata.languageFallback) showToast("模型仍有中文底座限制；这条回复已自动重试。后续训练版会继续改善。");
  } catch (error) {
    if (error.name === "AbortError") {
      const keptPartial = interruptStreamingMessage(timedOut ? "timedOut" : "stopped");
      showToast(timedOut
        ? keptPartial ? "等待超过 120 秒，已停止生成并保留已有内容。" : "等待超过 120 秒，已经停止生成。"
        : keptPartial ? "已停止生成，已有内容保留在对话中。" : "已经停止这次回复。");
    } else {
      const keptPartial = interruptStreamingMessage("failed");
      if (!keptPartial) {
        addMessage("error", `${error.message} 请确认本地模型服务已经运行，然后再试一次。`);
      }
      showToast(keptPartial ? `回复生成中断：${error.message}` : "没有接通本地模型，消息已保留。 ");
    }
  } finally {
    clearTimeout(timeout);
    activeStreamMessageId = null;
    activeRequestController = null;
    isSending = false;
    ui.sendButton.disabled = false;
    ui.stopButton.hidden = true;
    saveState();
    renderAll({ scroll: true });
    ui.input.focus();
  }
  return succeeded;
}

function resizeComposer() {
  ui.input.style.height = "auto";
  ui.input.style.height = `${Math.min(ui.input.scrollHeight, 150)}px`;
  ui.charCount.textContent = `${ui.input.value.length} / 4000`;
}

async function refreshHealth() {
  try {
    const response = await fetch("/api/health", { cache: "no-store" });
    const data = await response.json();
    if (data.chinese?.online) {
      ui.statusDot.className = "status-dot is-online";
      ui.connectionText.textContent = `本地在线 · 中文增强 ${data.chinese.model}`;
    } else if (data.kobold?.online) {
      ui.statusDot.className = "status-dot is-online";
      ui.connectionText.textContent = `本地在线 · ${String(data.kobold.model).replace(/^.*[\\/]/, "")}`;
    } else {
      throw new Error("offline");
    }
  } catch {
    ui.statusDot.className = "status-dot is-offline";
    ui.connectionText.textContent = "模型离线 · 可查看已有记录";
  }
}

function openSettings() {
  ui.chinesePreferred.checked = state.settings.chinesePreferred;
  ui.matureVisuals.checked = state.settings.matureVisuals;
  ui.temperature.value = state.settings.temperature;
  ui.temperatureValue.textContent = Number(state.settings.temperature).toFixed(2);
  ui.maxLength.value = state.settings.maxLength;
  ui.maxLengthValue.textContent = String(state.settings.maxLength);
  renderMemorySettings();
  ui.settingsDialog.showModal();
}

function saveSettings() {
  state.settings = {
    chinesePreferred: ui.chinesePreferred.checked,
    matureVisuals: ui.matureVisuals.checked,
    temperature: Number(ui.temperature.value),
    maxLength: Number(ui.maxLength.value)
  };
  saveState();
  if (!intimateVisualUnlocked() && state.visual.mood === "intimate") applyVisualMood("attentive", { force: true });
  showToast("设置已经留在这台电脑上。 ");
}

function exportArchive() {
  const payload = {
    format: "moon-window-save",
    schemaVersion: SAVE_VERSION,
    exportedAt: new Date().toISOString(),
    state
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `sydney-save-${new Date().toISOString().slice(0, 10)}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
  showToast("存档已导出。 ");
}

async function importArchive(file) {
  try {
    const payload = JSON.parse(await file.text());
    const imported = payload?.format === "moon-window-save" ? payload.state : payload;
    if (imported && Number(imported.version) > SAVE_VERSION) {
      throw new Error(`这个存档来自更新版本（v${imported.version}），请先更新月窗`);
    }
    if (!imported || ![1, SAVE_VERSION].includes(imported.version) || !Array.isArray(imported.messages)) {
      throw new Error("不是有效的月窗存档");
    }
    state = normalizeState(imported);
    saveState();
    renderAll({ scroll: true, reset: true });
    ui.settingsDialog.close();
    showToast("存档已恢复。欢迎回来。 ");
  } catch (error) {
    showToast(`导入失败：${error.message}`);
  } finally {
    ui.importInput.value = "";
  }
}

function startNewChat() {
  if (state.messages.length && !window.confirm("开启新会话？当前记录仍可先用“存档”导出。")) return;
  const settings = state.settings;
  const affinity = state.affinity;
  const memories = state.memories.map((memory) => ({ ...memory }));
  state = freshState();
  state.settings = settings;
  state.affinity = affinity;
  state.memories = memories;
  seedPrologue();
  saveState();
  renderAll({ scroll: true, reset: true });
  showToast("新的月夜已经开始。 ");
}

function clearAllData() {
  if (!window.confirm("清除全部对话、关系值、剧情进度和设置？此操作无法撤销。")) return;
  localStorage.removeItem(STORAGE_KEY);
  state = freshState();
  seedPrologue();
  saveState();
  renderAll({ scroll: true, reset: true });
  ui.settingsDialog.close();
  showToast("本地月窗数据已清除。 ");
}

function clearMemories() {
  if (!state.memories.length) return;
  if (!window.confirm("清空全部长期记忆？对话记录仍会保留，此操作无法撤销。")) return;
  state.memories = [];
  saveState();
  renderMemorySettings();
  renderMessages({ reset: true });
  showToast("长期记忆已清空。 ");
}

function seedPrologue() {
  const startNode = story?.nodes?.[story.start];
  if (!startNode) return;
  state.currentNode = story.start;
  if (!state.messages.length) addMessage("assistant", startNode.text);
}

async function loadStory() {
  try {
    const response = await fetch("/content/prologue.json");
    if (!response.ok) throw new Error("序章加载失败");
    story = await response.json();
  } catch {
    story = {
      start: "arrival",
      nodes: {
        arrival: {
          text: "晚上好。我一直在这扇窗口后面等你。你愿意陪我聊一会儿吗？ 💙",
          mood: "期待",
          choices: []
        }
      }
    };
  }
  if (!state.messages.length) seedPrologue();
  if (state.currentNode !== null && !story.nodes[state.currentNode]) state.currentNode = story.start;
  saveState();
  renderAll();
}

ui.form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage();
});

ui.input.addEventListener("input", resizeComposer);
ui.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    sendMessage();
  }
});

ui.quickPrompts.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-prompt]");
  if (button) sendMessage(button.dataset.prompt);
});

ui.messages.addEventListener("click", (event) => {
  const button = event.target.closest('button[data-action="toggle-memory"]');
  if (button) toggleMemoryForMessage(button.dataset.messageId);
});

ui.settingsButton.addEventListener("click", openSettings);
ui.closeSettingsButton.addEventListener("click", () => ui.settingsDialog.close());
ui.settingsForm.addEventListener("submit", saveSettings);
ui.temperature.addEventListener("input", () => {
  ui.temperatureValue.textContent = Number(ui.temperature.value).toFixed(2);
});
ui.maxLength.addEventListener("input", () => {
  ui.maxLengthValue.textContent = ui.maxLength.value;
});
ui.newChatButton.addEventListener("click", startNewChat);
ui.archiveButton.addEventListener("click", exportArchive);
ui.importButton.addEventListener("click", () => ui.importInput.click());
ui.clearDataButton.addEventListener("click", clearAllData);
ui.clearMemoriesButton.addEventListener("click", clearMemories);
ui.memoryList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-memory-id]");
  if (button && forgetMemory(button.dataset.memoryId)) showToast("已删除这条长期记忆。 ");
});
ui.stopButton.addEventListener("click", () => activeRequestController?.abort());
ui.previousSceneButton.addEventListener("click", () => stepScene(-1));
ui.nextSceneButton.addEventListener("click", () => stepScene(1));
ui.pauseSceneButton.addEventListener("click", () => setSceneRotationPaused(!sceneRotationPaused));
ui.importInput.addEventListener("change", () => {
  if (ui.importInput.files[0]) importArchive(ui.importInput.files[0]);
});
ui.chatButton.addEventListener("click", () => {
  state.view = "chat";
  saveState();
  renderAll();
  showToast("已切换到自由对话。 ");
});
ui.storyButton.addEventListener("click", () => {
  state.view = "story";
  saveState();
  renderAll();
  ui.choiceDock.scrollIntoView({ behavior: "smooth", block: "nearest" });
  showToast(state.currentNode === null ? "本段序章已经结束。" : "剧情选项已展开。 ");
});

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  deferredInstallPrompt = event;
  ui.installButton.hidden = false;
});
ui.installButton.addEventListener("click", async () => {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  await deferredInstallPrompt.userChoice;
  deferredInstallPrompt = null;
  ui.installButton.hidden = true;
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("/service-worker.js").catch(() => {}));
}

loadStory();
loadScenes();
refreshHealth();
resizeComposer();
setInterval(refreshHealth, 15000);
