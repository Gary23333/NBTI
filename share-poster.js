(function () {
  const W = 750;
  const H = 1200;
  const PAD = 52;

  const THEMES = {
    workplace: {
      id: 'workplace',
      name: '职场人格',
      icon: '💼',
      bg: '#0f0e17',
      bgTop: '#171423',
      bgGlow1: '#8b5cf6',
      bgGlow2: '#ec4899',
      accent: '#f472b6',
      accent2: '#8b5cf6',
      text: '#f5f3ff',
      textDim: '#b9b6d3',
      textFaint: '#7d7a96',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(255,255,255,0.04)',
      radar: { accent: '#f472b6', text: '#e8e8f0', textDim: '#8888a0', grid: '#3a3a52' }
    },
    animal: {
      id: 'animal',
      name: '动物系人格',
      icon: '🐾',
      bg: '#0d1b0f',
      bgTop: '#132a17',
      bgGlow1: '#f59e0b',
      bgGlow2: '#10b981',
      accent: '#fbbf24',
      accent2: '#34d399',
      text: '#f0fdf4',
      textDim: '#a7d7b5',
      textFaint: '#6b9077',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(16,185,129,0.06)',
      radar: { accent: '#fbbf24', text: '#d1fae5', textDim: '#6ee7b7', grid: '#2d4a35' }
    },
    color: {
      id: 'color',
      name: '色彩人格',
      icon: '🎨',
      bg: '#0f0f1a',
      bgTop: '#1a1025',
      bgGlow1: '#f43f5e',
      bgGlow2: '#06b6d4',
      accent: '#f472b6',
      accent2: '#38bdf8',
      text: '#fef3ff',
      textDim: '#d4b8e8',
      textFaint: '#8b6ca3',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(244,114,182,0.06)',
      radar: { accent: '#f472b6', text: '#fce7f3', textDim: '#f9a8d4', grid: '#3b2450' }
    },
    love: {
      id: 'love',
      name: '恋爱人格',
      icon: '💕',
      bg: '#1a0d14',
      bgTop: '#251019',
      bgGlow1: '#ec4899',
      bgGlow2: '#f43f5e',
      accent: '#f472b6',
      accent2: '#fb7185',
      text: '#fff1f2',
      textDim: '#e8b4c4',
      textFaint: '#a37889',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(236,72,153,0.06)',
      radar: { accent: '#f472b6', text: '#ffe4e6', textDim: '#fda4af', grid: '#4a2434' }
    },
    social: {
      id: 'social',
      name: '社交人格',
      icon: '👥',
      bg: '#14100b',
      bgTop: '#1f160d',
      bgGlow1: '#f97316',
      bgGlow2: '#06b6d4',
      accent: '#fb923c',
      accent2: '#22d3ee',
      text: '#fff7ed',
      textDim: '#e0c4a8',
      textFaint: '#a08870',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(249,115,22,0.06)',
      radar: { accent: '#fb923c', text: '#ffedd5', textDim: '#fdba74', grid: '#453324' }
    },
    mbti: {
      id: 'mbti',
      name: '官方MBTI',
      icon: '🧠',
      bg: '#0e0f1c',
      bgTop: '#151731',
      bgGlow1: '#6366f1',
      bgGlow2: '#8b5cf6',
      accent: '#818cf8',
      accent2: '#a78bfa',
      text: '#eef2ff',
      textDim: '#b6bce0',
      textFaint: '#7c81a8',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(99,102,241,0.06)',
      radar: { accent: '#818cf8', text: '#e0e7ff', textDim: '#a5b4fc', grid: '#2e3160' }
    },
    brainhol: {
      id: 'brainhol',
      name: '脑洞人格',
      icon: '🤯',
      bg: '#130b1c',
      bgTop: '#1c1029',
      bgGlow1: '#a855f7',
      bgGlow2: '#22d3ee',
      accent: '#c084fc',
      accent2: '#22d3ee',
      text: '#faf5ff',
      textDim: '#d0b3ec',
      textFaint: '#9378ad',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(168,85,247,0.07)',
      radar: { accent: '#c084fc', text: '#f3e8ff', textDim: '#d8b4fe', grid: '#3d2653' }
    },
    money: {
      id: 'money',
      name: '搞钱人格',
      icon: '💰',
      bg: '#171208',
      bgTop: '#211a0b',
      bgGlow1: '#f59e0b',
      bgGlow2: '#10b981',
      accent: '#fbbf24',
      accent2: '#34d399',
      text: '#fffbeb',
      textDim: '#e0cda2',
      textFaint: '#a08e68',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(245,158,11,0.07)',
      radar: { accent: '#fbbf24', text: '#fef3c7', textDim: '#fcd34d', grid: '#463a1d' }
    },
    spirit: {
      id: 'spirit',
      name: '精神状态检测',
      icon: '🔋',
      bg: '#100c1a',
      bgTop: '#181229',
      bgGlow1: '#7c3aed',
      bgGlow2: '#0ea5e9',
      accent: '#a78bfa',
      accent2: '#38bdf8',
      text: '#f5f3ff',
      textDim: '#c2b8e6',
      textFaint: '#877da8',
      line: 'rgba(255,255,255,0.08)',
      panel: 'rgba(124,58,237,0.07)',
      radar: { accent: '#a78bfa', text: '#ede9fe', textDim: '#c4b5fd', grid: '#33264d' }
    }
  };

  const DEFAULT_THEME = 'workplace';

  const FONT_STACK = "-apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif";
  const MONO_STACK = "'SF Mono', 'Courier New', monospace";

  function getTheme(themeId) {
    return THEMES[themeId] || THEMES[DEFAULT_THEME];
  }

  function svgToImage(svg) {
    return new Promise((resolve) => {
      if (typeof svg !== 'string' || !svg) { resolve(null); return; }
      if (!/xmlns=/.test(svg)) {
        svg = svg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
      }
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => resolve(null);
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
      setTimeout(() => resolve(img.complete && img.naturalWidth ? img : null), 3000);
    });
  }

  function roundRectPath(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function wrapLines(ctx, text, maxWidth, maxLines) {
    const str = String(text || '').replace(/\s+/g, ' ').trim();
    if (!str) return [];
    const lines = [];
    let line = '';
    for (const ch of str) {
      if (ctx.measureText(line + ch).width > maxWidth && line) {
        lines.push(line);
        line = ch;
        if (lines.length === maxLines) break;
      } else {
        line += ch;
      }
    }
    if (lines.length < maxLines && line) lines.push(line);
    const consumed = lines.join('').length;
    if (consumed < str.length && lines.length) {
      let last = lines[lines.length - 1];
      while (last && ctx.measureText(last + '…').width > maxWidth) last = last.slice(0, -1);
      lines[lines.length - 1] = last + '…';
    }
    return lines;
  }

  function drawCenteredLines(ctx, lines, y, lineHeight) {
    lines.forEach((line, i) => ctx.fillText(line, W / 2, y + i * lineHeight));
    return y + lines.length * lineHeight;
  }

  function formatDate(d) {
    const p = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}.${p(d.getMonth() + 1)}.${p(d.getDate())}`;
  }

  function glow(ctx, x, y, radius, color, alpha) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, radius);
    g.addColorStop(0, color);
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.fillStyle = g;
    ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
    ctx.restore();
  }

  function paintBackground(ctx, theme) {
    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, theme.bgTop);
    bgGrad.addColorStop(0.4, theme.bg);
    bgGrad.addColorStop(1, theme.bg);
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);
    glow(ctx, W - 80, 100, 320, theme.bgGlow1, 0.12);
    glow(ctx, 80, H - 180, 360, theme.bgGlow2, 0.10);
    glow(ctx, W / 2, H / 2, 400, theme.accent2, 0.05);
  }

  function paintHeader(ctx, theme, themeInfo) {
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';

    ctx.fillStyle = theme.accent;
    ctx.font = `600 22px ${FONT_STACK}`;
    const themeLabel = themeInfo ? themeInfo.icon + ' ' + themeInfo.name : theme.name;
    ctx.fillText(themeLabel, W / 2, 70);

    ctx.fillStyle = theme.text;
    ctx.font = `800 32px ${FONT_STACK}`;
    ctx.fillText('NBTI · 人格测试', W / 2, 112);

    ctx.strokeStyle = theme.line;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PAD, 140);
    ctx.lineTo(W - PAD, 140);
    ctx.stroke();

    ctx.save();
    ctx.translate(W / 2, 140);
    ctx.rotate(Math.PI / 4);
    ctx.fillStyle = theme.accent;
    ctx.fillRect(-5, -5, 10, 10);
    ctx.restore();
  }

  function paintFooter(ctx, theme, slogan) {
    ctx.strokeStyle = theme.line;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PAD, H - 80);
    ctx.lineTo(W - PAD, H - 80);
    ctx.stroke();

    ctx.font = `400 22px ${FONT_STACK}`;
    ctx.fillStyle = theme.textFaint;
    ctx.textAlign = 'left';
    ctx.fillText(formatDate(new Date()), PAD, H - 36);
    ctx.textAlign = 'right';
    const host = (typeof location !== 'undefined' && location.host) || '';
    ctx.fillText(`${slogan}${host ? ' · ' + host : ''}`, W - PAD, H - 36);
  }

  async function generate(result, scores, opts) {
    const r = result || {};
    const options = opts || {};
    const theme = getTheme(options.theme);
    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');

    paintBackground(ctx, theme);
    paintHeader(ctx, theme, options.themeInfo);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';

    const AVATAR = 240;
    const ax = (W - AVATAR) / 2;
    const ay = 175;
    let avatarImg = null;
    if (window.NBTIAvatar && typeof window.NBTIAvatar.generateSvgAvatar === 'function') {
      try {
        avatarImg = await svgToImage(window.NBTIAvatar.generateSvgAvatar(r.type, { theme: options.theme }));
      } catch (e) { avatarImg = null; }
    }
    ctx.save();
    roundRectPath(ctx, ax, ay, AVATAR, AVATAR, 36);
    ctx.clip();
    if (avatarImg) {
      ctx.drawImage(avatarImg, ax, ay, AVATAR, AVATAR);
    } else {
      ctx.fillStyle = theme.panel;
      ctx.fillRect(ax, ay, AVATAR, AVATAR);
      ctx.fillStyle = theme.textFaint;
      ctx.font = `400 24px ${FONT_STACK}`;
      ctx.fillText(r.type || 'NBTI', W / 2, ay + AVATAR / 2 + 8);
    }
    ctx.restore();
    roundRectPath(ctx, ax - 3, ay - 3, AVATAR + 6, AVATAR + 6, 38);
    const borderGrad = ctx.createLinearGradient(ax, ay, ax + AVATAR, ay + AVATAR);
    borderGrad.addColorStop(0, theme.accent);
    borderGrad.addColorStop(1, theme.accent2);
    ctx.strokeStyle = borderGrad;
    ctx.lineWidth = 4;
    ctx.stroke();

    let y = ay + AVATAR + 70;
    ctx.fillStyle = theme.accent;
    ctx.font = `900 64px ${MONO_STACK}`;
    ctx.fillText(String(r.type || 'UNKNOWN'), W / 2, y);

    y += 56;
    ctx.fillStyle = theme.text;
    ctx.font = `800 38px ${FONT_STACK}`;
    ctx.fillText(String(r.name || ''), W / 2, y);

    y += 42;
    ctx.fillStyle = theme.textDim;
    ctx.font = `500 26px ${FONT_STACK}`;
    const onelineText = r.oneline ? '"' + r.oneline + '"' : '';
    y = drawCenteredLines(ctx, wrapLines(ctx, onelineText, W - PAD * 2 - 80, 2), y, 40);

    const RADAR = 300;
    const ry = y + 36;
    let radarImg = null;
    if (window.NBTIRadar && typeof window.NBTIRadar.getRadarSvg === 'function') {
      try {
        radarImg = await svgToImage(window.NBTIRadar.getRadarSvg(scores, { size: RADAR, colors: theme.radar }));
      } catch (e) { radarImg = null; }
    }
    if (radarImg) {
      ctx.save();
      ctx.shadowColor = theme.accent;
      ctx.shadowBlur = 40;
      ctx.drawImage(radarImg, (W - RADAR) / 2, ry, RADAR, RADAR);
      ctx.restore();
    } else {
      ctx.strokeStyle = theme.line;
      ctx.strokeRect((W - RADAR) / 2, ry, RADAR, RADAR);
    }
    y = ry + RADAR;

    const metaBoxY = y + 24;
    const metaBoxH = 200;
    roundRectPath(ctx, PAD, metaBoxY, W - PAD * 2, metaBoxH, 20);
    ctx.fillStyle = theme.panel;
    ctx.fill();
    ctx.strokeStyle = theme.line;
    ctx.lineWidth = 1;
    ctx.stroke();

    const metas = [
      { icon: '🎬', label: '名场面', value: r.scene },
      { icon: '🎯', label: '适配', value: r.adapt },
      { icon: '⚠️', label: '翻车', value: r.crash }
    ].filter(m => m.value);

    ctx.textAlign = 'left';
    const metaStartY = metaBoxY + 42;
    const metaLineH = 48;
    metas.slice(0, 3).forEach((m, i) => {
      const my = metaStartY + i * metaLineH;
      ctx.font = `600 22px ${FONT_STACK}`;
      ctx.fillStyle = theme.accent;
      ctx.fillText(m.icon + ' ' + m.label, PAD + 28, my);
      const labelWidth = ctx.measureText(m.icon + ' ' + m.label).width + 28;
      ctx.font = `400 22px ${FONT_STACK}`;
      ctx.fillStyle = theme.textDim;
      const maxW = W - PAD * 2 - 56 - labelWidth;
      const valLines = wrapLines(ctx, m.value, maxW, 1);
      if (valLines[0]) {
        ctx.fillText(valLines[0], PAD + 28 + labelWidth, my);
      }
    });

    paintFooter(ctx, theme, options.slogan || '测测你是哪种人格');

    return canvas;
  }

  async function download(result, scores, opts, filename) {
    const options = typeof opts === 'string' ? { filename: opts } : (opts || {});
    const canvas = await generate(result, scores, options);
    const type = (result && result.type) || 'result';
    const name = filename || options.filename || `nbti-${String(type).toLowerCase()}-poster.png`;
    return new Promise((resolve) => {
      const done = url => {
        const link = document.createElement('a');
        link.download = name;
        link.href = url;
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 100);
        resolve();
      };
      if (canvas.toBlob) {
        canvas.toBlob(blob => {
          if (blob) done(URL.createObjectURL(blob));
          else done(canvas.toDataURL('image/png'));
        }, 'image/png');
      } else {
        done(canvas.toDataURL('image/png'));
      }
    });
  }

  function lookupName(type) {
    const t = String(type || '').toUpperCase();
    if (window.NBTICompat && window.NBTICompat.TYPES && window.NBTICompat.TYPES[t]) {
      return window.NBTICompat.TYPES[t].name;
    }
    return String(type || 'UNKNOWN');
  }

  async function drawCompatAvatar(ctx, type, x, y, size, theme, avatarTheme) {
    let img = null;
    if (window.NBTIAvatar && typeof window.NBTIAvatar.generateSvgAvatar === 'function') {
      try {
        img = await svgToImage(window.NBTIAvatar.generateSvgAvatar(type, { theme: avatarTheme }));
      } catch (e) { img = null; }
    }
    ctx.save();
    roundRectPath(ctx, x, y, size, size, 28);
    ctx.clip();
    if (img) {
      ctx.drawImage(img, x, y, size, size);
    } else {
      ctx.fillStyle = theme.panel;
      ctx.fillRect(x, y, size, size);
      ctx.fillStyle = theme.textFaint;
      ctx.font = `400 20px ${FONT_STACK}`;
      ctx.textAlign = 'center';
      ctx.fillText(String(type || '???'), x + size / 2, y + size / 2 + 7);
    }
    ctx.restore();
    roundRectPath(ctx, x - 2, y - 2, size + 4, size + 4, 30);
    const borderGrad = ctx.createLinearGradient(x, y, x + size, y + size);
    borderGrad.addColorStop(0, theme.accent);
    borderGrad.addColorStop(1, theme.accent2);
    ctx.strokeStyle = borderGrad;
    ctx.lineWidth = 3;
    ctx.stroke();
  }

  async function generateCompat(mine, theirs, compat, opts) {
    const m = mine || {};
    const t = theirs || {};
    const c = compat || {};
    const options = opts || {};
    const theme = getTheme(options.theme);
    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');

    paintBackground(ctx, theme);
    paintHeader(ctx, theme, options.themeInfo);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';

    ctx.fillStyle = theme.accent2;
    ctx.font = `700 28px ${FONT_STACK}`;
    ctx.fillText('💞 CP合盘报告', W / 2, 180);

    const AV = 200;
    const GAP = 100;
    const ay = 220;
    const leftX = (W - AV * 2 - GAP) / 2;
    const rightX = leftX + AV + GAP;
    await drawCompatAvatar(ctx, m.type, leftX, ay, AV, theme, options.theme);
    await drawCompatAvatar(ctx, t.type, rightX, ay, AV, theme, options.theme);

    const badgeX = W / 2;
    const badgeY = ay + AV / 2;
    ctx.beginPath();
    ctx.arc(badgeX, badgeY, 50, 0, Math.PI * 2);
    const badgeGrad = ctx.createLinearGradient(badgeX - 50, badgeY - 50, badgeX + 50, badgeY + 50);
    badgeGrad.addColorStop(0, theme.accent);
    badgeGrad.addColorStop(1, theme.accent2);
    ctx.fillStyle = badgeGrad;
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.4)';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = '#ffffff';
    ctx.font = `900 32px ${FONT_STACK}`;
    ctx.fillText('❤', badgeX, badgeY + 12);

    const nameOf = (side, fallbackType) => String(side.name || lookupName(fallbackType));
    ctx.font = `800 28px ${MONO_STACK}`;
    ctx.fillStyle = theme.accent;
    ctx.fillText(String(m.type || '???'), leftX + AV / 2, ay + AV + 48);
    ctx.fillText(String(t.type || '???'), rightX + AV / 2, ay + AV + 48);
    ctx.font = `700 24px ${FONT_STACK}`;
    ctx.fillStyle = theme.text;
    const leftName = wrapLines(ctx, nameOf(m, m.type), AV + 40, 1);
    const rightName = wrapLines(ctx, nameOf(t, t.type), AV + 40, 1);
    if (leftName[0]) ctx.fillText(leftName[0], leftX + AV / 2, ay + AV + 84);
    if (rightName[0]) ctx.fillText(rightName[0], rightX + AV / 2, ay + AV + 84);

    let y = ay + AV + 150;
    ctx.fillStyle = theme.textDim;
    ctx.font = `600 24px ${FONT_STACK}`;
    ctx.fillText('合 拍 指 数', W / 2, y);

    y += 90;
    const hasScore = typeof c.score === 'number';
    ctx.fillStyle = theme.accent;
    ctx.font = `900 120px ${FONT_STACK}`;
    const scoreText = hasScore ? String(c.score) : '--';
    ctx.fillText(scoreText, W / 2 - 30, y);
    if (hasScore) {
      ctx.font = `700 48px ${FONT_STACK}`;
      ctx.fillText('%', W / 2 + 80, y - 48);
    }

    if (hasScore) {
      const BAR_W = 440;
      const barX = (W - BAR_W) / 2;
      const barY = y + 36;
      roundRectPath(ctx, barX, barY, BAR_W, 16, 8);
      ctx.fillStyle = theme.panel;
      ctx.fill();
      const scoreRatio = Math.max(0, Math.min(100, c.score)) / 100;
      roundRectPath(ctx, barX, barY, BAR_W * scoreRatio, 16, 8);
      const barGrad = ctx.createLinearGradient(barX, barY, barX + BAR_W, barY);
      barGrad.addColorStop(0, theme.accent);
      barGrad.addColorStop(1, theme.accent2);
      ctx.fillStyle = barGrad;
      ctx.fill();
    }

    y += hasScore ? 130 : 90;
    ctx.fillStyle = theme.text;
    ctx.font = `800 42px ${FONT_STACK}`;
    ctx.fillText(String(c.title || ''), W / 2, y);

    y += 40;
    const verdictBoxY = y;
    const verdictBoxH = 220;
    roundRectPath(ctx, PAD, verdictBoxY, W - PAD * 2, verdictBoxH, 20);
    ctx.fillStyle = theme.panel;
    ctx.fill();
    ctx.strokeStyle = theme.line;
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.fillStyle = theme.textDim;
    ctx.font = `400 24px ${FONT_STACK}`;
    ctx.textAlign = 'center';
    const verdictLines = wrapLines(ctx, c.verdict, W - PAD * 2 - 60, 5);
    const verdictStartY = verdictBoxY + 36;
    verdictLines.forEach((line, i) => {
      ctx.fillText(line, W / 2, verdictStartY + i * 40);
    });

    paintFooter(ctx, theme, options.slogan || '测测你们是绝配还是互怼');

    return canvas;
  }

  async function downloadCompat(mine, theirs, compat, opts, filename) {
    const options = typeof opts === 'string' ? { filename: opts } : (opts || {});
    const canvas = await generateCompat(mine, theirs, compat, options);
    const mType = String((mine && mine.type) || 'me').toLowerCase();
    const tType = String((theirs && theirs.type) || 'ta').toLowerCase();
    const name = filename || options.filename || `nbti-compat-${mType}-${tType}.png`;
    return new Promise((resolve) => {
      const done = url => {
        const link = document.createElement('a');
        link.download = name;
        link.href = url;
        link.click();
        setTimeout(() => URL.revokeObjectURL(url), 100);
        resolve();
      };
      if (canvas.toBlob) {
        canvas.toBlob(blob => {
          if (blob) done(URL.createObjectURL(blob));
          else done(canvas.toDataURL('image/png'));
        }, 'image/png');
      } else {
        done(canvas.toDataURL('image/png'));
      }
    });
  }

  function generateCopyText(result, themeName, hashtags) {
    const r = result || {};
    const lines = [];
    lines.push(`【${r.type || 'NBTI'} · ${r.name || '神秘人格'}】`);
    if (r.oneline) {
      lines.push(`"${r.oneline}"`);
    }
    lines.push('');
    const traits = [];
    if (r.scene) traits.push(`▫️ 名场面：${r.scene}`);
    if (r.adapt) traits.push(`▫️ 适配：${r.adapt}`);
    if (r.crash) traits.push(`▫️ 翻车：${r.crash}`);
    if (traits.length) {
      lines.push(...traits);
      lines.push('');
    }
    const theme = themeName ? `#${themeName}` : '#NBTI人格测试';
    const tags = hashtags || ['#人格测试', '#NBTI', '#职场人格'];
    lines.push([theme, ...tags].join(' '));
    return lines.join('\n');
  }

  window.NBTIPoster = {
    THEMES,
    getTheme,
    generate,
    download,
    generateCompat,
    downloadCompat,
    generateCopyText
  };
})();