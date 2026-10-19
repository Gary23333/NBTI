// NBTI 共享可变状态与常量
// 作为明确的模块边界：所有需要跨模块读写的可变状态都集中在这个可变的 state 对象上，
// 避免拆分出 ES Module 之后出现隐式的跨文件全局变量。

export const state = {
  // ---- 会话与题目进度 ----
  conversationId: '',
  currentQuestion: 0,
  totalQuestions: 25,
  scores: { nb: 0, bh: 0, tf: 0, ip: 0 },
  currentResult: null,
  nextDim: 'NB',
  canConclude: false,
  answerLocked: false,
  incompleteRetryCount: 0,

  // ---- 主题 / 风格选择 ----
  selectedTheme: 'workplace',
  selectedStyle: '暴躁老油条',
  themesList: [],
  stylesList: [],
  welcomeStep: 'theme',

  // ---- 运行配置 ----
  minQuestions: 12,
  maxQuestions: 16,
  configLoaded: false,
  preloadEnabled: true,

  // ---- 预载缓存与流式请求 ----
  preloadCache: {},
  preloadMessageMap: {},
  preloadVersion: 0,
  activeQuestionRequestId: 0,
  preloadStatus: 'idle',
  preloadCount: 0,
  preloadTotal: 0,

  // ---- 快速模式（仅前端编排，不影响后端） ----
  fastMode: true,

  // ---- 首题预热草稿 ----
  warmupDraft: null,
  warmupInFlight: false,
  warmupPromise: null,

  // ---- 其它 ----
  firstQuestionCache: null
};

// 题目不完整时的最大重试次数
export const MAX_INCOMPLETE_RETRIES = 3;

// 风格对应的 emoji
export const STYLE_EMOJIS = {
  '暴躁老油条': '😤',
  '冷面纪录片': '🎬',
  '戏精闺蜜': '💅',
  '霸总文学': '👑',
  '玄学算命': '🔮',
  '二次元萌系': '🌸',
  '官方MBTI': '🧠'
};

// 9 主题分组：核心 3 主题 + 热门 6 主题（热门主题带 NEW 角标）
export const CORE_THEME_IDS = ['workplace', 'animal', 'color'];
export const NEW_THEME_IDS = ['love', 'social', 'mbti', 'brainhol', 'money', 'spirit'];

// 主题信息兜底表（API 不可用时保证 9 主题可渲染/可选择）
export const THEME_INFO_MAP = {
  workplace: { id: 'workplace', name: '职场人格', icon: '💼', description: '经典职场人格测试，16种职场角色定位' },
  animal: { id: 'animal', name: '动物系人格', icon: '🐾', description: '你是哪种动物？揭秘你的野性人格' },
  color: { id: 'color', name: '色彩人格', icon: '🎨', description: '你的灵魂是什么颜色？色彩心理学测试' },
  love: { id: 'love', name: '恋爱人格', icon: '💕', description: '你在恋爱中是什么类型？揭秘你的爱情模式' },
  social: { id: 'social', name: '社交人格', icon: '👥', description: '你是社牛还是社恐？社交场合真实的你' },
  mbti: { id: 'mbti', name: '官方MBTI', icon: '🧠', description: '经典16型人格测试，权威心理学视角' },
  brainhol: { id: 'brainhol', name: '脑洞人格', icon: '🤯', description: '奇葩脑洞测试，你的脑回路有多清奇' },
  money: { id: 'money', name: '搞钱人格', icon: '💰', description: '你的财富观是哪种流派？揭秘你的搞钱体质' },
  spirit: { id: 'spirit', name: '精神状态检测', icon: '🔋', description: '当代年轻人精神图鉴，测测你的精神电量' }
};

// 主题选择卡片专属色（取自各主题 primary 色）
export const THEME_CARD_COLORS = {
  workplace: '#2563EB',
  animal: '#059669',
  color: '#8B5CF6',
  love: '#EC4899',
  social: '#F97316',
  mbti: '#6366F1',
  brainhol: '#A855F7',
  money: '#F59E0B',
  spirit: '#7C3AED'
};

export function getThemeInfo(themeId) {
  const fromList = state.themesList.find(t => t.id === themeId);
  if (fromList) return { id: fromList.id, name: fromList.name, icon: fromList.icon };
  return THEME_INFO_MAP[themeId] || THEME_INFO_MAP.workplace;
}
