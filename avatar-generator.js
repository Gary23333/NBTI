(function () {
  const rand = (min, max) => Math.random() * (max - min) + min;
  const randInt = (min, max) => Math.floor(rand(min, max + 1));
  const pick = arr => arr[Math.floor(Math.random() * arr.length)];
  const esc = value => String(value).replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
  const pts = points => points.map(p => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ');

  const DEFAULT_THEMES = {
    NBTI: { primary: '#DC2626', secondary: '#991B1B', bg: '#FEE2E2', name: '卷王', accessories: ['briefcase', 'chart', 'flame', 'coffee'] },
    NBTP: { primary: '#2563EB', secondary: '#1E40AF', bg: '#DBEAFE', name: '棋手', accessories: ['chess', 'brain', 'ruler', 'target'] },
    NBFI: { primary: '#374151', secondary: '#1F2937', bg: '#F3F4F6', name: '独狼', accessories: ['wolf', 'lightning', 'gamepad', 'guitar'] },
    NBFP: { primary: '#059669', secondary: '#047857', bg: '#D1FAE5', name: '浪子', accessories: ['wave', 'plane', 'backpack', 'globe'] },
    NHTI: { primary: '#D97706', secondary: '#B45309', bg: '#FEF3C7', name: '霸总', accessories: ['crown', 'coin', 'trophy', 'chart-up'] },
    NHTP: { primary: '#EA580C', secondary: '#C2410C', bg: '#FFF7ED', name: '教练', accessories: ['medal', 'megaphone', 'muscle', 'jersey'] },
    NHFI: { primary: '#92400E', secondary: '#78350F', bg: '#FEF3C7', name: '护犊子', accessories: ['shield', 'pan', 'heart', 'home'] },
    NHFP: { primary: '#EC4899', secondary: '#DB2777', bg: '#FCE7F3', name: '气氛组', accessories: ['confetti', 'balloon', 'music', 'sparkle'] },
    SBTI: { primary: '#CA8A04', secondary: '#A16207', bg: '#FEF9C3', name: '工蚁', accessories: ['wrench', 'clipboard', 'clock', 'hammer'] },
    SBTP: { primary: '#9CA3AF', secondary: '#6B7280', bg: '#F9FAFB', name: '人形计算器', accessories: ['calculator', 'chart', 'laptop', 'phone'] },
    SBFI: { primary: '#78350F', secondary: '#451A03', bg: '#FEF3C7', name: '螺丝钉', accessories: ['bolt', 'gear', 'toolbox', 'box'] },
    SBFP: { primary: '#7C3AED', secondary: '#6D28D9', bg: '#EDE9FE', name: '扫地僧', accessories: ['book', 'zen', 'bamboo', 'yin-yang'] },
    SHTI: { primary: '#1E40AF', secondary: '#1E3A8A', bg: '#DBEAFE', name: '大管家', accessories: ['notebook', 'folder', 'radio', 'check'] },
    SHTP: { primary: '#1F2937', secondary: '#111827', bg: '#F9FAFB', name: '质检警察', accessories: ['magnifier', 'check', 'document', 'scales'] },
    SHFI: { primary: '#EC4899', secondary: '#DB2777', bg: '#FCE7F3', name: '居委会大妈', accessories: ['speech', 'tea', 'flower', 'gift'] },
    SHFP: { primary: '#E5E7EB', secondary: '#D1D5DB', bg: '#F9FAFB', name: '职场空气', accessories: ['wind', 'cloud', 'quiet-face', 'leaf'] },
    schrodinger: { primary: '#6B7280', secondary: '#4B5563', bg: '#F3F4F6', name: '薛定谔的打工人', accessories: ['question', 'atom', 'box', 'mist'], effect: 'translucent' },
    hexagon: { primary: '#F59E0B', secondary: '#D97706', bg: '#FEF3C7', name: '六边形战士', accessories: ['star', 'flame', 'trophy', 'sword'], effect: 'golden' },
    buddha: { primary: '#F97316', secondary: '#EA580C', bg: '#FFF7ED', name: '职场活佛', accessories: ['zen', 'lotus', 'yin-yang', 'beads'], effect: 'buddha_light' },
    twoface: { primary: '#1F2937', secondary: '#F9FAFB', bg: '#D1D5DB', name: '职场双面人', accessories: ['mask', 'half-moon', 'moon', 'sunglasses'], effect: 'split' },
    meme_lord: { primary: '#8B5CF6', secondary: '#7C3AED', bg: '#EDE9FE', name: '互联网嘴替', accessories: ['microphone', 'speech', 'keyboard', 'phone'], effect: 'barrage' }
  };

  const LABEL_ACCESSORY = {
    金丝眼镜: 'glasses-gold', 圆框眼镜: 'glasses-round', 银框眼镜: 'glasses-silver', 老花镜: 'glasses-round', 墨镜: 'sunglasses', 护目镜: 'goggles',
    红领带: 'tie-red', 领带: 'tie', 蓝围巾: 'scarf', 黑口罩: 'mask-medical', 项链: 'beads', 金领结: 'bowtie', 哨子: 'whistle', 佛珠: 'beads', 工牌: 'badge', 红袖章: 'armband',
    西装: 'suit', 西装领: 'suit', 大衣: 'coat', 皮衣: 'jacket', 背心: 'jersey', 三件套西装: 'suit', 运动服: 'jersey', 围裙: 'apron', 花衬衫: 'hawaiian-shirt', 工装: 'workwear',
    白衬衫: 'shirt', 工装裤: 'workwear', 道袍: 'robe', 制服: 'uniform', 碎花衫: 'flower-shirt', 卫衣: 'hoodie', 袈裟: 'robe', 披风: 'cape', 分裂西装: 'split-suit',
    公文包: 'briefcase', 笔记本电脑: 'laptop', 棋盘: 'chess', 钢笔: 'pen', 帆布包: 'backpack', 金表: 'watch', 战术板: 'clipboard', 平底锅: 'pan', 汤勺: 'spoon',
    手机: 'phone', 扳手: 'wrench', 工具箱: 'toolbox', 计算器: 'calculator', 文件夹: 'folder', 螺丝刀: 'screwdriver', 钳子: 'pliers', 扫帚: 'broom', 对讲机: 'radio',
    钥匙串: 'keys', 放大镜: 'magnifier', 红笔: 'pen-red', 检查表: 'checklist', 蒲扇: 'fan', 保温杯: 'thermos', 问号牌: 'question', 盾牌: 'shield', 宝剑: 'sword',
    键盘: 'keyboard', 皇冠: 'crown', 光圈: 'halo', 莲花座: 'lotus', 半脸面具: 'mask', 耳机: 'headphones', 弹幕框: 'speech', 表情包: 'meme-card', 量子叠加符号: 'atom', 薛定谔方程: 'formula',
    棒球帽: 'cap', 运动头带: 'headband', 大金链: 'chain', 安全帽: 'helmet', 斗笠: 'straw-hat', 烫卷发: 'curl-hair', 爆炸头假发: 'afro-wig', '勋章×3': 'medal'
  };

  const naturalHairColors = ['rgb(0,0,0)', 'rgb(44,34,43)', 'rgb(80,68,68)', 'rgb(120,84,60)', 'rgb(167,133,106)', 'rgb(185,55,55)', 'rgb(128,128,128)'];
  const bgAccents = ['#F5F5DC', '#B0E0E6', '#D1D5DB', '#98FB98', '#FFFDD0', '#E6E6FA', '#BC8F8F', '#87CEEB', '#F5FFFA', '#F5DEB3'];

  function cubicBezier(p0, p1, p2, p3, t) {
    const mt = 1 - t;
    return [
      mt ** 3 * p0[0] + 3 * mt ** 2 * t * p1[0] + 3 * mt * t ** 2 * p2[0] + t ** 3 * p3[0],
      mt ** 3 * p0[1] + 3 * mt ** 2 * t * p1[1] + 3 * mt * t ** 2 * p2[1] + t ** 3 * p3[1]
    ];
  }

  function eggPoints(a, b, k, segments) {
    const result = [];
    const quadrant = (sx, sy, start, end, reverse) => {
      const from = reverse ? end : start;
      const to = reverse ? start : end;
      const step = reverse ? -1 : 1;
      for (let i = from; reverse ? i > to : i < to; i += step) {
        const degree = (Math.PI / 2 / segments) * i + rand(-Math.PI / 1.1 / segments, Math.PI / 1.1 / segments);
        const y = sy * Math.sin(degree) * b;
        const denom = Math.max(0.06, 1 + k * y);
        const x = sx * Math.sqrt(Math.max(0, ((1 - (y * y) / (b * b)) / denom) * a * a)) + rand(-a / 200, a / 200);
        result.push([x, y]);
      }
    };
    quadrant(1, 1, 0, segments, false);
    quadrant(-1, 1, 0, segments, true);
    quadrant(-1, -1, 0, segments, false);
    quadrant(1, -1, 0, segments, true);
    return result;
  }

  function rectIntersection(radian, a, b) {
    const r = Math.max(0, Math.min(Math.PI / 2, radian));
    if (Math.abs(r - Math.PI / 2) < 0.0001) return { x: 0, y: b };
    const m = Math.tan(r);
    return m * a < b ? { x: a, y: m * a } : { x: b / m, y: b };
  }

  function rectPoints(a, b, segments) {
    const result = [];
    const pushPoint = (sx, sy, i) => {
      const degree = (Math.PI / 2 / segments) * i + rand(-Math.PI / 11 / segments, Math.PI / 11 / segments);
      const p = rectIntersection(degree, a, b);
      result.push([sx * p.x, sy * p.y]);
    };
    for (let i = 0; i < segments; i++) pushPoint(1, 1, i);
    for (let i = segments; i > 0; i--) pushPoint(-1, 1, i);
    for (let i = 0; i < segments; i++) pushPoint(-1, -1, i);
    for (let i = segments; i > 0; i--) pushPoint(1, -1, i);
    return result;
  }

  function faceContour(numPoints = 74, scale = 0.56) {
    const x0 = rand(50, 100), y0 = rand(70, 100), y1 = rand(50, 80), x1 = rand(70, 100);
    const k0 = rand(0.001, 0.005) * (Math.random() > 0.5 ? 1 : -1);
    const k1 = rand(0.001, 0.005) * (Math.random() > 0.5 ? 1 : -1);
    const a = Math.random() > 0.1 ? eggPoints(x0, y0, k0, numPoints) : rectPoints(x0, y0, numPoints);
    const b = Math.random() > 0.3 ? eggPoints(x1, y1, k1, numPoints) : rectPoints(x1, y1, numPoints);
    const tx0 = rand(-5, 5), ty0 = rand(-15, 15), tx1 = rand(-5, 25), ty1 = rand(-5, 5);
    for (let i = 0; i < a.length; i++) {
      a[i][0] += tx0; a[i][1] += ty0; b[i][0] += tx1; b[i][1] += ty1;
    }
    const result = [];
    let cx = 0, cy = 0;
    for (let i = 0; i < a.length; i++) {
      const p = [
        a[i][0] * 0.7 + b[(i + a.length / 4) % a.length][1] * 0.3,
        a[i][1] * 0.7 - b[(i + a.length / 4) % a.length][0] * 0.3
      ];
      result.push(p); cx += p[0]; cy += p[1];
    }
    cx /= result.length; cy /= result.length;
    for (const p of result) { p[0] = (p[0] - cx) * scale; p[1] = (p[1] - cy) * scale - 6; }
    const width = Math.abs(result[0][0] - result[result.length / 2][0]);
    const height = Math.abs(result[result.length / 4][1] - result[(result.length * 3) / 4][1]);
    result.push(result[0], result[1]);
    return { points: result, width, height, center: [0, -6] };
  }

  function eyeParams(width) {
    const heightUpper = Math.random() * width / 1.2;
    const heightLower = Math.random() * width / 1.2;
    const trueWidth = width + rand(-width / 40, width / 40);
    const upperLeft = rand(-trueWidth / 10, trueWidth / 2.3);
    const upperRight = rand(-trueWidth / 10, trueWidth / 2.3);
    return {
      heightUpper, heightLower, p0x: rand(-0.2, 0.2), p3x: rand(-0.2, 0.2), p0y: rand(-0.2, 0.2), p3y: rand(-0.2, 0.2),
      upperLeft, upperRight, upperLeftY: Math.random() * heightUpper, upperRightY: Math.random() * heightUpper,
      lowerLeft: rand(upperLeft, trueWidth / 2.1), lowerRight: rand(upperRight, trueWidth / 2.1),
      lowerLeftY: rand(-Math.random() * heightUpper + 5, heightLower), lowerRightY: rand(-Math.random() * heightUpper + 5, heightLower),
      c0: Math.random(), c1: Math.random(), c2: Math.random(), c3: Math.random()
    };
  }

  function eyePoints(params, width) {
    const p0 = [-width / 2 + params.p0x * width / 16, params.p0y * params.heightUpper / 16];
    const p3 = [width / 2 + params.p3x * width / 16, params.p3y * params.heightUpper / 16];
    const p1u = [p0[0] + params.upperLeft, p0[1] + params.upperLeftY];
    const p2u = [p3[0] - params.upperRight, p3[1] + params.upperRightY];
    const p1l = [p0[0] + params.lowerLeft, p0[1] - params.lowerLeftY];
    const p2l = [p3[0] - params.lowerRight, p3[1] - params.lowerRightY];
    const upper = [], lower = [];
    const uc0 = [p0[0] * (1 - params.c0) + p1l[0] * params.c0, p0[1] * (1 - params.c0) + p1l[1] * params.c0];
    const uc1 = [p3[0] * (1 - params.c1) + p2l[0] * params.c1, p3[1] * (1 - params.c1) + p2l[1] * params.c1];
    const lc0 = [p0[0] * (1 - params.c2) + p1u[0] * params.c2, p0[1] * (1 - params.c2) + p1u[1] * params.c2];
    const lc1 = [p3[0] * (1 - params.c3) + p2u[0] * params.c3, p3[1] * (1 - params.c3) + p2u[1] * params.c3];
    const upperLeftCtrl = [], upperRightCtrl = [], lowerLeftCtrl = [], lowerRightCtrl = [];
    for (let i = 0; i < 100; i++) {
      const t = i / 100;
      upper.push(cubicBezier(p0, p1u, p2u, p3, t));
      lower.push(cubicBezier(p0, p1l, p2l, p3, t));
      upperLeftCtrl.push(cubicBezier(uc0, p0, p1u, p2u, t));
      upperRightCtrl.push(cubicBezier(p1u, p2u, p3, uc1, t));
      lowerLeftCtrl.push(cubicBezier(lc0, p0, p1l, p2l, t));
      lowerRightCtrl.push(cubicBezier(p1l, p2l, p3, lc1, t));
    }
    for (let i = 0; i < 75; i++) {
      const w = ((75 - i) / 75) ** 2;
      upper[i] = [upper[i][0] * (1 - w) + upperLeftCtrl[i + 25][0] * w, upper[i][1] * (1 - w) + upperLeftCtrl[i + 25][1] * w];
      upper[i + 25] = [upper[i + 25][0] * w + upperRightCtrl[i][0] * (1 - w), upper[i + 25][1] * w + upperRightCtrl[i][1] * (1 - w)];
      lower[i] = [lower[i][0] * (1 - w) + lowerLeftCtrl[i + 25][0] * w, lower[i][1] * (1 - w) + lowerLeftCtrl[i + 25][1] * w];
      lower[i + 25] = [lower[i + 25][0] * w + lowerRightCtrl[i][0] * (1 - w), lower[i + 25][1] * w + lowerRightCtrl[i][1] * (1 - w)];
    }
    const center = [(upper[50][0] + lower[50][0]) / 2, (-upper[50][1] - lower[50][1]) / 2];
    for (let i = 0; i < 100; i++) {
      upper[i] = [upper[i][0] - center[0], -upper[i][1] - center[1]];
      lower[i] = [lower[i][0] - center[0], -lower[i][1] - center[1]];
    }
    return { upper, lower, contour: upper.slice(10, 90).concat(lower.slice(10, 90).reverse()) };
  }

  function bothEyes(width) {
    const leftParams = eyeParams(width);
    const rightParams = { ...leftParams };
    Object.keys(rightParams).forEach(k => typeof rightParams[k] === 'number' && (rightParams[k] += rand(-Math.abs(rightParams[k]) / 2, Math.abs(rightParams[k]) / 2)));
    const left = eyePoints(leftParams, width);
    const right = eyePoints(rightParams, width);
    [left.upper, left.lower, left.contour].forEach(list => list.forEach(p => { p[0] = -p[0]; }));
    return { left, right };
  }

  function bezierCurve(controlPoints, count) {
    const n = controlPoints.length - 1;
    const choose = (nn, kk) => {
      let res = 1;
      for (let i = 1; i <= kk; i++) res = res * (nn - i + 1) / i;
      return res;
    };
    const curve = [];
    for (let i = 0; i <= count; i++) {
      const t = i / count;
      let x = 0, y = 0;
      for (let j = 0; j <= n; j++) {
        const w = choose(n, j) * (1 - t) ** (n - j) * t ** j;
        x += w * controlPoints[j].x; y += w * controlPoints[j].y;
      }
      curve.push([x, y]);
    }
    return curve;
  }

  function generateHair(face) {
    const base = face.slice(0, -2);
    const hairs = [];
    const method0 = count => {
      for (let i = 0; i < count; i++) {
        const len = randInt(15, 25);
        const a = randInt(30, 140), b = randInt(30, 140);
        const line0 = [], line1 = [];
        for (let j = 0; j < len; j++) {
          const p0 = base[(base.length - (j + a)) % base.length];
          const p1 = base[(base.length - (-j + b)) % base.length];
          line0.push({ x: p0[0], y: p0[1] }); line1.push({ x: p1[0], y: p1[1] });
        }
        const c0 = bezierCurve(line0, len), c1 = bezierCurve(line1, len);
        hairs.push(c0.map((p, j) => {
          const w = (j / len) ** 2;
          return [p[0] * w + c1[j][0] * (1 - w), p[1] * w + c1[j][1] * (1 - w)];
        }));
      }
    };
    const method3 = count => {
      const split = randInt(0, 200);
      const picked = Array.from({ length: count }, () => randInt(10, 180)).sort((a, b) => a - b);
      picked.forEach(index => {
        const len = randInt(22, 38), lower = Math.random() > 0.9 ? rand(0, 1) : rand(1, 1.55);
        const reverse = index > split ? 1 : -1;
        const line = [];
        for (let j = 0; j < len; j++) {
          const p = base[(base.length - (reverse * j * 2 + index)) % base.length];
          const portion = (1 - (j / len) ** rand(0.1, 3)) * (1 - lower) + lower;
          line.push({ x: p[0] * portion, y: p[1] });
        }
        hairs.push(bezierCurve(line, len));
      });
    };
    if (Math.random() > 0.18) method0(randInt(18, 48));
    if (Math.random() > 0.28) method3(randInt(18, 82));
    return hairs;
  }

  function mouthShape(faceHeight, faceWidth) {
    const choice = randInt(0, 2);
    if (choice === 2) {
      const center = [rand(-faceWidth / 8, faceWidth / 8), rand(faceHeight / 4, faceHeight / 2.5) - 6];
      const mouth = eggPoints(rand(faceWidth / 10, faceWidth / 4), rand(faceHeight / 20, faceHeight / 10), 0.001, 50);
      const r = rand(-Math.PI / 9.5, Math.PI / 9.5);
      return mouth.map(p => [p[0] * Math.cos(r) - p[1] * Math.sin(r) + center[0], p[0] * Math.sin(r) + p[1] * Math.cos(r) + center[1]]);
    }
    const ry = rand(faceHeight / 7, choice ? faceHeight / 4 : faceHeight / 3.5) - 6;
    const ly = rand(faceHeight / 7, choice ? faceHeight / 4 : faceHeight / 3.5) - 6;
    const rx = rand(faceWidth / 10, faceWidth / 2);
    const lx = -rx + rand(-faceWidth / 20, faceWidth / 20);
    const cp0 = [rand(0, rx), rand(ly + 5, faceHeight / 1.5) - 6];
    const cp1 = [rand(lx, 0), rand(ly + 5, faceHeight / 1.5) - 6];
    const mouth = [];
    for (let i = 0; i < 1; i += 0.01) mouth.push(cubicBezier([lx, ly], cp1, cp0, [rx, ry], i));
    for (let i = 0; i < 1; i += 0.01) mouth.push(cubicBezier([rx, ry], cp0, cp1, [lx, ly], i));
    if (!choice) return mouth;
    const center = [(rx + lx) / 2, (mouth[25][1] + mouth[75][1]) / 2];
    return mouth.map(p => [(p[0] - center[0]) * 0.6 + center[0], -(p[1] - center[1]) * 0.6 + center[1] * 0.8]);
  }

  const EMOJI_ACCESSORY = {
    '💼': 'briefcase', '📊': 'chart', '🔥': 'flame', '☕': 'coffee',
    '♟️': 'chess', '🧠': 'brain', '📐': 'ruler', '🎯': 'target',
    '🐺': 'wolf', '⚡': 'lightning', '🎮': 'gamepad', '🎸': 'guitar',
    '🌊': 'wave', '✈️': 'plane', '🎒': 'backpack', '🌍': 'globe',
    '👑': 'crown', '💰': 'coin', '🏆': 'trophy', '📈': 'chart-up',
    '🏅': 'medal', '📣': 'megaphone', '💪': 'muscle', '🎽': 'jersey',
    '🛡️': 'shield', '🍳': 'pan', '❤️': 'heart', '🏠': 'home',
    '🎉': 'confetti', '🎈': 'balloon', '🎵': 'music', '✨': 'sparkle',
    '🔧': 'wrench', '📋': 'clipboard', '⏰': 'clock', '🔨': 'hammer',
    '🔢': 'calculator', '💻': 'laptop', '📱': 'phone',
    '🔩': 'bolt', '⚙️': 'gear', '🛠️': 'toolbox', '📦': 'box',
    '📚': 'book', '🧘': 'zen', '🎋': 'bamboo', '☯️': 'yin-yang',
    '📒': 'notebook', '🗂️': 'folder', '📞': 'radio', '✅': 'check',
    '🔍': 'magnifier', '📝': 'document', '⚖️': 'scales',
    '🗣️': 'speech', '🍵': 'tea', '🌻': 'flower', '💝': 'gift',
    '💨': 'wind', '☁️': 'cloud', '😶': 'quiet-face', '🍃': 'leaf',
    '❓': 'question', '🧪': 'beaker', '🌫️': 'mist', '⭐': 'star',
    '⚔️': 'sword', '🪷': 'lotus', '🎭': 'mask', '◐': 'half-moon',
    '🌓': 'moon', '🕶️': 'sunglasses', '🎤': 'microphone',
    '💬': 'speech', '⌨️': 'keyboard'
  };

  function iconPalette(theme) {
    return {
      a: theme.primary || '#475569',
      b: theme.secondary || theme.primary || '#1f2937',
      c: '#fff7ed',
      d: '#111827',
      e: '#f8fafc',
      gold: '#fbbf24',
      red: '#ef4444',
      blue: '#38bdf8',
      green: '#22c55e',
      shadow: 'rgba(15,23,42,.22)'
    };
  }

  function accessoryPath(type, p) {
    const fill = p.a;
    const dark = p.b;
    const line = p.d;
    const light = p.e;
    switch (type) {
      case 'briefcase':
        return `<rect x="-10" y="-3" width="20" height="14" rx="2.5" fill="${fill}" stroke="${line}" stroke-width="1.3"/><path d="M-4 -3v-3h8v3" fill="none" stroke="${line}" stroke-width="1.4"/><path d="M-10 2h20" stroke="${dark}" stroke-width="1.2"/><rect x="-2" y="1" width="4" height="3" rx=".8" fill="${p.gold}" stroke="${line}" stroke-width=".6"/>`;
      case 'chart':
      case 'chart-up':
        return `<rect x="-11" y="-10" width="22" height="20" rx="3" fill="${light}" stroke="${line}" stroke-width="1.2"/><rect x="-7" y="1" width="3" height="6" rx="1" fill="${fill}"/><rect x="-1.5" y="-4" width="3" height="11" rx="1" fill="${p.blue}"/><rect x="4" y="-8" width="3" height="15" rx="1" fill="${p.red}"/><path d="M-7 5l5-7 5 3 5-8" fill="none" stroke="${dark}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>`;
      case 'flame':
        return `<path d="M1 11C-7 8-9 1-4-5c1 4 3 4 4-2 3 3 8 8 5 14 3-1 5-4 5-7 4 7 0 13-9 11z" fill="${p.red}" stroke="${line}" stroke-width="1.1" stroke-linejoin="round"/><path d="M1 8c-3-2-3-5 0-8 1 3 4 4 2 8 2-1 3-3 3-5 2 4 0 7-5 5z" fill="${p.gold}" opacity=".95"/>`;
      case 'coffee':
      case 'tea':
      case 'thermos':
        return `<path d="M-8 -1h14v8a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6z" fill="${light}" stroke="${line}" stroke-width="1.2"/><path d="M6 1h4a3 3 0 0 1 0 6H6" fill="none" stroke="${line}" stroke-width="1.2"/><path d="M-5 -5c2-2-1-3 1-5M0-5c2-2-1-3 1-5M5-5c2-2-1-3 1-5" stroke="${dark}" stroke-width="1" stroke-linecap="round" opacity=".7"/><ellipse cx="-1" cy="-1" rx="7" ry="2" fill="${fill}" opacity=".25"/>`;
      case 'chess':
        return `<circle cx="0" cy="-8" r="3" fill="${dark}"/><path d="M-4 -5h8l-1 11h-6z" fill="${dark}"/><path d="M-8 9h16v4h-16z" fill="${dark}"/><path d="M-6 6h12" stroke="${light}" stroke-width="1" opacity=".5"/>`;
      case 'brain':
        return `<path d="M-8 1c-5-4-1-11 4-8 2-5 8-2 8 2 5-1 8 5 4 9 2 5-5 9-9 5-4 4-11-2-7-8z" fill="#f9a8d4" stroke="${line}" stroke-width="1.1"/><path d="M-5-3c4 0 3 4 0 5M0-7c-2 4 2 5 0 9M5-3c-4 1-3 5 0 6" fill="none" stroke="#be185d" stroke-width="1" stroke-linecap="round"/>`;
      case 'ruler':
        return `<path d="M-10 7L7-10l5 5L-5 12z" fill="${p.gold}" stroke="${line}" stroke-width="1.1"/><path d="M-5 2l3 3M-1-2l2 2M3-6l3 3" stroke="${line}" stroke-width=".9"/>`;
      case 'target':
        return `<circle cx="0" cy="0" r="11" fill="${light}" stroke="${line}" stroke-width="1.2"/><circle cx="0" cy="0" r="7" fill="none" stroke="${p.red}" stroke-width="2"/><circle cx="0" cy="0" r="2.6" fill="${p.red}"/><path d="M0-13v5M0 8v5M-13 0h5M8 0h5" stroke="${line}" stroke-width="1"/>`;
      case 'wolf':
        return `<path d="M-10 7l3-15 6 5 6-5 5 15-7 6-6-3-6 3z" fill="${dark}" stroke="${line}" stroke-width="1.1"/><path d="M-4 2l4 7 4-7" fill="${light}" opacity=".75"/><circle cx="-4" cy="0" r="1.2" fill="${p.gold}"/><circle cx="4" cy="0" r="1.2" fill="${p.gold}"/>`;
      case 'lightning':
        return `<path d="M2-12L-8 2h6l-3 11L8-3H1z" fill="${p.gold}" stroke="${line}" stroke-width="1.1" stroke-linejoin="round"/>`;
      case 'gamepad':
        return `<path d="M-11 3c0-5 2-8 6-6h10c4-2 6 1 6 6 0 5-3 8-6 5l-3-3h-4l-3 3c-3 3-6 0-6-5z" fill="${light}" stroke="${line}" stroke-width="1.2"/><path d="M-7 2h5M-4-1v6" stroke="${dark}" stroke-width="1.3"/><circle cx="5" cy="1" r="1.4" fill="${p.red}"/><circle cx="8" cy="4" r="1.4" fill="${p.blue}"/>`;
      case 'guitar':
        return `<path d="M-7 6c-4-4 0-10 4-7l2 2 8-9 3 3-9 8 2 2c3 4-4 8-7 4z" fill="#b45309" stroke="${line}" stroke-width="1.1"/><circle cx="-4" cy="4" r="2" fill="${dark}"/><path d="M0 1l8-8M2 3l8-8" stroke="${light}" stroke-width=".7"/>`;
      case 'wave':
        return `<path d="M-12 4c5-8 10-8 15-1 3 4 6 3 9 0-2 8-8 11-15 7-4-2-6-2-9 1 1-3 1-5 0-7z" fill="${p.blue}" stroke="${line}" stroke-width="1"/><path d="M-8 4c5-2 8 3 13 2" fill="none" stroke="${light}" stroke-width="1.3" stroke-linecap="round"/>`;
      case 'plane':
        return `<path d="M-12 2L12-9 4 13 0 4z" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M0 4l12-13-16 10" fill="none" stroke="${p.blue}" stroke-width="1.1"/>`;
      case 'backpack':
        return `<rect x="-8" y="-7" width="16" height="19" rx="5" fill="${fill}" stroke="${line}" stroke-width="1.2"/><path d="M-4-7c0-4 8-4 8 0M-8-1h16M-4 4h8" fill="none" stroke="${light}" stroke-width="1.1"/><path d="M-8-3c-5 2-5 9 0 11M8-3c5 2 5 9 0 11" fill="none" stroke="${line}" stroke-width="1"/>`;
      case 'globe':
        return `<circle cx="0" cy="0" r="11" fill="${p.blue}" stroke="${line}" stroke-width="1.2"/><path d="M-9 0h18M0-10c4 4 4 16 0 20M0-10c-4 4-4 16 0 20" fill="none" stroke="${light}" stroke-width="1"/><path d="M-5-5c3-2 6-1 9 1M-4 6c3 1 7 1 10-1" fill="none" stroke="${light}" stroke-width=".9"/>`;
      case 'crown':
        return `<path d="M-11 7l2-13 6 7 5-9 5 9 6-7 2 13z" fill="${p.gold}" stroke="${line}" stroke-width="1.1" stroke-linejoin="round"/><rect x="-10" y="7" width="20" height="4" rx="1" fill="${p.gold}" stroke="${line}" stroke-width="1"/>`;
      case 'coin':
        return `<circle cx="0" cy="0" r="10" fill="${p.gold}" stroke="${line}" stroke-width="1.2"/><ellipse cx="0" cy="0" rx="5" ry="9" fill="none" stroke="${line}" stroke-width="1"/><path d="M-4 0h8" stroke="${line}" stroke-width="1.2"/><circle cx="4" cy="-5" r="2" fill="${light}" opacity=".45"/>`;
      case 'trophy':
        return `<path d="M-7-8h14v6c0 6-3 9-7 9s-7-3-7-9z" fill="${p.gold}" stroke="${line}" stroke-width="1.1"/><path d="M-7-5h-5c0 5 2 7 6 7M7-5h5c0 5-2 7-6 7M0 7v4M-5 12h10" fill="none" stroke="${line}" stroke-width="1.2"/>`;
      case 'medal':
        return `<path d="M-5-12l5 8 5-8" fill="none" stroke="${p.red}" stroke-width="3"/><circle cx="0" cy="3" r="8" fill="${p.gold}" stroke="${line}" stroke-width="1.1"/><path d="M0-1l1.5 3.2L5 2.6 2.4 5 3 8.5 0 6.8-3 8.5-2.4 5-5 2.6-1.5 2.2z" fill="${light}"/>`;
      case 'megaphone':
        return `<path d="M-11 0l14-7v14l-14-4z" fill="${light}" stroke="${line}" stroke-width="1.2"/><path d="M-11 0h-3v4h3M-5 5l2 7" stroke="${line}" stroke-width="1.2"/><path d="M6-5c3 3 3 7 0 10" fill="none" stroke="${fill}" stroke-width="1.5"/>`;
      case 'muscle':
        return `<path d="M-10 6c3-7 6-10 11-10 0-3 3-6 6-4-2 3-1 5 3 7 4 3 2 10-3 11H-7c-3 0-5-1-3-4z" fill="#f8c7a6" stroke="${line}" stroke-width="1.1"/><path d="M-1-3c-1 5 4 7 9 5" fill="none" stroke="#b45309" stroke-width="1"/>`;
      case 'jersey':
      case 'shirt':
      case 'workwear':
      case 'hoodie':
      case 'uniform':
      case 'jacket':
      case 'coat':
      case 'suit':
      case 'apron':
      case 'robe':
      case 'cape':
      case 'flower-shirt':
      case 'hawaiian-shirt':
      case 'split-suit':
        return `<path d="M-9-7l5-4h8l5 4 4 6-5 3v10H-8V2l-5-3z" fill="${type === 'split-suit' ? '#111827' : fill}" stroke="${line}" stroke-width="1.1" stroke-linejoin="round"/><path d="M0-11v23" stroke="${type === 'split-suit' ? light : dark}" stroke-width="1"/><path d="M-3-10l3 5 3-5" fill="${light}" stroke="${line}" stroke-width=".8"/><circle cx="4" cy="-1" r="1" fill="${p.gold}"/><circle cx="4" cy="4" r="1" fill="${p.gold}"/>`;
      case 'shield':
        return `<path d="M0-12l10 4v7c0 7-4 11-10 14C-6 10-10 6-10-1v-7z" fill="${fill}" stroke="${line}" stroke-width="1.2"/><path d="M0-8v17M-5-2h10" stroke="${light}" stroke-width="1.2"/>`;
      case 'pan':
        return `<ellipse cx="-3" cy="2" rx="8" ry="6" fill="#374151" stroke="${line}" stroke-width="1.1"/><path d="M4-1l10-8" stroke="${line}" stroke-width="3" stroke-linecap="round"/><circle cx="-5" cy="0" r="2" fill="${p.gold}"/>`;
      case 'heart':
        return `<path d="M0 10C-10 3-13-3-8-8c3-3 7-1 8 3 1-4 5-6 8-3 5 5 2 11-8 18z" fill="${p.red}" stroke="${line}" stroke-width="1.1"/>`;
      case 'home':
        return `<path d="M-12 0L0-11 12 0" fill="none" stroke="${line}" stroke-width="1.6" stroke-linecap="round"/><rect x="-8" y="0" width="16" height="12" rx="1.5" fill="${light}" stroke="${line}" stroke-width="1.1"/><rect x="-2" y="5" width="4" height="7" fill="${fill}"/>`;
      case 'confetti':
        return `<path d="M-10 11l4-20 15 15z" fill="${p.gold}" stroke="${line}" stroke-width="1.1"/><circle cx="-3" cy="-7" r="1.5" fill="${p.red}"/><rect x="6" y="-9" width="4" height="4" rx="1" fill="${p.blue}" transform="rotate(25 8 -7)"/><path d="M4-2c4-6 8-6 10-2" fill="none" stroke="${p.green}" stroke-width="1.3" stroke-linecap="round"/>`;
      case 'balloon':
        return `<ellipse cx="0" cy="-3" rx="8" ry="10" fill="${p.red}" stroke="${line}" stroke-width="1.1"/><path d="M0 7l-2 4h4zM0 11c-6 2 4 4-2 7" fill="none" stroke="${line}" stroke-width="1"/><ellipse cx="-3" cy="-7" rx="2" ry="3" fill="${light}" opacity=".45"/>`;
      case 'music':
        return `<path d="M-5 5V-9l13-3v14" fill="none" stroke="${line}" stroke-width="2" stroke-linecap="round"/><ellipse cx="-8" cy="7" rx="4" ry="3" fill="${fill}" stroke="${line}" stroke-width="1"/><ellipse cx="5" cy="4" rx="4" ry="3" fill="${fill}" stroke="${line}" stroke-width="1"/>`;
      case 'sparkle':
      case 'star':
        return `<path d="M0-12l3.5 7.5L12-3 5.8 2.7 7.5 11 0 6.7-7.5 11l1.7-8.3L-12-3l8.5-1.5z" fill="${p.gold}" stroke="${line}" stroke-width="1.1" stroke-linejoin="round"/>`;
      case 'wrench':
      case 'screwdriver':
      case 'pliers':
      case 'hammer':
        return type === 'hammer'
          ? `<rect x="-2" y="-6" width="4" height="18" rx="1" fill="#92400e" stroke="${line}" stroke-width="1"/><path d="M-10-9H6l5 4-2 4H-10z" fill="${dark}" stroke="${line}" stroke-width="1.1"/>`
          : `<path d="M7-10a6 6 0 0 0-7 7L-11 8l5 5L5 2a6 6 0 0 0 7-7l-4 4-5-5z" fill="${dark}" stroke="${line}" stroke-width="1.1"/><circle cx="-7" cy="9" r="1.3" fill="${light}"/>`;
      case 'clipboard':
      case 'checklist':
        return `<rect x="-9" y="-9" width="18" height="22" rx="3" fill="${light}" stroke="${line}" stroke-width="1.1"/><rect x="-4" y="-12" width="8" height="5" rx="2" fill="${fill}" stroke="${line}" stroke-width="1"/><path d="M-5-2h9M-5 3h9M-5 8h6" stroke="${dark}" stroke-width="1"/><path d="M-7-2l1 1 2-3" fill="none" stroke="${p.green}" stroke-width="1.2"/>`;
      case 'clock':
      case 'watch':
        return `<circle cx="0" cy="0" r="10" fill="${light}" stroke="${line}" stroke-width="1.3"/><path d="M0-6v7l5 3" stroke="${dark}" stroke-width="1.4" stroke-linecap="round"/><path d="M-6-11l-3-3M6-11l3-3" stroke="${line}" stroke-width="1.2"/>`;
      case 'calculator':
        return `<rect x="-8" y="-12" width="16" height="24" rx="3" fill="${dark}" stroke="${line}" stroke-width="1.1"/><rect x="-5" y="-9" width="10" height="5" rx="1" fill="${p.green}"/><g fill="${light}"><circle cx="-4" cy="0" r="1.5"/><circle cx="0" cy="0" r="1.5"/><circle cx="4" cy="0" r="1.5"/><circle cx="-4" cy="5" r="1.5"/><circle cx="0" cy="5" r="1.5"/><circle cx="4" cy="5" r="1.5"/></g>`;
      case 'laptop':
      case 'keyboard':
        return type === 'keyboard'
          ? `<rect x="-12" y="-7" width="24" height="14" rx="2" fill="${dark}" stroke="${line}" stroke-width="1"/><g fill="${light}" opacity=".85"><rect x="-9" y="-4" width="3" height="2"/><rect x="-4" y="-4" width="3" height="2"/><rect x="1" y="-4" width="3" height="2"/><rect x="6" y="-4" width="3" height="2"/><rect x="-7" y="1" width="14" height="2"/></g>`
          : `<rect x="-10" y="-10" width="20" height="14" rx="2" fill="${dark}" stroke="${line}" stroke-width="1"/><rect x="-13" y="5" width="26" height="5" rx="2" fill="${light}" stroke="${line}" stroke-width="1"/><rect x="-7" y="-7" width="14" height="8" fill="${p.blue}" opacity=".65"/>`;
      case 'phone':
        return `<rect x="-6" y="-12" width="12" height="24" rx="3" fill="${dark}" stroke="${line}" stroke-width="1.1"/><rect x="-4" y="-8" width="8" height="15" fill="${p.blue}" opacity=".7"/><circle cx="0" cy="9" r="1" fill="${light}"/>`;
      case 'bolt':
        return `<path d="M-8-10H4L1-2h8L-5 12l3-9h-7z" fill="${dark}" stroke="${line}" stroke-width="1.1" stroke-linejoin="round"/><circle cx="0" cy="0" r="2" fill="${p.gold}"/>`;
      case 'gear':
        return `<path d="M0-12l2 3 4-1 2 4-2 3 3 3-3 3 2 3-2 4-4-1-2 3-2-3-4 1-2-4 2-3-3-3 3-3-2-3 2-4 4 1z" fill="${dark}" stroke="${line}" stroke-width="1"/><circle cx="0" cy="0" r="4" fill="${light}" stroke="${line}" stroke-width="1"/>`;
      case 'toolbox':
      case 'box':
        return `<rect x="-11" y="-5" width="22" height="15" rx="2" fill="${type === 'box' ? '#c08457' : fill}" stroke="${line}" stroke-width="1.1"/><path d="M-5-5v-4h10v4M-11 0h22M0-5v15" fill="none" stroke="${line}" stroke-width="1"/><rect x="-2" y="1" width="4" height="3" fill="${p.gold}"/>`;
      case 'book':
      case 'notebook':
        return `<path d="M-10-10h9c2 0 3 1 3 3v18c0-2-1-3-3-3h-9z" fill="${fill}" stroke="${line}" stroke-width="1.1"/><path d="M2-10h8v18H2c-2 0-3 1-3 3V-7c0-2 1-3 3-3z" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M4-5h4M4 0h4" stroke="${dark}" stroke-width=".8"/>`;
      case 'zen':
        return `<circle cx="0" cy="0" r="11" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M0-10c6 4 6 16 0 20-6-4-6-16 0-20z" fill="${dark}"/><circle cx="0" cy="-5" r="2" fill="${light}"/><circle cx="0" cy="5" r="2" fill="${dark}"/>`;
      case 'bamboo':
        return `<path d="M-4 12l5-24M4 11l4-20" stroke="${p.green}" stroke-width="3" stroke-linecap="round"/><path d="M-6-3l-6-4M-1 2l-6 3M5-4l7-5M6 3l7 2" stroke="${p.green}" stroke-width="1.5" stroke-linecap="round"/>`;
      case 'yin-yang':
        return `<circle cx="0" cy="0" r="11" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M0-11a5.5 5.5 0 0 1 0 11 5.5 5.5 0 0 0 0 11 11 11 0 0 0 0-22z" fill="${dark}"/><circle cx="0" cy="-5.5" r="1.7" fill="${dark}"/><circle cx="0" cy="5.5" r="1.7" fill="${light}"/>`;
      case 'folder':
        return `<path d="M-12-7h9l3 3h12v15h-24z" fill="${p.gold}" stroke="${line}" stroke-width="1.1"/><path d="M-12-3h24" stroke="${line}" stroke-width="1"/>`;
      case 'radio':
        return `<rect x="-10" y="-7" width="20" height="17" rx="3" fill="${dark}" stroke="${line}" stroke-width="1.1"/><path d="M-4-7l8-7" stroke="${line}" stroke-width="1.2"/><circle cx="-4" cy="2" r="4" fill="${light}"/><path d="M4-1h4M4 3h4" stroke="${light}" stroke-width="1"/>`;
      case 'check':
        return `<circle cx="0" cy="0" r="11" fill="${p.green}" stroke="${line}" stroke-width="1.1"/><path d="M-6 0l4 5 8-10" fill="none" stroke="${light}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>`;
      case 'magnifier':
        return `<circle cx="-2" cy="-2" r="7" fill="${light}" stroke="${line}" stroke-width="1.4"/><path d="M4 4l7 7" stroke="${line}" stroke-width="3" stroke-linecap="round"/><path d="M-5-4c2-2 5-2 7 0" stroke="${p.blue}" stroke-width="1" opacity=".7"/>`;
      case 'document':
        return `<path d="M-8-11h11l5 5v18H-8z" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M3-11v5h5M-5-3h9M-5 2h10M-5 7h7" stroke="${dark}" stroke-width="1"/>`;
      case 'scales':
        return `<path d="M0-11v22M-8-6h16M-5 11h10" stroke="${line}" stroke-width="1.4"/><path d="M-8-6l-5 8h10zM8-6L3 2h10z" fill="${light}" stroke="${line}" stroke-width="1"/>`;
      case 'speech':
        return `<path d="M-11-7h22v13H1l-6 6 1-6h-7z" fill="${light}" stroke="${line}" stroke-width="1.1"/><circle cx="-5" cy="0" r="1.3" fill="${fill}"/><circle cx="0" cy="0" r="1.3" fill="${fill}"/><circle cx="5" cy="0" r="1.3" fill="${fill}"/>`;
      case 'flower':
        return `<circle cx="0" cy="0" r="3" fill="${p.gold}" stroke="${line}" stroke-width=".8"/><g fill="${p.red}" stroke="${line}" stroke-width=".7"><ellipse cx="0" cy="-7" rx="3" ry="5"/><ellipse cx="0" cy="7" rx="3" ry="5"/><ellipse cx="-7" cy="0" rx="5" ry="3"/><ellipse cx="7" cy="0" rx="5" ry="3"/></g><path d="M0 3v9" stroke="${p.green}" stroke-width="1.3"/>`;
      case 'gift':
        return `<rect x="-10" y="-2" width="20" height="14" rx="2" fill="${p.red}" stroke="${line}" stroke-width="1.1"/><rect x="-12" y="-7" width="24" height="6" rx="1.5" fill="${p.gold}" stroke="${line}" stroke-width="1"/><path d="M0-7v19" stroke="${light}" stroke-width="1.3"/><path d="M0-7c-8-8-10 1 0 0 8-8 10 1 0 0z" fill="none" stroke="${line}" stroke-width="1"/>`;
      case 'wind':
        return `<path d="M-12-4H5c5 0 5-6 0-6-2 0-4 1-5 3M-11 3H9c4 0 4 6-1 6-2 0-4-1-5-3M-8-1h16" fill="none" stroke="${fill}" stroke-width="2" stroke-linecap="round"/>`;
      case 'cloud':
      case 'mist':
        return `<path d="M-10 5c-3-5 2-9 6-6 2-7 12-5 12 2 5 0 6 8 0 9h-15c-2 0-3-1-3-5z" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M-7 13h14" stroke="${fill}" stroke-width="1.3" stroke-linecap="round" opacity=".65"/>`;
      case 'quiet-face':
        return `<circle cx="0" cy="0" r="10" fill="${light}" stroke="${line}" stroke-width="1.1"/><circle cx="-4" cy="-2" r="1.2" fill="${dark}"/><circle cx="4" cy="-2" r="1.2" fill="${dark}"/><path d="M-4 4h8" stroke="${dark}" stroke-width="1.2" stroke-linecap="round"/>`;
      case 'leaf':
        return `<path d="M-10 8C-5-8 5-12 12-10 10-1 4 9-10 8z" fill="${p.green}" stroke="${line}" stroke-width="1.1"/><path d="M-9 7C-2 3 3-2 10-9" stroke="${light}" stroke-width="1.1"/>`;
      case 'question':
        return `<circle cx="0" cy="0" r="11" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M-4-5c1-5 10-4 9 2-.5 4-5 4-5 8" fill="none" stroke="${fill}" stroke-width="2.2" stroke-linecap="round"/><circle cx="0" cy="9" r="1.5" fill="${fill}"/>`;
      case 'atom':
        return `<circle cx="0" cy="0" r="2.3" fill="${fill}"/><ellipse cx="0" cy="0" rx="11" ry="4" fill="none" stroke="${line}" stroke-width="1"/><ellipse cx="0" cy="0" rx="11" ry="4" fill="none" stroke="${line}" stroke-width="1" transform="rotate(60)"/><ellipse cx="0" cy="0" rx="11" ry="4" fill="none" stroke="${line}" stroke-width="1" transform="rotate(-60)"/>`;
      case 'sword':
        return `<path d="M-2 5L8-12l4-2-2 4L-5 8z" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M-8 10l6-6M-7 2l7 7" stroke="${p.gold}" stroke-width="2" stroke-linecap="round"/>`;
      case 'lotus':
        return `<path d="M0-10c5 6 5 12 0 18-5-6-5-12 0-18z" fill="#f9a8d4" stroke="${line}" stroke-width=".9"/><path d="M-3 8c-7-2-9-7-6-12 6 2 8 7 6 12zM3 8c7-2 9-7 6-12-6 2-8 7-6 12z" fill="#f472b6" stroke="${line}" stroke-width=".9"/><path d="M-10 10h20" stroke="${p.green}" stroke-width="1.2" stroke-linecap="round"/>`;
      case 'mask':
        return `<path d="M-11-5c6-5 16-5 22 0-1 9-6 14-11 14S-10 4-11-5z" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M0-9v18" stroke="${dark}" stroke-width="1"/><path d="M-7-1c3-2 5-2 7 0M7-1c-3-2-5-2-7 0" fill="none" stroke="${line}" stroke-width="1"/><path d="M-4 5c3 2 5 2 8 0" fill="none" stroke="${p.red}" stroke-width="1"/>`;
      case 'half-moon':
      case 'moon':
        return `<circle cx="0" cy="0" r="11" fill="${p.gold}" stroke="${line}" stroke-width="1.1"/><circle cx="4" cy="-2" r="11" fill="${light}"/>`;
      case 'sunglasses':
      case 'glasses-gold':
      case 'glasses-round':
      case 'glasses-silver':
      case 'goggles':
        return `<circle cx="-5" cy="0" r="5" fill="${type === 'sunglasses' ? dark : 'none'}" stroke="${type === 'glasses-gold' ? p.gold : line}" stroke-width="1.4"/><circle cx="5" cy="0" r="5" fill="${type === 'sunglasses' ? dark : 'none'}" stroke="${type === 'glasses-gold' ? p.gold : line}" stroke-width="1.4"/><path d="M0 0h0M-10-1l-3-2M10-1l3-2" stroke="${line}" stroke-width="1.1"/>`;
      case 'microphone':
        return `<rect x="-5" y="-12" width="10" height="15" rx="5" fill="${dark}" stroke="${line}" stroke-width="1.1"/><path d="M-9-2c0 6 18 6 18 0M0 4v7M-5 12h10" fill="none" stroke="${line}" stroke-width="1.3"/><path d="M-2-8h4M-2-4h4" stroke="${light}" stroke-width=".8"/>`;
      case 'tie':
      case 'tie-red':
      case 'bowtie':
      case 'scarf':
      case 'chain':
      case 'beads':
        return type === 'bowtie'
          ? `<path d="M0 0l-10-6v12zM0 0l10-6v12z" fill="${p.gold}" stroke="${line}" stroke-width="1"/><circle cx="0" cy="0" r="2.5" fill="${fill}" stroke="${line}" stroke-width=".8"/>`
          : `<path d="M-3-10h6l3 4-3 18h-6l-3-18z" fill="${type === 'tie-red' ? p.red : fill}" stroke="${line}" stroke-width="1.1"/><path d="M-3-10l3 4 3-4" fill="${light}" stroke="${line}" stroke-width=".8"/>`;
      case 'cap':
      case 'helmet':
      case 'straw-hat':
      case 'headband':
      case 'halo':
      case 'curl-hair':
      case 'afro-wig':
        if (type === 'halo') return `<ellipse cx="0" cy="0" rx="12" ry="5" fill="none" stroke="${p.gold}" stroke-width="2.2"/><ellipse cx="0" cy="0" rx="7" ry="2.5" fill="none" stroke="${light}" stroke-width="1"/>`;
        if (type === 'helmet') return `<path d="M-11 2a11 11 0 0 1 22 0v4h-22z" fill="${p.gold}" stroke="${line}" stroke-width="1.1"/><path d="M0-9v11M-12 5h24" stroke="${line}" stroke-width="1"/>`;
        if (type === 'straw-hat') return `<ellipse cx="0" cy="4" rx="14" ry="4" fill="${p.gold}" stroke="${line}" stroke-width="1"/><path d="M-7 4c1-9 13-9 14 0z" fill="${p.gold}" stroke="${line}" stroke-width="1"/>`;
        return `<path d="M-10 1c2-9 18-9 20 0v4h-20z" fill="${fill}" stroke="${line}" stroke-width="1.1"/><path d="M4 4h10c-2 4-8 4-12 1" fill="${fill}" stroke="${line}" stroke-width="1"/>`;
      case 'badge':
      case 'armband':
      case 'formula':
      case 'meme-card':
      case 'beaker':
      default:
        return `<rect x="-10" y="-10" width="20" height="20" rx="4" fill="${light}" stroke="${line}" stroke-width="1.1"/><path d="M-5 4l4 4 7-12" fill="none" stroke="${fill}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="6" cy="-6" r="2" fill="${p.gold}"/>`;
    }
  }

  function renderAccessoryIcon(type, x, y, size, rotation, theme) {
    const p = iconPalette(theme);
    return `<g class="accessory-svg accessory-${esc(type)}" transform="translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${rotation.toFixed(1)}) scale(${(size / 28).toFixed(3)})">
      ${accessoryPath(type, p)}
    </g>`;
  }

  function getTheme(personality, options) {
    const source = (options && options.themes && options.themes[personality]) || DEFAULT_THEMES[personality] || DEFAULT_THEMES.NBTI;
    const preview = window.PERSONALITIES && window.PERSONALITIES[personality];
    if (preview && preview.colors) {
      return {
        primary: preview.colors.primary,
        secondary: preview.colors.secondary || preview.colors.primary,
        bg: preview.colors.bg,
        name: preview.name,
        effect: preview.effect || source.effect,
        accessories: source.accessories || (source.emojis || []).map(item => EMOJI_ACCESSORY[item]).filter(Boolean)
      };
    }
    return source;
  }

  function getAccessoryIcons(personality, theme, options) {
    const preview = window.PERSONALITIES && window.PERSONALITIES[personality];
    const labels = [];
    if (preview && preview.accessories) {
      Object.values(preview.accessories).forEach(group => Array.isArray(group) && labels.push(...group));
    }
    const labelIcons = labels.map(label => LABEL_ACCESSORY[label] || null).filter(Boolean);
    const themeIcons = (
      theme.accessories ||
      DEFAULT_THEMES[personality]?.accessories ||
      (theme.emojis || DEFAULT_THEMES[personality]?.emojis || []).map(item => EMOJI_ACCESSORY[item]).filter(Boolean)
    ).slice();
    const merged = [];
    [...themeIcons, ...labelIcons].forEach(item => !merged.includes(item) && merged.push(item));
    if (options && options.includeAllAccessories) return merged;
    return merged.slice(0, Math.max(4, Math.min(7, merged.length)));
  }

  function generateSvgAvatar(personality = 'NBTI', options = {}) {
    const theme = getTheme(personality, options);
    const size = options.size || 200;
    const uid = `av_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    const face = faceContour(70, options.scale || 0.70);
    const faceOpacity = theme.effect === 'translucent' ? 0.72 : 1;
    const eyes = bothEyes(Math.max(16, face.width * rand(0.36, 0.46)));
    const distance = rand(face.width / 4.6, face.width / 3.9);
    const eyeY = -(face.height / rand(5.7, 7.4)) - 10;
    const leftEye = { x: -(distance + rand(-face.width / 20, face.width / 10)), y: eyeY + rand(-face.height / 50, face.height / 50) };
    const rightEye = { x: distance + rand(-face.width / 20, face.width / 10), y: eyeY + rand(-face.height / 50, face.height / 50) };
    const pupil = contour => {
      const upper = contour.slice(0, 80), lower = contour.slice(80).reverse();
      const i0 = randInt(10, Math.max(11, upper.length - 10));
      const i1 = randInt(10, Math.max(11, lower.length - 10));
      const t = rand(0.2, 0.8);
      return [upper[i0][0] * t + lower[i1][0] * (1 - t), upper[i0][1] * t + lower[i1][1] * (1 - t)];
    };
    const lp = pupil(eyes.left.contour), rp = pupil(eyes.right.contour);
    const hairColor = personality === 'hexagon' ? '#D97706' : (personality === 'twoface' ? `url(#splitHair_${uid})` : (Math.random() > 0.12 ? pick(naturalHairColors) : `url(#rainbow_${uid})`));
    const hairs = generateHair(face.points);
    const mouth = mouthShape(face.height, face.width);
    const accessoryIcons = getAccessoryIcons(personality, theme, options);
    const bg = Math.random() > 0.52 ? theme.bg : pick(bgAccents);

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" width="${size}" height="${size}" role="img" aria-label="${esc(theme.name || personality)} avatar">`;
    svg += `<defs>
      <filter id="fuzzy_${uid}" x="-8%" y="-8%" width="116%" height="116%">
        <feTurbulence baseFrequency="0.045" numOctaves="3" type="fractalNoise" result="noise"/>
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="1.6"/>
      </filter>
      <clipPath id="leftEye_${uid}"><polyline points="${pts(eyes.left.contour)}"/></clipPath>
      <clipPath id="rightEye_${uid}"><polyline points="${pts(eyes.right.contour)}"/></clipPath>
      <linearGradient id="rainbow_${uid}" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="${theme.primary}"/><stop offset="${randInt(20, 80)}%" stop-color="#22D3EE"/><stop offset="100%" stop-color="${theme.secondary}"/>
      </linearGradient>
      <linearGradient id="splitHair_${uid}" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="49%" stop-color="#111827"/><stop offset="51%" stop-color="#F9FAFB"/>
      </linearGradient>
      <radialGradient id="halo_${uid}"><stop offset="0%" stop-color="${theme.primary}" stop-opacity=".45"/><stop offset="100%" stop-color="${theme.primary}" stop-opacity="0"/></radialGradient>
    </defs>`;
    svg += `<rect x="-100" y="-100" width="200" height="200" fill="${bg}"/>`;
    if (theme.effect === 'split') svg += `<rect x="0" y="-100" width="100" height="200" fill="${theme.secondary}" opacity=".28"/>`;
    if (theme.effect === 'golden' || theme.effect === 'buddha_light' || theme.effect === 'glow') svg += `<circle cx="0" cy="-10" r="72" fill="url(#halo_${uid})"/>`;
    svg += `<g opacity="${faceOpacity}">`;
    svg += `<polyline id="faceContour" class="face-shape" points="${pts(face.points)}" fill="#ffc9a9" stroke="#111" stroke-width="2.2" stroke-linejoin="round" filter="url(#fuzzy_${uid})"/>`;

    const eyeGroup = (id, eye, pos, pupilPoint, clip) => {
      svg += `<g id="${id}" transform="translate(${pos.x.toFixed(1)} ${pos.y.toFixed(1)})">`;
      svg += `<polyline points="${pts(eye.contour)}" fill="#fff" stroke="#fff" stroke-width="0" stroke-linejoin="round" filter="url(#fuzzy_${uid})"/>`;
      svg += `<polyline points="${pts(eye.upper)}" fill="none" stroke="#111" stroke-width="${rand(2.0, 3.3)}" stroke-linejoin="round" stroke-linecap="round" filter="url(#fuzzy_${uid})"/>`;
      svg += `<polyline points="${pts(eye.lower)}" fill="none" stroke="#111" stroke-width="${rand(1.8, 3.1)}" stroke-linejoin="round" stroke-linecap="round" filter="url(#fuzzy_${uid})"/>`;
      for (let i = 0; i < 10; i++) {
        svg += `<circle r="${rand(2.3, 4.7)}" cx="${pupilPoint[0] + rand(-2.2, 2.2)}" cy="${pupilPoint[1] + rand(-2.2, 2.2)}" stroke="#111" fill="none" stroke-width="${rand(0.8, 1.4)}" filter="url(#fuzzy_${uid})" clip-path="url(#${clip})"/>`;
      }
      svg += `</g>`;
    };
    eyeGroup('leftEye', eyes.left, leftEye, lp, `leftEye_${uid}`);
    eyeGroup('rightEye', eyes.right, rightEye, rp, `rightEye_${uid}`);

    svg += `<g id="hairs">`;
    hairs.forEach(h => {
      const shifted = h.map(p => [p[0], p[1] - rand(0, 2)]);
      svg += `<polyline points="${pts(shifted)}" fill="none" stroke="${hairColor}" stroke-width="${rand(0.7, 2.6)}" stroke-linejoin="round" stroke-linecap="round" filter="url(#fuzzy_${uid})" opacity="${rand(0.75, 1)}"/>`;
    });
    svg += `</g>`;

    const noseRight = [rand(face.width / 18, face.width / 12), rand(-3, face.height / 5) - 6];
    const noseLeft = [rand(-face.width / 18, -face.width / 12), noseRight[1] + rand(-face.height / 30, face.height / 20)];
    if (Math.random() > 0.5) {
      [noseLeft, noseRight].forEach(nose => {
        for (let i = 0; i < 10; i++) svg += `<circle r="${rand(0.8, 2.5)}" cx="${nose[0] + rand(-1.8, 1.8)}" cy="${nose[1] + rand(-1.8, 1.8)}" stroke="#111" fill="none" stroke-width="${rand(0.8, 1.3)}" filter="url(#fuzzy_${uid})"/>`;
      });
    } else {
      svg += `<path d="M ${noseLeft[0]} ${noseLeft[1]} Q ${noseRight[0]} ${noseRight[1] * 1.5}, ${(noseLeft[0] + noseRight[0]) / 2} ${-eyeY * 0.18}" fill="none" stroke="#111" stroke-width="${rand(2.1, 3.2)}" stroke-linejoin="round" filter="url(#fuzzy_${uid})"/>`;
    }
    svg += `<polyline points="${pts(mouth)}" fill="rgb(215,127,140)" stroke="#111" stroke-width="${rand(2.3, 3.1)}" stroke-linejoin="round" filter="url(#fuzzy_${uid})"/>`;
    svg += `</g>`;

    function generateAccessoryPositions(count, fw, fh) {
      const positions = [];
      const minR = Math.max(fw, fh) / 2 + 12;
      const maxR = 78;
      for (let i = 0; i < count; i++) {
        const baseAngle = (Math.PI * 2 / count) * i;
        const angle = baseAngle + rand(-0.5, 0.5);
        const r = rand(minR, maxR);
        positions.push([Math.cos(angle) * r, Math.sin(angle) * r]);
      }
      return positions;
    }
    const visibleIcons = accessoryIcons.slice(0, 7);
    const positions = generateAccessoryPositions(visibleIcons.length, face.width, face.height);
    visibleIcons.forEach((icon, i) => {
      const [x, y] = positions[i];
      svg += renderAccessoryIcon(icon, x, y, rand(22, 38), rand(-12, 12), theme);
    });
    if (theme.effect === 'barrage') {
      const barragePositions = generateAccessoryPositions(3, face.width, face.height);
      ['speech', 'keyboard', 'sparkle'].forEach((type, i) => {
        const [x, y] = barragePositions[i];
        svg += renderAccessoryIcon(type, x, y, rand(22, 34), rand(-10, 10), theme);
      });
    }
    svg += `</svg>`;
    return svg;
  }

  window.NBTIAvatar = {
    themes: DEFAULT_THEMES,
    generateSvgAvatar
  };
})();
