(function () {
  // 好友合盘规则引擎：零 LLM、零依赖、纯本地确定性规则（同输入必同输出，方便测试）
  var TYPES = {
    NBTI: { name: '卷王', tagline: '我不是在加班，我是在修行' },
    NBTP: { name: '棋手', tagline: '棋盘上就我一个活人' },
    NBFI: { name: '独狼', tagline: '一个人干翻一个部门' },
    NBFP: { name: '浪子', tagline: '简历像一部冒险小说' },
    NHTI: { name: '霸总', tagline: '我不是在 PUA 你' },
    NHTP: { name: '教练', tagline: '我培养英雄' },
    NHFI: { name: '护犊子', tagline: '天塌了我顶着' },
    NHFP: { name: '气氛组', tagline: '公司没我早散了' },
    SBTI: { name: '工蚁', tagline: '我让所有灯都亮着' },
    SBTP: { name: '人形计算器', tagline: '感情会影响判断' },
    SBFI: { name: '螺丝钉', tagline: '最无聊但最不可替代' },
    SBFP: { name: '扫地僧', tagline: '你以为我是青铜' },
    SHTI: { name: '大管家', tagline: '诸葛亮都没我会排' },
    SHTP: { name: '质检警察', tagline: '99.9% 不行，要 100%' },
    SHFI: { name: '居委会大妈', tagline: '有矛盾找我' },
    SHFP: { name: '职场空气', tagline: '随缘随风随工资条' }
  };

  // 彩蛋人格：不在五行中，走兜底结构
  var EASTER_EGGS = ['schrodinger', 'hexagon', 'buddha', 'twoface', 'meme_lord'];

  var EASTER_RESULT = {
    score: null,
    title: '跳出三界外',
    verdict: '彩蛋人格不在五行中，合盘仅供参考，建议直接当面 battle。',
    dims: []
  };

  // 四维度定义（字母顺序即类型码位序）：same=同频；diff 按维度倾向分互补/互斥
  var DIMS = [
    { key: 'NB', pair: ['N', 'S'], label: '节奏 · 能动 vs 稳态', same: '同频', diff: '互斥' },
    { key: 'BH', pair: ['B', 'H'], label: '社交 · 边界 vs 合群', same: '同频', diff: '互补' },
    { key: 'TF', pair: ['T', 'F'], label: '决策 · 理性 vs 感性', same: '同频', diff: '互补' },
    { key: 'IP', pair: ['I', 'P'], label: '执行 · 闭环 vs 灵活', same: '同频', diff: '互斥' }
  ];

  // 维度短评：4 维度 × 同/反 共 8 套，每套 2 条，用类型码哈希确定性选取
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
      same: ['交付节奏复制粘贴， deadline 在你们面前就是摆设。', '要么一起闭环到底，要么一起灵活跑路，整齐划一。'],
      diff: ['一个要闭环一个要变通，项目群里的火药味比咖啡还提神。', '你嫌他没谱他嫌你死板，互相看不惯又干不掉对方。']
    }
  ];

  // 组合名池：按同维度数分档，哈希确定性选取
  var TITLE_POOLS = {
    3: ['同频搭子', '灵魂共振', '一个频道的'],
    1: ['相爱相杀', '塑料同事情', '对抗路同事']
  };

  // 确定性哈希：同输入必得同值
  function hashStr(s) {
    var h = 0;
    for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
    return h;
  }

  function pick(arr, seed) {
    return arr[seed % arr.length];
  }

  // 归一化输入：不区分大小写；返回 16 型大写码 / 彩蛋小写码 / null
  function normalize(type) {
    if (typeof type !== 'string') return null;
    var t = type.trim();
    if (!t) return null;
    var upper = t.toUpperCase();
    if (upper.length === 4 && TYPES[upper]) return upper;
    var lower = t.toLowerCase();
    if (EASTER_EGGS.indexOf(lower) !== -1) return lower;
    // 彩蛋码也可能是大写传入（如 SCHRODINGER），上面已覆盖；其余 4 字母但不在表内 → 非法
    return null;
  }

  function getCompat(typeA, typeB) {
    var a = normalize(typeA);
    var b = normalize(typeB);
    if (!a || !b) return null;
    // 彩蛋人格（任一）走兜底
    if (!TYPES[a] || !TYPES[b]) {
      return { score: EASTER_RESULT.score, title: EASTER_RESULT.title, verdict: EASTER_RESULT.verdict, dims: [] };
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
      dims.push({
        dim: d.key,
        label: d.label,
        relation: same ? d.same : d.diff,
        comment: pick(same ? COMMENTS[i].same : COMMENTS[i].diff, seed + i)
      });
    }

    // 合拍指数：基础 20 + 每同维 15；反维按互补 +8 / 互斥 +3 兜底加分
    var score = 20 + sameCount * 15 + diffBonus;
    var title;
    if (sameCount === 4) {
      score = 96;
      title = '世另我';
    } else if (sameCount === 0) {
      score += 6; // 欢喜冤家火花加成：全反也有春天
      title = '欢喜冤家';
    } else if (sameCount === 3) {
      title = pick(TITLE_POOLS[3], seed);
    } else if (sameCount === 2) {
      title = TYPES[a].name + '遇上' + TYPES[b].name;
    } else {
      title = pick(TITLE_POOLS[1], seed);
    }
    if (score > 100) score = 100;
    if (score < 0) score = 0;

    // verdict：开场（按分数档）+ 维度结论 + 收尾（按组合类型）
    var opening;
    if (score >= 85) opening = '你们俩像同一个神经中枢分叉出来的，';
    else if (score >= 65) opening = '这组合属于老天赏饭吃的搭配，';
    else if (score >= 45) opening = '你们的关系像一份需求文档，';
    else opening = '你们俩放一起，HR 看了连夜改组织架构，';

    var middle = '四个维度同频 ' + sameCount + ' 个';
    if (sameCount === 4) middle += '，同步率高到离谱';
    else if (sameCount === 0) middle += '，全靠对冲产生火花';
    else middle += '，剩下的全靠磨合与演技';

    var closing;
    if (sameCount === 4) closing = '建议原地结拜，工位拼一起，一起卷死全公司。';
    else if (sameCount === 0) closing = '建议保持安全距离，偶尔约饭，别一起做项目。';
    else if (score >= 65) closing = '建议锁死这对 CP，组队摸鱼效率翻倍。';
    else if (score >= 45) closing = '能处，但别指望心有灵犀，多说话少猜。';
    else closing = '合盘分数偏低，建议把锅甩给星座。';

    return { score: score, title: title, verdict: opening + middle + '。' + closing, dims: dims };
  }

  window.NBTICompat = { TYPES: TYPES, EASTER_EGGS: EASTER_EGGS, getCompat: getCompat };
})();
