(function () {
  var TYPES = {
    NBTI: { name: '卷王', tagline: '我不是在加班，我是在修行', category: 'workplace' },
    NBTP: { name: '棋手', tagline: '棋盘上就我一个活人', category: 'workplace' },
    NBFI: { name: '独狼', tagline: '一个人干翻一个部门', category: 'workplace' },
    NBFP: { name: '浪子', tagline: '简历像一部冒险小说', category: 'workplace' },
    NHTI: { name: '霸总', tagline: '我不是在 PUA 你', category: 'workplace' },
    NHTP: { name: '教练', tagline: '我培养英雄', category: 'workplace' },
    NHFI: { name: '护犊子', tagline: '天塌了我顶着', category: 'workplace' },
    NHFP: { name: '气氛组', tagline: '公司没我早散了', category: 'workplace' },
    SBTI: { name: '工蚁', tagline: '我让所有灯都亮着', category: 'workplace' },
    SBTP: { name: '人形计算器', tagline: '感情会影响判断', category: 'workplace' },
    SBFI: { name: '螺丝钉', tagline: '最无聊但最不可替代', category: 'workplace' },
    SBFP: { name: '扫地僧', tagline: '你以为我是青铜', category: 'workplace' },
    SHTI: { name: '大管家', tagline: '诸葛亮都没我会排', category: 'workplace' },
    SHTP: { name: '质检警察', tagline: '99.9% 不行，要 100%', category: 'workplace' },
    SHFI: { name: '居委会大妈', tagline: '有矛盾找我', category: 'workplace' },
    SHFP: { name: '职场空气', tagline: '随缘随风随工资条', category: 'workplace' }
  };

  var ANIMAL_TYPES = {
    NBTI: { name: '东北虎', tagline: '丛林之王，独来独往的顶级猎手', category: 'animal' },
    NBTP: { name: '狐狸', tagline: '聪明狡黠，算无遗策的谋略家', category: 'animal' },
    NBFI: { name: '雪豹', tagline: '高山隐士，一击致命的独行侠', category: 'animal' },
    NBFP: { name: '猎豹', tagline: '速度之王，永远在追逐下一个目标', category: 'animal' },
    NHTI: { name: '狮王', tagline: '草原霸主，威严不容置疑的领袖', category: 'animal' },
    NHTP: { name: '头狼', tagline: '狼群之首，带领团队走向胜利', category: 'animal' },
    NHFI: { name: '棕熊', tagline: '护崽狂魔，谁敢动我的人试试', category: 'animal' },
    NHFP: { name: '金毛', tagline: '快乐小狗，团队的气氛担当', category: 'animal' },
    SBTI: { name: '工蜂', tagline: '勤勤恳恳，蜂巢的无名英雄', category: 'animal' },
    SBTP: { name: '猫头鹰', tagline: '夜视之眼，冷静精准的观察者', category: 'animal' },
    SBFI: { name: '树懒', tagline: '慢活大师，与世无争的哲学家', category: 'animal' },
    SBFP: { name: '章鱼', tagline: '伪装大师，深藏不露的智者', category: 'animal' },
    SHTI: { name: '大象', tagline: '记忆超群，稳重可靠的族长', category: 'animal' },
    SHTP: { name: '黑猫', tagline: '完美主义，细节决定一切', category: 'animal' },
    SHFI: { name: '海豚', tagline: '治愈系天使，海里的心理医生', category: 'animal' },
    SHFP: { name: '水母', tagline: '随波逐流，海洋里的透明精灵', category: 'animal' }
  };

  var LOVE_TYPES = {
    NBTI: { name: '爱情架构师', tagline: '恋爱是项目管理，目标明确执行到位', category: 'love' },
    NBTP: { name: '海王本王', tagline: '万花丛中过，片叶不沾身', category: 'love' },
    NBFI: { name: '忠犬骑士', tagline: '爱你这件事，我单方面宣布终身有效', category: 'love' },
    NBFP: { name: '浪漫游侠', tagline: '爱你时全力以赴，缘尽时潇洒转身', category: 'love' },
    NHTI: { name: '恋爱CEO', tagline: '我们的五年规划我做好了，签字吧', category: 'love' },
    NHTP: { name: '理智贴贴怪', tagline: '嘴上说随缘，身体却很诚实地粘着你', category: 'love' },
    NHFI: { name: '热恋永动机', tagline: '对你的喜欢24小时营业，永不打烊', category: 'love' },
    NHFP: { name: '恋爱脑本脑', tagline: '上头是日常，理智已离家出走', category: 'love' },
    SBTI: { name: '闷声守候者', tagline: '不说爱，但余生都是你的Plan A', category: 'love' },
    SBTP: { name: '爱情绝缘体', tagline: '恋爱？哦，等我忙完这阵再说', category: 'love' },
    SBFI: { name: '暗恋收藏家', tagline: '把你放在心里最深处，谁也不告诉', category: 'love' },
    SBFP: { name: '灵魂独行客', tagline: '心动常有，行动全无', category: 'love' },
    SHTI: { name: '温水伴侣', tagline: '不浪漫但靠谱，爱都藏在细节里', category: 'love' },
    SHTP: { name: '备胎转正委', tagline: '你不找我我不找你，你找我我一直在', category: 'love' },
    SHFI: { name: '望夫石', tagline: '爱上了就是一辈子，等也是', category: 'love' },
    SHFP: { name: '恋爱NPC', tagline: '在别人的爱情故事里，我永远在待机', category: 'love' }
  };

  var SOCIAL_TYPES = {
    NBTI: { name: '社交悍匪', tagline: '组局我说了算，社恐都给我让道', category: 'social' },
    NBTP: { name: '气氛操盘手', tagline: '场子冷不了，但谁也别想指挥我', category: 'social' },
    NBFI: { name: '聚会麦霸', tagline: 'KTV的麦在我手里，谁抢跟谁急', category: 'social' },
    NBFP: { name: '快乐显眼包', tagline: '有我在的地方，尴尬不存在', category: 'social' },
    NHTI: { name: '社交导演', tagline: '全场人际关系，我一手编排', category: 'social' },
    NHTP: { name: '人形WiFi', tagline: '走到哪连到哪，信号满格', category: 'social' },
    NHFI: { name: '热场暖宝宝', tagline: '所有人的情绪我都要照顾到', category: 'social' },
    NHFP: { name: '捧场王', tagline: '哈哈哈哈哈哈，你讲得真好', category: 'social' },
    SBTI: { name: '高冷观察员', tagline: '我不说话，但全场尽在掌握', category: 'social' },
    SBTP: { name: '社交节能侠', tagline: '能打字绝不语音，能线上绝不见面', category: 'social' },
    SBFI: { name: '社恐leader', tagline: '心里很慌，但场面必须撑住', category: 'social' },
    SBFP: { name: '隐形听众', tagline: '我在听，你们聊，别cue我', category: 'social' },
    SHTI: { name: '幕后军师', tagline: '饭局我不组，但去哪吃听我的', category: 'social' },
    SHTP: { name: '树洞本洞', tagline: '所有人的秘密都在我这，嘴比保险柜严', category: 'social' },
    SHFI: { name: '温柔港湾', tagline: '朋友有难第一个想到我', category: 'social' },
    SHFP: { name: '人形抱枕', tagline: '不说话，但抱着很安心', category: 'social' }
  };

  var MBTI_TYPES = {
    ISTJ: { name: '检查员', tagline: '认真严谨、负责任的务实者', category: 'mbti' },
    ISFJ: { name: '保护者', tagline: '温暖体贴、忠于职守的守护者', category: 'mbti' },
    INFJ: { name: '提倡者', tagline: '富有洞察力、理想主义的引路人', category: 'mbti' },
    INTJ: { name: '建筑师', tagline: '独立思考、战略导向的规划者', category: 'mbti' },
    ISTP: { name: '鉴赏家', tagline: '冷静理性、擅长动手的实践者', category: 'mbti' },
    ISFP: { name: '探险家', tagline: '温和敏感、热爱艺术的体验者', category: 'mbti' },
    INFP: { name: '调停者', tagline: '理想主义、富同情心的梦想家', category: 'mbti' },
    INTP: { name: '逻辑学家', tagline: '思辨缜密、追求真理的思考者', category: 'mbti' },
    ESTP: { name: '企业家', tagline: '精力充沛、行动力强的冒险家', category: 'mbti' },
    ESFP: { name: '表演者', tagline: '热情外向、活在当下的娱乐者', category: 'mbti' },
    ENFP: { name: '竞选者', tagline: '充满热情、富有创造力的激励者', category: 'mbti' },
    ENTP: { name: '辩论家', tagline: '聪明好奇、喜欢挑战的创新者', category: 'mbti' },
    ESTJ: { name: '总经理', tagline: '务实高效、组织能力强的管理者', category: 'mbti' },
    ESFJ: { name: '执政官', tagline: '热心友善、善于合作的协调者', category: 'mbti' },
    ENFJ: { name: '主人公', tagline: '富有魅力、天生的领导者', category: 'mbti' },
    ENTJ: { name: '指挥官', tagline: '果断自信、战略眼光的领袖', category: 'mbti' }
  };

  var BRAINHOL_TYPES = {
    NBTI: { name: '星际病院院长', tagline: '地球容不下我，我是来殖民笑点的', category: 'brainhol' },
    NBTP: { name: '宇宙抬杠机', tagline: '和外星人都能抬杠，杠出银河系', category: 'brainhol' },
    NBFI: { name: '外星电波人', tagline: '我的信号，人类接收不到', category: 'brainhol' },
    NBFP: { name: '银河gai溜子', tagline: '在宇宙的街头巷尾瞎逛，到处惹事', category: 'brainhol' },
    NHTI: { name: '伪装地球人', tagline: '潜伏十年，开口就暴露', category: 'brainhol' },
    NHTP: { name: '人形bug', tagline: '出厂设置就有问题，懒得修了', category: 'brainhol' },
    NHFI: { name: '脑洞永动机', tagline: '一秒三个离谱想法，全是发病现场', category: 'brainhol' },
    NHFP: { name: '抽象艺术家', tagline: '没人懂我，包括我自己', category: 'brainhol' },
    SBTI: { name: '地球卧底', tagline: '表面正常，档案厚得能出书', category: 'brainhol' },
    SBTP: { name: '潜伏期患者', tagline: '看着正常，其实病得不轻，只是没到时候', category: 'brainhol' },
    SBFI: { name: '静默发病区', tagline: '脑内世界大战，表面岁月静好', category: 'brainhol' },
    SBFP: { name: '地心脑洞仓', tagline: '脑洞深埋地心，一挖一个喷涌', category: 'brainhol' },
    SHTI: { name: '正经胡说家', tagline: '用最正经的脸，说最离谱的话', category: 'brainhol' },
    SHTP: { name: '伪正常之光', tagline: '全病区最像正常人的病人', category: 'brainhol' },
    SHFI: { name: '深夜emo诗人', tagline: '凌晨三点，我和宇宙对话', category: 'brainhol' },
    SHFP: { name: '透明病友', tagline: '病得很安静，安静到没人发现', category: 'brainhol' }
  };

  var MONEY_TYPES = {
    NBTI: { name: '复利孤狼', tagline: '一个人一台电脑，闷声滚雪球', category: 'money' },
    NBTP: { name: '量化赌徒', tagline: 'K线是我的战场，止损比谁都快', category: 'money' },
    NBFI: { name: '风口赌徒', tagline: 'All in是一种信仰，输了从头再来', category: 'money' },
    NBFP: { name: '野路子游资', tagline: '直觉告诉我，这波能翻倍', category: 'money' },
    NHTI: { name: '搞钱合伙人', tagline: '组队开黑，一起财富自由', category: 'money' },
    NHTP: { name: '带货团长', tagline: '兄弟们跟我冲，这波团购必赚', category: 'money' },
    NHFI: { name: '画饼资本家', tagline: '梦想很大，跟我干的人更多', category: 'money' },
    NHFP: { name: '搞钱气氛组', tagline: '天天喊搞钱，先搞个奶茶钱', category: 'money' },
    SBTI: { name: '稳健复利佬', tagline: '年化5%，但我睡得着觉', category: 'money' },
    SBTP: { name: '薅羊毛宗师', tagline: '满减凑单，精确到分', category: 'money' },
    SBFI: { name: '存钱罐本罐', tagline: '钱放我这，比银行还安全', category: 'money' },
    SBFP: { name: '抠门小能手', tagline: '不是没钱，是钱花得心疼', category: 'money' },
    SHTI: { name: '家庭CFO', tagline: '全家财政大权，我一人执掌', category: 'money' },
    SHTP: { name: 'AA活算盘', tagline: '这顿58块3毛，转我58就行', category: 'money' },
    SHFI: { name: '守财暖炉', tagline: '钱不多，但都花在在乎的人身上', category: 'money' },
    SHFP: { name: '月光佛系人', tagline: '钱是身外之物，花完再说', category: 'money' }
  };

  var SPIRIT_TYPES = {
    NBTI: { name: '永动机卷王', tagline: '精力用不完，自律到可怕', category: 'spirit' },
    NBTP: { name: '特种兵玩家', tagline: '一天打卡八个景点，攻略全靠临场', category: 'spirit' },
    NBFI: { name: '热血小太阳', tagline: '每天元气满满，朋友圈正能量批发商', category: 'spirit' },
    NBFP: { name: '快乐疯批', tagline: '精神状态遥遥领先，快乐得不讲道理', category: 'spirit' },
    NHTI: { name: '紧绷发条人', tagline: '表面积极上进，内心弦快崩了', category: 'spirit' },
    NHTP: { name: '亢奋型焦虑', tagline: '一边打鸡血，一边心慌慌', category: 'spirit' },
    NHFI: { name: '元气哭包', tagline: '白天哈哈哈，深夜嘤嘤嘤，早八照样起', category: 'spirit' },
    NHFP: { name: '情绪过山车', tagline: '上一秒嘻嘻，下一秒不嘻嘻', category: 'spirit' },
    SBTI: { name: '低电量模式', tagline: '节能运行中，请勿打扰', category: 'spirit' },
    SBTP: { name: '摆烂哲学家', tagline: '不是躺平，是与世界和解', category: 'spirit' },
    SBFI: { name: '淡淡的', tagline: '对什么都淡淡的，长期稳定地淡淡的', category: 'spirit' },
    SBFP: { name: '人间小透明', tagline: '存在感低，情绪也低，平稳地低', category: 'spirit' },
    SHTI: { name: '体面崩溃人', tagline: '哭都要挑时间，崩溃都按计划', category: 'spirit' },
    SHTP: { name: '内耗大师', tagline: '脑子里开了个批斗会，批的是自己', category: 'spirit' },
    SHFI: { name: '深夜emo电台', tagline: '凌晨准时开播，天亮自动闭麦', category: 'spirit' },
    SHFP: { name: '破碎感本感', tagline: '风一吹就碎，碎了还自己扫', category: 'spirit' }
  };

  var COLOR_TYPES = {
    NBTI: { name: '中国红', tagline: '热情似火，天生的领导者', category: 'color' },
    NBTP: { name: '皇家蓝', tagline: '深邃睿智，运筹帷幄的策略家', category: 'color' },
    NBFI: { name: '黑金', tagline: '神秘高贵，不可触碰的存在', category: 'color' },
    NBFP: { name: '橙红', tagline: '活力四射，永远年轻永远热血', category: 'color' },
    NHTI: { name: '酒红', tagline: '成熟霸气，掌控全场的女王', category: 'color' },
    NHTP: { name: '焦糖色', tagline: '温暖治愈，人生导师般的存在', category: 'color' },
    NHFI: { name: '珊瑚粉', tagline: '温柔守护，治愈系小太阳', category: 'color' },
    NHFP: { name: '柠檬黄', tagline: '快乐源泉，走到哪亮到哪', category: 'color' },
    SBTI: { name: '石灰白', tagline: '默默奉献，最可靠的底色', category: 'color' },
    SBTP: { name: '墨黑', tagline: '理性深邃，数据就是一切', category: 'color' },
    SBFI: { name: '奶茶色', tagline: '温柔百搭，最舒服的存在', category: 'color' },
    SBFP: { name: '雾霾蓝', tagline: '文艺复古，有故事的颜色', category: 'color' },
    SHTI: { name: '橄榄绿', tagline: '沉稳务实，靠谱的代言人', category: 'color' },
    SHTP: { name: '藏青', tagline: '严谨细致，零容错的完美主义', category: 'color' },
    SHFI: { name: '豆沙粉', tagline: '善解人意，最好的倾听者', category: 'color' },
    SHFP: { name: '米白', tagline: '佛系随缘，存在感极低的小透明', category: 'color' }
  };

  var TYPE_TABLES = {
    workplace: TYPES,
    animal: ANIMAL_TYPES,
    color: COLOR_TYPES,
    love: LOVE_TYPES,
    social: SOCIAL_TYPES,
    mbti: MBTI_TYPES,
    brainhol: BRAINHOL_TYPES,
    money: MONEY_TYPES,
    spirit: SPIRIT_TYPES
  };

  var ALL_TYPES = {};
  Object.keys(TYPE_TABLES).forEach(function (themeId) {
    var table = TYPE_TABLES[themeId];
    Object.keys(table).forEach(function (k) {
      if (themeId === 'workplace') ALL_TYPES[k] = table[k];
      else ALL_TYPES[k + '_' + themeId] = table[k];
    });
  });

  var EASTER_EGGS = ['schrodinger', 'hexagon', 'buddha', 'twoface', 'double', 'meme_lord', 'mouthpiece'];

  var EASTER_RESULT = {
    score: null,
    title: '跳出三界外',
    verdict: '彩蛋人格不在五行中，合盘仅供参考，建议直接当面 battle。',
    dims: []
  };

  var DIMS = [
    { key: 'NB', pair: ['N', 'S'], label: '节奏 · 能动 vs 稳态', same: '同频', diff: '互斥' },
    { key: 'BH', pair: ['B', 'H'], label: '社交 · 边界 vs 合群', same: '同频', diff: '互补' },
    { key: 'TF', pair: ['T', 'F'], label: '决策 · 理性 vs 感性', same: '同频', diff: '互补' },
    { key: 'IP', pair: ['I', 'P'], label: '执行 · 闭环 vs 灵活', same: '同频', diff: '互斥' }
  ];

  var DIM_TABLES = {
    workplace: DIMS,
    animal: [
      { key: 'NB', pair: ['N', 'S'], label: '食性 · 猎食 vs 食草', same: '同频', diff: '互斥' },
      { key: 'BH', pair: ['B', 'H'], label: '群性 · 独居 vs 群居', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '血性 · 冷血 vs 热血', same: '同频', diff: '互补' },
      { key: 'IP', pair: ['I', 'P'], label: '作息 · 昼行 vs 夜行', same: '同频', diff: '互斥' }
    ],
    color: [
      { key: 'NB', pair: ['N', 'S'], label: '色温 · 暖色 vs 冷色', same: '同频', diff: '对冲' },
      { key: 'BH', pair: ['B', 'H'], label: '纯度 · 纯色 vs 混色', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '明度 · 深色 vs 浅色', same: '同频', diff: '互补' },
      { key: 'IP', pair: ['I', 'P'], label: '亮度 · 亮色 vs 暗色', same: '同频', diff: '互斥' }
    ],
    love: [
      { key: 'NB', pair: ['N', 'S'], label: '姿态 · 主动 vs 被动', same: '同频', diff: '拉扯' },
      { key: 'BH', pair: ['B', 'H'], label: '距离 · 独立 vs 依恋', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '脑回路 · 理性 vs 感性', same: '同频', diff: '互补' },
      { key: 'IP', pair: ['I', 'P'], label: '承诺 · 笃定 vs 随缘', same: '同频', diff: '互斥' }
    ],
    social: [
      { key: 'NB', pair: ['N', 'S'], label: '电量 · 外向 vs 内向', same: '同频', diff: '互补' },
      { key: 'BH', pair: ['B', 'H'], label: '距离 · 边界 vs 共情', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '频道 · 逻辑 vs 情绪', same: '同频', diff: '互补' },
      { key: 'IP', pair: ['I', 'P'], label: '位置 · 主导 vs 配合', same: '同频', diff: '互斥' }
    ],
    mbti: [
      { key: 'EI', pair: ['E', 'I'], label: '精力 · 外倾 vs 内倾', same: '同频', diff: '互补' },
      { key: 'SN', pair: ['S', 'N'], label: '感知 · 感觉 vs 直觉', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '判断 · 思考 vs 情感', same: '同频', diff: '互补' },
      { key: 'JP', pair: ['J', 'P'], label: '生活 · 判断 vs 感知', same: '同频', diff: '互斥' }
    ],
    brainhol: [
      { key: 'NB', pair: ['N', 'S'], label: '籍贯 · 外星 vs 地球', same: '同频', diff: '互斥' },
      { key: 'BH', pair: ['B', 'H'], label: '病情 · 深井冰 vs 正常人', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '病种 · 神经病 vs 精神病', same: '同频', diff: '互补' },
      { key: 'IP', pair: ['I', 'P'], label: '病程 · 发病 vs 潜伏期', same: '同频', diff: '互斥' }
    ],
    money: [
      { key: 'NB', pair: ['N', 'S'], label: '打法 · 狼性 vs 稳守', same: '同频', diff: '互斥' },
      { key: 'BH', pair: ['B', 'H'], label: '队形 · 单干 vs 抱团', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '算盘 · 精算 vs 感觉', same: '同频', diff: '互补' },
      { key: 'IP', pair: ['I', 'P'], label: '周期 · 长线 vs 短线', same: '同频', diff: '互斥' }
    ],
    spirit: [
      { key: 'NB', pair: ['N', 'S'], label: '电量 · 亢奋 vs 低迷', same: '同频', diff: '互斥' },
      { key: 'BH', pair: ['B', 'H'], label: '内核 · 稳定 vs 破防', same: '同频', diff: '互补' },
      { key: 'TF', pair: ['T', 'F'], label: '系统 · 理智 vs 感性', same: '同频', diff: '互补' },
      { key: 'IP', pair: ['I', 'P'], label: '节奏 · 规律 vs 混乱', same: '同频', diff: '互斥' }
    ]
  };

  var COMMENTS = [
    {
      same: ['连摸鱼都踩着同一个节拍，工位像装了同步器。', '一个眼神就知道对方要卷还是要躺，默契得让 HR 害怕。'],
      diff: ['一个猛踩油门一个死拉手刹，合作项目秒变拔河现场。', '你想冲锋他想守塔，开会像在打辩论赛。']
    },
    {
      same: ['边界感同款，谁也别想 PUA 你们俩。', '社交电量同款，团建逃兵或气氛担当，要做都一起做。'],
      diff: ['一个独狼一个拉群，组队干活刚好互补，谁都不尴尬。', '你守边界他搞联结，一个挡枪一个递水，配合意外丝滑。']
    },
    {
      same: ['脑回路同型号，吵起来都用同一套逻辑，谁也说服不了谁。', '一个用数据说话一个也是，感性派在旁边看得直摇头。'],
      diff: ['一个泼冷水一个递纸巾，理性感性刚好拼成一个完整的人。', '你算账他共情，吵架都像交叉学科研讨会，最后总能圆回来。']
    },
    {
      same: ['交付节奏复制粘贴，deadline 在你们面前就是摆设。', '要么一起闭环到底，要么一起灵活跑路，整齐划一。'],
      diff: ['一个要闭环一个要变通，项目群里的火药味比咖啡还提神。', '你嫌他没谱他嫌你死板，互相看不惯又干不掉对方。']
    }
  ];

  var ANIMAL_COMMENTS = [
    {
      same: ['狩猎节奏神同步，草原上最佳拍档非你们莫属。', '一个眼神就知道对方是要出击还是要潜伏，默契到可怕。'],
      diff: ['一个是冲刺型选手一个是耐力型选手，捕猎路线永远对不上。', '你喜欢正面刚他喜欢绕后，战术分歧比猎物还难搞。']
    },
    {
      same: ['领地意识同款，要么一起占山为王，要么一起云游四方。', '社交距离拿捏得一模一样，谁越界谁先炸毛。'],
      diff: ['一个独居一个群居，你需要独处充电他需要贴贴续命，刚好互补。', '你划地盘他搞团建，一个守家一个外交，配合得天衣无缝。']
    },
    {
      same: ['都是冷血/热血同款，处理问题的逻辑出奇一致。', '要么一起冷静分析局势，要么一起热血上头冲锋。'],
      diff: ['一个冷血冷静一个热血共情，你负责拍板他负责安慰，完美搭配。', '你算计得失他在乎感受，吵架像捕食者撞上治愈系。']
    },
    {
      same: ['作息同款生物钟，要么都是昼行猛士要么都是夜行动物。', '出动时间神同步，捕猎/休息节奏完全一致。'],
      diff: ['你白天精神他晚上兴奋，约会像跨时区恋爱。', '一个昼行一个夜行，你睡觉他蹦迪，时差感拉满。']
    }
  ];

  var LOVE_COMMENTS = [
    {
      same: ['一个主动撩一个主动接，暧昧期直接快进到官宣。', '都等着对方先开口，暗恋能谈成马拉松。'],
      diff: ['一个猛冲一个后退，你追我逃的戏码天天上演。', '表白与装傻的极限拉扯，旁观者都替你们着急。']
    },
    {
      same: ['都要自己的空间，恋爱谈成两个星球的礼貌互访。', '粘人程度同款，24小时连体婴也不嫌腻。'],
      diff: ['一个要自由一个要贴贴，距离感刚好调成最舒服的档位。', '你独立他依恋，一个放风筝一个拽线，谁也丢不了谁。']
    },
    {
      same: ['吵架都讲道理，恋爱谈成辩论赛，赢了道理输了气氛。', '两个恋爱脑互相上头，纪念日能过成偶像剧。'],
      diff: ['一个讲道理一个要态度，鸡同鸭讲又莫名互补。', '你泼冷水他递糖，理性和感性刚好拼成一个完整恋人。']
    },
    {
      same: ['都奔着结婚去，五年规划直接对齐颗粒度。', '都随缘，恋爱谈成开盲盒，惊喜刺激又心慌。'],
      diff: ['一个要承诺一个要自由，安全感与飘忽感的世纪对决。', '你想定下来他想再看看，进度条永远差半格。']
    }
  ];

  var SOCIAL_COMMENTS = [
    {
      same: ['两个社牛同场，场子热到要开空调。', '两个社恐互相点头，安静也是一种默契。'],
      diff: ['一个满场飞一个角落蹲，社交电量刚好能互相借。', '你负责热场他负责收尾，一场饭局两种圆满。']
    },
    {
      same: ['边界感同款，谁也不会半夜打电话哭诉求安慰。', '共情力同款，抱头痛哭的画面过于和谐。'],
      diff: ['一个有墙一个没墙，你挡枪他递纸，配合意外丝滑。', '他负责温暖全场，你负责把他拽回安全距离。']
    },
    {
      same: ['都用逻辑说话，群聊里就你俩在认真抬杠。', '情绪价值互给，一句话就能 get 到对方的点。'],
      diff: ['一个讲道理一个讲感受，聊着聊着就变成互相翻译。', '你冷静分析他暴风共情，朋友的烦恼被你们双杀。']
    },
    {
      same: ['都想控场，组个局能开成董事会。', '都习惯配合，没人拿主意，饭局能约到明年。'],
      diff: ['一个主导一个配合，天生的主持与嘉宾配置。', '你定地方他捧场，社交流水线运转丝滑。']
    }
  ];

  var MBTI_COMMENTS = [
    {
      same: ['充电方式一致，社交续航同款，谁也不拖谁后腿。', '都是外倾/内倾同款，相处节奏天然合拍。'],
      diff: ['一个从社交回血一个靠独处充电，尊重差异就是高级浪漫。', '外倾带内倾看世界，内倾教外倾静下来，刚好互补。']
    },
    {
      same: ['都关注事实细节，沟通零成本，像在用同一套数据库。', '都靠直觉联想，脑电波直接对接，聊三天三夜不累。'],
      diff: ['一个看眼前一个看远方，视野拼起来就是全景图。', '感觉型落地，直觉型起飞，一个管现实一个管可能性。']
    },
    {
      same: ['决策都用同一套逻辑，争执少效率高，理性CP的典范。', '都以情感为先，互相理解从不冷战，温柔加倍。'],
      diff: ['思考型给方案，情感型给温度，刚柔并济的经典组合。', '一个讲理一个讲情，磨合好了就是最稳的互补结构。']
    },
    {
      same: ['都爱做计划，行程表精确到分钟，执行力恐怖如斯。', '都随性灵活，说走就走，自由灵魂的双向奔赴。'],
      diff: ['一个要闭环一个要开放，计划与变化天天打架又天天和解。', '判断型收，感知型放，生活需要这一点张力。']
    }
  ];

  var BRAINHOL_COMMENTS = [
    {
      same: ['两个外星人用母语交流，地球人完全插不上话。', '都是地球籍，正常得让病友们怀疑人生。'],
      diff: ['一个星际漫游一个脚踏实地，跨服聊天居然不卡。', '你负责离谱他负责把离谱翻译成地球语。']
    },
    {
      same: ['病情一致，发病时间都能同步，病房住成双人套间。', '都是正常人（自称），互相拆台的姿势都很健康。'],
      diff: ['一个深井冰一个正常人，一个敢想一个敢拦，绝配。', '他的脑洞你来兜底，你的正常他来打破。']
    },
    {
      same: ['病种相同，交流病情像在开学术研讨会。', '思维跳脱程度同款，上一秒宇宙下一秒晚饭。'],
      diff: ['一个神经病一个精神病，病理不同但处方可以共享。', '你离谱得有逻辑，他离谱得有感情，合起来是部完整作品。']
    },
    {
      same: ['都处于发病期，谁也别嫌弃谁的症状。', '都在潜伏期，表面岁月静好，暗地互相试探。'],
      diff: ['一个正在发病一个还在潜伏，先发病带动后发病。', '你的突发奇想，他的蓄谋已久，时间差产生美。']
    }
  ];

  var MONEY_COMMENTS = [
    {
      same: ['两匹狼盯上同一块肉，要么合伙要么对决。', '都求稳，账户余额涨得慢但睡得都香。'],
      diff: ['一个敢冲一个敢守，冲锋的有人兜底，守家的有人开路。', '你狼性他稳健，组合起来是进可攻退可守的基金配置。']
    },
    {
      same: ['都单干，合作像两家公司并购，流程走得飞起。', '都抱团，搞钱先搞群，人多力量大。'],
      diff: ['一个独狼一个群居，你打猎他分肉，产业链闭环了。', '他负责组队，你负责单点突破，团战 solo 两不误。']
    },
    {
      same: ['都是精算师，恋爱开销都要做 ROI 分析。', '都凭感觉，投资靠玄学，亏了还能互相安慰。'],
      diff: ['一个算账一个直觉，数据和灵感双修，想不赚都难。', '你精算他感觉，一个避雷一个抓风口，刚好互补。']
    },
    {
      same: ['都做长线，十年后的财富自由已经预约成功。', '都做短线，快进快出，刺激是他们的多巴胺。'],
      diff: ['一个拿长线一个炒短线，你种树他摘果，节奏永远对不上。', '长线嫌短线浮躁，短线嫌长线磨叽，但收益曲线居然互补。']
    }
  ];

  var SPIRIT_COMMENTS = [
    {
      same: ['都打满鸡血，凌晨五点的朋友圈就你俩互赞。', '都低电量运行，沉默是今晚的充电器。'],
      diff: ['一个满电一个亏电，你蹦迪他躺平，互相觉得对方离谱。', '亢奋的负责发光，低迷的负责省电，能量守恒了。']
    },
    {
      same: ['内核都稳，天塌下来先拍照发朋友圈。', '都易破防，抱头痛哭的画面过于熟练。'],
      diff: ['一个稳如老狗一个一碰就碎，你当定海神针他当情绪晴雨表。', '他破防你兜底，你无聊他整活，稳与脆的奇妙平衡。']
    },
    {
      same: ['理智都在线，深夜emo与你们无关。', '感性都泛滥，看广告都能看哭，纸巾AA。'],
      diff: ['一个理性分析一个感性决堤，你讲道理他负责哭，配合默契。', '理智的把感性的从深夜拽回来，感性的教理智的怎么做人。']
    },
    {
      same: ['作息都规律，养生局约起来毫不费力。', '都混乱，昼夜颠倒二人组，早餐吃在下午三点。'],
      diff: ['一个规律一个混乱，你定的闹钟他永远听不到。', '规律党想救混乱党，混乱党想带歪规律党，持久战。']
    }
  ];

  var COLOR_COMMENTS = [
    {
      same: ['色温一致，站一起就是同色系穿搭模板。', '冷暖同款，情绪天气预报永远同步。'],
      diff: ['一暖一冷，你像夏天他像冬天，凑一起是完整四季。', '暖色负责发光，冷色负责降温，恒温组合。']
    },
    {
      same: ['都是纯色，纯粹得容不下一点杂质。', '都是混色，层次感丰富到能开画展。'],
      diff: ['一个纯粹一个层次，你负责鲜明他负责韵味。', '纯色定调，混色铺陈，配色方案天生一对。']
    },
    {
      same: ['明度相同，深到一起高级，浅到一起清新。', '深浅同款，影调统一，合照不用修图。'],
      diff: ['一深一浅，你负责质感他负责透气，光影平衡了。', '深色压场，浅色提亮，画面终于有了对比度。']
    },
    {
      same: ['亮度都高，走哪都是人群高光。', '亮度都暗，低调到快隐身，但质感拉满。'],
      diff: ['一亮一暗，你当聚光灯他当氛围组，曝光刚好。', '亮色抓眼球，暗色留余味，一张一弛。']
    }
  ];

  var COMMENT_TABLES = {
    workplace: COMMENTS,
    animal: ANIMAL_COMMENTS,
    color: COLOR_COMMENTS,
    love: LOVE_COMMENTS,
    social: SOCIAL_COMMENTS,
    mbti: MBTI_COMMENTS,
    brainhol: BRAINHOL_COMMENTS,
    money: MONEY_COMMENTS,
    spirit: SPIRIT_COMMENTS
  };

  var TITLE_POOLS = {
    3: ['同频搭子', '灵魂共振', '一个频道的'],
    1: ['相爱相杀', '塑料同事情', '对抗路同事']
  };

  var THEME_TITLE_POOLS = {
    love: { 3: ['命中注定', '锁死这对', '甜度超标'], 1: ['欢喜冤家', '极限拉扯', '追逃游戏'] },
    social: { 3: ['社交搭子', '营业共同体', '一个频道的'], 1: ['频道错位', '社牛与社恐', '营业反差'] },
    mbti: { 3: ['黄金搭档', '类型共振', '同频组合'], 1: ['张力组合', '互补磨合', '差异吸引'] },
    brainhol: { 3: ['病友交流', '脑波共振', '一个病房的'], 1: ['跨服聊天', '病情互搏', '离谱对撞'] },
    money: { 3: ['搞钱搭子', '财富共振', '一个金库的'], 1: ['多空对决', '算盘打架', '风口互搏'] },
    spirit: { 3: ['电量同款', '状态共振', '一个充电桩的'], 1: ['满电与亏电', '状态对冲', '情绪对撞'] }
  };

  var ANIMAL_CP_PRESETS = {
    'NBTI|NHFP': {
      score: 92,
      title: '猛虎与甜狗',
      verdict: '东北虎外表霸气内心柔软，金毛快乐小狗天生治愈系。看似反差极大，实则猛虎需要金毛的阳光融化冰冷，金毛需要猛虎的保护给足安全感。这是典型的"霸道总裁爱上我"动物版，甜到掉牙！',
      dims: [
        { label: '节奏 · 猎食 vs 食草', relation: '互补', comment: '猛虎负责打猎，小狗负责摇旗呐喊' },
        { label: '社交 · 独居 vs 群居', relation: '互补', comment: '老虎的领地只有金毛能自由进出' },
        { label: '决策 · 冷血 vs 热血', relation: '互补', comment: '外冷内热组合，决策理性+共情满分' },
        { label: '执行 · 昼行 vs 夜行', relation: '同频', comment: '都是白天活跃型，作息一致' }
      ],
      tags: ['#动物CP', '#甜宠', '#反差萌']
    },
    'NBTP|SHFI': {
      score: 88,
      title: '狐豚恋歌',
      verdict: '狐狸聪明狡黠满肚子坏水，海豚温柔治愈善解人意。狐狸的所有小心思海豚都能看穿，但海豚选择用爱包容；狐狸原本游戏人间，遇到海豚才想安定下来。智性恋天花板！',
      dims: [
        { label: '节奏 · 猎食 vs 食草', relation: '互补', comment: '狐狸捕猎海豚摸鱼，动静结合' },
        { label: '社交 · 独居 vs 群居', relation: '互补', comment: '狐狸只对海豚卸下防备' },
        { label: '决策 · 冷血 vs 热血', relation: '互补', comment: '狐狸出谋划策，海豚安抚情绪' },
        { label: '执行 · 昼行 vs 夜行', relation: '同频', comment: '白天一起玩耍晚上一起休息' }
      ],
      tags: ['#动物CP', '#智性恋', '#治愈系']
    },
    'NHTI|NHFI': {
      score: 95,
      title: '狮熊联盟',
      verdict: '狮王威严霸气，棕熊护崽狂魔。一个是草原霸主，一个是森林守护者，都是顶级王者组合。对外强强联手无人能敌，对内互相宠溺甜到发腻。这才是王炸CP！',
      dims: [
        { label: '节奏 · 猎食 vs 食草', relation: '同频', comment: '都是顶级掠食者，节奏神同步' },
        { label: '社交 · 独居 vs 合群', relation: '互补', comment: '狮王领导群伦，棕熊守护家人' },
        { label: '决策 · 冷血 vs 热血', relation: '互补', comment: '狮王决断，棕熊重情' },
        { label: '执行 · 昼行 vs 夜行', relation: '同频', comment: '白天一起巡视领地' }
      ],
      tags: ['#动物CP', '#强强联合', '#王者CP']
    },
    'NHTP|NHFP': {
      score: 90,
      title: '狼狗情缘',
      verdict: '头狼沉稳有担当，金毛热情似小太阳。头狼在外带领狼群披荆斩棘，回到金毛身边瞬间变成粘人大狗狗。平时严肃脸只对金毛笑，这是什么神仙爱情！',
      dims: [
        { label: '节奏 · 猎食 vs 食草', relation: '互补', comment: '头狼冲锋，金毛后方支援' },
        { label: '社交 · 群居 vs 群居', relation: '同频', comment: '都是群体动物，家族观念强' },
        { label: '决策 · 冷血 vs 热血', relation: '互补', comment: '理性头狼被热血金毛融化' },
        { label: '执行 · 昼行 vs 夜行', relation: '同频', comment: '一起狩猎一起休息' }
      ],
      tags: ['#动物CP', '#忠犬', '#双向奔赴']
    },
    'NBFI|SBFP': {
      score: 85,
      title: '雪豹遇章鱼',
      verdict: '雪豹高山隐士高冷神秘，章鱼深海智者深藏不露。两个都是独行侠，本应保持距离，却被彼此的神秘气质深深吸引。高手过招点到为止，这是智者之间的爱情！',
      dims: [
        { label: '节奏 · 猎食 vs 食草', relation: '同频', comment: '都是耐心型猎手，伺机而动' },
        { label: '社交 · 独居 vs 独居', relation: '同频', comment: '两个社恐的爱情，安静却美好' },
        { label: '决策 · 冷血 vs 冷血', relation: '同频', comment: '都理智得可怕，却为对方破例' },
        { label: '执行 · 昼行 vs 夜行', relation: '互斥', comment: '雪豹白天巡视，章鱼夜晚出没' }
      ],
      tags: ['#动物CP', '#高冷CP', '#智性恋']
    },
    'NBFP|SHFI': {
      score: 87,
      title: '豹豚逐浪',
      verdict: '猎豹风驰电掣永远在追逐下一个目标，海豚温柔治愈随遇而安。猎豹勇往直前海豚是他最温暖的港湾，不管猎豹跑多远，回头总能看到海豚微笑着等他回来。',
      dims: [
        { label: '节奏 · 猎食 vs 食草', relation: '互补', comment: '猎豹冲刺，海豚慢游' },
        { label: '社交 · 独居 vs 群居', relation: '互补', comment: '猎豹独行，海豚好客' },
        { label: '决策 · 冷血 vs 热血', relation: '互补', comment: '猎豹目标导向，海豚情感导向' },
        { label: '执行 · 昼行 vs 夜行', relation: '同频', comment: '白天猎豹捕猎，海豚陪伴' }
      ],
      tags: ['#动物CP', '#治愈', '#港湾']
    },
    'SHTI|SHFP': {
      score: 83,
      title: '象母与水母',
      verdict: '大象稳重可靠记忆超群，水母随波逐流自由自在。大象总是记得所有纪念日和水母的小喜好，水母则教会大象放慢脚步享受当下。靠谱大叔遇上随性少女，稳稳的幸福！',
      dims: [
        { label: '节奏 · 食草 vs 食草', relation: '同频', comment: '都是温和派，不紧不慢' },
        { label: '社交 · 合群 vs 群居', relation: '同频', comment: '都是群体动物，重视陪伴' },
        { label: '决策 · 理性 vs 感性', relation: '互补', comment: '大象规划未来，水母享受现在' },
        { label: '执行 · 昼行 vs 夜行', relation: '互斥', comment: '大象作息规律，水母随性' }
      ],
      tags: ['#动物CP', '#稳重', '#大叔萝莉']
    },
    'SBTP|SHTP': {
      score: 80,
      title: '夜猫组',
      verdict: '猫头鹰夜视之眼冷静观察者，黑猫完美主义细节控。两个都是夜行性动物，深夜是他们最佳交流时间。一起吐槽白天的人类，一起追求极致完美，吐槽役CP赛高！',
      dims: [
        { label: '节奏 · 食草 vs 食草', relation: '同频', comment: '都是慢工出细活型' },
        { label: '社交 · 边界 vs 边界', relation: '同频', comment: '都需要私人空间，互不打扰' },
        { label: '决策 · 理性 vs 理性', relation: '同频', comment: '两个理性怪，辩论到天亮' },
        { label: '执行 · 夜行 vs 夜行', relation: '同频', comment: '深夜是他们的主场' }
      ],
      tags: ['#动物CP', '#夜猫子', '#吐槽役']
    },
    'NHFI|SHFP': {
      score: 82,
      title: '熊抱水母',
      verdict: '棕熊外凶内柔护崽狂魔，水母软萌透明随波逐流。棕熊的占有欲只想把水母护在掌心，水母看似柔弱却能包容棕熊的所有坏脾气。体型差萌爆了！',
      dims: [
        { label: '节奏 · 猎食 vs 食草', relation: '互补', comment: '棕熊找吃的，水母跟着飘' },
        { label: '社交 · 合群 vs 群居', relation: '同频', comment: '都重视身边人' },
        { label: '决策 · 热血 vs 热血', relation: '同频', comment: '都是感性派，容易共情' },
        { label: '执行 · 昼行 vs 夜行', relation: '互斥', comment: '棕熊需要冬眠，水母全年无休' }
      ],
      tags: ['#动物CP', '#体型差', '#治愈']
    },
    'NBTP|NHTP': {
      score: 86,
      title: '狐狼智斗',
      verdict: '狐狸狡黠多计谋，头狼沉稳有领导力。一个是军师一个是领袖，联手打天下的配置。平时斗智斗勇互不相让，遇到外敌却能一致对外，强强联合搞事业！',
      dims: [
        { label: '节奏 · 猎食 vs 猎食', relation: '同频', comment: '都是行动派，效率极高' },
        { label: '社交 · 独居 vs 群居', relation: '互补', comment: '狐狸出鬼点子，头狼拍板执行' },
        { label: '决策 · 冷血 vs 冷血', relation: '同频', comment: '理性搭档，算无遗策' },
        { label: '执行 · 昼行 vs 昼行', relation: '同频', comment: '白天一起搞事业' }
      ],
      tags: ['#动物CP', '#事业CP', '#强强']
    }
  };

  function hashStr(s) {
    var h = 0;
    for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    return h;
  }

  function pick(arr, seed) {
    return arr[seed % arr.length];
  }

  function normalize(type) {
    if (typeof type !== 'string') return null;
    var t = type.trim();
    if (!t) return null;
    var upper = t.toUpperCase();
    if (upper.length === 4 && (TYPES[upper] || MBTI_TYPES[upper])) return upper;
    var lower = t.toLowerCase();
    if (EASTER_EGGS.indexOf(lower) !== -1) return lower;
    return null;
  }

  function getPresetKey(a, b) {
    var k1 = a + '|' + b;
    var k2 = b + '|' + a;
    if (ANIMAL_CP_PRESETS[k1]) return { key: k1, reversed: false };
    if (ANIMAL_CP_PRESETS[k2]) return { key: k2, reversed: true };
    return null;
  }

  function getTypeInfo(type, category) {
    if (!type) return { name: 'UNKNOWN', tagline: '' };
    var t = String(type).toUpperCase();
    var table = TYPE_TABLES[category];
    if (table && table[t]) return table[t];
    if (TYPES[t]) return TYPES[t];
    if (ANIMAL_TYPES[t]) return ANIMAL_TYPES[t];
    if (MBTI_TYPES[t]) return MBTI_TYPES[t];
    return { name: t, tagline: '' };
  }

  function getCompat(typeA, typeB, opts) {
    var options = opts || {};
    var category = options.category || 'workplace';
    var a = normalize(typeA);
    var b = normalize(typeB);
    if (!a || !b) return null;
    if (EASTER_EGGS.indexOf(a.toLowerCase()) !== -1 || EASTER_EGGS.indexOf(b.toLowerCase()) !== -1) {
      return { score: EASTER_RESULT.score, title: EASTER_RESULT.title, verdict: EASTER_RESULT.verdict, dims: [] };
    }

    var typeTable = TYPE_TABLES[category] || TYPES;
    var commentTable = COMMENT_TABLES[category] || COMMENTS;
    var dimTable = DIM_TABLES[category] || DIMS;

    if (category === 'animal') {
      var preset = getPresetKey(a, b);
      if (preset) {
        var presetData = ANIMAL_CP_PRESETS[preset.key];
        var result = {
          score: presetData.score,
          title: presetData.title,
          verdict: presetData.verdict,
          dims: presetData.dims.map(function (d) {
            return { dim: '', label: d.label, relation: d.relation, comment: d.comment };
          }),
          isPreset: true,
          tags: presetData.tags
        };
        var nameA = getTypeInfo(a, 'animal').name;
        var nameB = getTypeInfo(b, 'animal').name;
        result.types = { a: nameA, b: nameB };
        return result;
      }
    }

    var seed = hashStr(a + '|' + b);
    var dims = [];
    var sameCount = 0;
    var diffBonus = 0;

    for (var i = 0; i < dimTable.length; i++) {
      var d = dimTable[i];
      var same = a[i] === b[i];
      if (same) sameCount++;
      else diffBonus += (d.diff === '互补' ? 8 : 3);
      var commentArr = commentTable[i] ? (same ? commentTable[i].same : commentTable[i].diff) : COMMENTS[i].same;
      dims.push({
        dim: d.key,
        label: d.label,
        relation: same ? d.same : d.diff,
        comment: pick(commentArr, seed + i)
      });
    }

    var score = 20 + sameCount * 15 + diffBonus;
    var themePools = THEME_TITLE_POOLS[category] || {};
    var title;
    if (sameCount === 4) {
      score = 96;
      title = category === 'animal' ? '世另兽' : '世另我';
    } else if (sameCount === 0) {
      score += 6;
      title = '欢喜冤家';
    } else if (sameCount === 3) {
      title = pick(themePools[3] || TITLE_POOLS[3], seed);
    } else if (sameCount === 2) {
      var nameA = typeTable[a] ? typeTable[a].name : a;
      var nameB = typeTable[b] ? typeTable[b].name : b;
      title = nameA + '遇上' + nameB;
    } else {
      title = pick(themePools[1] || TITLE_POOLS[1], seed);
    }
    if (score > 100) score = 100;
    if (score < 0) score = 0;

    var opening;
    if (score >= 85) opening = category === 'animal' ? '你们俩像同一个巢穴长大的，' : '你们俩像同一个神经中枢分叉出来的，';
    else if (score >= 65) opening = category === 'animal' ? '这对动物CP属于老天爷赏饭吃的搭配，' : '这组合属于老天赏饭吃的搭配，';
    else if (score >= 45) opening = category === 'animal' ? '你们的关系像一份动物行为学报告，' : '你们的关系像一份需求文档，';
    else opening = category === 'animal' ? '你们俩放一起，动物园管理员连夜加高围栏，' : '你们俩放一起，HR 看了连夜改组织架构，';

    var middle = '四个维度同频 ' + sameCount + ' 个';
    if (sameCount === 4) middle += '，同步率高到离谱';
    else if (sameCount === 0) middle += '，全靠对冲产生火花';
    else middle += category === 'animal' ? '，剩下的全靠气味相投' : '，剩下的全靠磨合与演技';

    var closing;
    if (sameCount === 4) closing = category === 'animal' ? '建议原地结对，一起捕猎一起冬眠。' : '建议原地结拜，工位拼一起，一起卷死全公司。';
    else if (sameCount === 0) closing = category === 'animal' ? '建议保持安全距离，动物园分笼饲养。' : '建议保持安全距离，偶尔约饭，别一起做项目。';
    else if (score >= 65) closing = category === 'animal' ? '建议锁死这对CP，一起撒野一起浪。' : '建议锁死这对 CP，组队摸鱼效率翻倍。';
    else if (score >= 45) closing = category === 'animal' ? '能处，但别指望心电感应，多摇尾巴少呲牙。' : '能处，但别指望心有灵犀，多说话少猜。';
    else closing = category === 'animal' ? '合盘分数偏低，建议把锅甩给进化论。' : '合盘分数偏低，建议把锅甩给星座。';

    return { score: score, title: title, verdict: opening + middle + '。' + closing, dims: dims, isPreset: false };
  }

  function getAnimalCPList() {
    return Object.keys(ANIMAL_CP_PRESETS).map(function (k) {
      var parts = k.split('|');
      var data = ANIMAL_CP_PRESETS[k];
      return {
        typeA: parts[0],
        typeB: parts[1],
        nameA: ANIMAL_TYPES[parts[0]].name,
        nameB: ANIMAL_TYPES[parts[1]].name,
        score: data.score,
        title: data.title
      };
    });
  }

  window.NBTICompat = {
    TYPES: TYPES,
    ANIMAL_TYPES: ANIMAL_TYPES,
    TYPE_TABLES: TYPE_TABLES,
    DIM_TABLES: DIM_TABLES,
    EASTER_EGGS: EASTER_EGGS,
    ANIMAL_CP_PRESETS: ANIMAL_CP_PRESETS,
    getCompat: getCompat,
    getTypeInfo: getTypeInfo,
    getAnimalCPList: getAnimalCPList
  };
})();