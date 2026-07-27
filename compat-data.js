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

  var ALL_TYPES = {};
  Object.keys(TYPES).forEach(function (k) { ALL_TYPES[k] = TYPES[k]; });
  Object.keys(ANIMAL_TYPES).forEach(function (k) { ALL_TYPES[k + '_animal'] = ANIMAL_TYPES[k]; });

  var EASTER_EGGS = ['schrodinger', 'hexagon', 'buddha', 'twoface', 'meme_lord'];

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

  var TITLE_POOLS = {
    3: ['同频搭子', '灵魂共振', '一个频道的'],
    1: ['相爱相杀', '塑料同事情', '对抗路同事']
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
    if (upper.length === 4 && (TYPES[upper] || ANIMAL_TYPES[upper])) return upper;
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
    if (category === 'animal' && ANIMAL_TYPES[t]) return ANIMAL_TYPES[t];
    if (TYPES[t]) return TYPES[t];
    if (ANIMAL_TYPES[t]) return ANIMAL_TYPES[t];
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

    var typeTable = category === 'animal' ? ANIMAL_TYPES : TYPES;
    var commentTable = category === 'animal' ? ANIMAL_COMMENTS : COMMENTS;

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

    for (var i = 0; i < DIMS.length; i++) {
      var d = DIMS[i];
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
    var title;
    if (sameCount === 4) {
      score = 96;
      title = category === 'animal' ? '世另兽' : '世另我';
    } else if (sameCount === 0) {
      score += 6;
      title = '欢喜冤家';
    } else if (sameCount === 3) {
      title = pick(TITLE_POOLS[3], seed);
    } else if (sameCount === 2) {
      var nameA = typeTable[a] ? typeTable[a].name : a;
      var nameB = typeTable[b] ? typeTable[b].name : b;
      title = nameA + '遇上' + nameB;
    } else {
      title = pick(TITLE_POOLS[1], seed);
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
    EASTER_EGGS: EASTER_EGGS,
    ANIMAL_CP_PRESETS: ANIMAL_CP_PRESETS,
    getCompat: getCompat,
    getTypeInfo: getTypeInfo,
    getAnimalCPList: getAnimalCPList
  };
})();