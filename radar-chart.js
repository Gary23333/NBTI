(function () {
  // 四轴定义：NB 上、BH 右、TF 下、IP 左；文案提炼自 prompts.py 四维度描述
  const AXES = [
    { key: 'nb', pos: 'N·能动', neg: 'S·稳态', dx: 0, dy: -1 },
    { key: 'bh', pos: 'B·边界', neg: 'H·合群', dx: 1, dy: 0 },
    { key: 'tf', pos: 'T·理性', neg: 'F·感性', dx: 0, dy: 1 },
    { key: 'ip', pos: 'I·强执行', neg: 'P·灵活', dx: -1, dy: 0 }
  ];

  const DEFAULT_COLORS = {
    accent: '#f472b6',
    text: '#e8e8f0',
    textDim: '#8888a0',
    grid: '#2e2e42'
  };

  function cssVar(name) {
    if (typeof window === 'undefined' || typeof document === 'undefined' || !document.documentElement) return '';
    if (typeof window.getComputedStyle !== 'function') return '';
    return window.getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function resolveColors(opts) {
    const c = (opts && opts.colors) || {};
    return {
      accent: c.accent || cssVar('--accent') || DEFAULT_COLORS.accent,
      text: c.text || cssVar('--text') || DEFAULT_COLORS.text,
      textDim: c.textDim || cssVar('--text-dim') || DEFAULT_COLORS.textDim,
      grid: c.grid || cssVar('--border') || DEFAULT_COLORS.grid
    };
  }

  // 归一化：-10..+10 -> 0..1，clamp 到 [0.05, 1]（全 0 彩蛋人格也能画出小多边形）
  function normalize(v) {
    const n = ((Number(v) || 0) + 10) / 20;
    return Math.min(1, Math.max(0.05, n));
  }

  function fmt(n) {
    return Math.round(n * 10) / 10;
  }

  function getRadarSvg(scores, opts) {
    const size = (opts && opts.size) || 240;
    const colors = resolveColors(opts);
    const cx = size / 2;
    const cy = size / 2;
    const r = size / 2 - 56;
    const fontMain = Math.round(size * 0.05);
    const fontSub = Math.round(size * 0.04);
    const s = scores || {};

    const pointAt = (axis, ratio) => [cx + axis.dx * r * ratio, cy + axis.dy * r * ratio];
    const ptsStr = points => points.map(p => `${fmt(p[0])},${fmt(p[1])}`).join(' ');

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" role="img" aria-label="维度画像雷达图">`;

    // 网格圈 25% / 50% / 75% / 100%
    [0.25, 0.5, 0.75, 1].forEach(ratio => {
      svg += `<polygon points="${ptsStr(AXES.map(a => pointAt(a, ratio)))}" fill="none" stroke="${colors.grid}" stroke-width="1"/>`;
    });

    // 轴线 + 中心点
    AXES.forEach(a => {
      const [x, y] = pointAt(a, 1);
      svg += `<line x1="${fmt(cx)}" y1="${fmt(cy)}" x2="${fmt(x)}" y2="${fmt(y)}" stroke="${colors.grid}" stroke-width="1"/>`;
    });
    svg += `<circle cx="${fmt(cx)}" cy="${fmt(cy)}" r="2" fill="${colors.grid}"/>`;

    // 数据多边形 + 顶点圆点
    const dataPoints = AXES.map(a => pointAt(a, normalize(s[a.key])));
    svg += `<polygon points="${ptsStr(dataPoints)}" fill="${colors.accent}" fill-opacity="0.2" stroke="${colors.accent}" stroke-width="2" stroke-linejoin="round"/>`;
    dataPoints.forEach(p => {
      svg += `<circle cx="${fmt(p[0])}" cy="${fmt(p[1])}" r="3" fill="${colors.accent}"/>`;
    });

    // 轴标签：外端正极（正分方向），内侧负极
    AXES.forEach(a => {
      const vertical = a.dx === 0;
      const outSign = vertical ? a.dy : a.dx;
      const anchor = vertical ? 'middle' : (a.dx > 0 ? 'start' : 'end');
      const gap = 8;
      const lx = cx + a.dx * (r + gap);
      const ly = cy + a.dy * (r + gap);
      let posX, posY, negX, negY;
      if (vertical) {
        posX = negX = lx;
        if (outSign < 0) { posY = ly - fontSub - 6; negY = ly - 2; }
        else { negY = ly + fontSub + 2; posY = negY + fontMain + 4; }
      } else {
        posY = ly - 3;
        negY = ly + fontSub + 3;
        posX = negX = lx;
      }
      svg += `<text x="${fmt(posX)}" y="${fmt(posY)}" text-anchor="${anchor}" font-size="${fontMain}" font-weight="600" fill="${colors.text}">${a.pos}</text>`;
      svg += `<text x="${fmt(negX)}" y="${fmt(negY)}" text-anchor="${anchor}" font-size="${fontSub}" fill="${colors.textDim}">${a.neg}</text>`;
    });

    svg += '</svg>';
    return svg;
  }

  function renderRadar(container, scores, opts) {
    if (typeof container === 'string') container = document.getElementById(container);
    if (!container) return null;
    container.innerHTML = getRadarSvg(scores, opts);
    return container;
  }

  window.NBTIRadar = {
    renderRadar,
    getRadarSvg
  };
})();
