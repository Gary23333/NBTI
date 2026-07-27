(function () {
  // 分享海报生成器：零依赖原生 Canvas，固定深色配色（不随页面主题变，保证分享一致性）
  const W = 750;
  const H = 1200;
  const PAD = 48;

  const COLORS = {
    bg: '#0f0e17',
    bgTop: '#171423',
    accent: '#f472b6',
    text: '#f5f3ff',
    textDim: '#b9b6d3',
    textFaint: '#7d7a96',
    line: 'rgba(255,255,255,0.08)',
    panel: 'rgba(255,255,255,0.04)',
    radar: { accent: '#f472b6', text: '#e8e8f0', textDim: '#8888a0', grid: '#3a3a52' }
  };

  const FONT_STACK = "-apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif";
  const MONO_STACK = "'SF Mono', 'Courier New', monospace";

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
      // 兜底：极端情况下 onload/onerror 均不触发
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

  // CJK 友好换行：逐字符测量，返回行数组，最多 maxLines 行，超出截断加省略号
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
    // 被截断时给最后一行补省略号
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

  // ---- 背景：深色底 + 微弱纵向渐变 + 角落装饰光晕 ----
  function paintBackground(ctx) {
    const bgGrad = ctx.createLinearGradient(0, 0, 0, H);
    bgGrad.addColorStop(0, COLORS.bgTop);
    bgGrad.addColorStop(0.35, COLORS.bg);
    bgGrad.addColorStop(1, COLORS.bg);
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);
    glow(ctx, W - 60, 80, 260, COLORS.accent, 0.10);
    glow(ctx, 60, H - 140, 300, '#60a5fa', 0.08);
  }

  // ---- 顶部品牌 + 分隔线 ----
  function paintHeader(ctx) {
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = COLORS.text;
    ctx.font = `700 30px ${FONT_STACK}`;
    ctx.fillText('NBTI · 牛比体', W / 2, 78);

    ctx.strokeStyle = COLORS.line;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PAD, 104);
    ctx.lineTo(W - PAD, 104);
    ctx.stroke();
    // 分隔线中心的小装饰
    ctx.fillStyle = COLORS.accent;
    ctx.save();
    ctx.translate(W / 2, 104);
    ctx.rotate(Math.PI / 4);
    ctx.fillRect(-4, -4, 8, 8);
    ctx.restore();
  }

  // ---- 底部：日期 + 域名 slogan ----
  function paintFooter(ctx, slogan) {
    ctx.strokeStyle = COLORS.line;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(PAD, H - 96);
    ctx.lineTo(W - PAD, H - 96);
    ctx.stroke();

    ctx.font = `400 20px ${FONT_STACK}`;
    ctx.fillStyle = COLORS.textFaint;
    ctx.textAlign = 'left';
    ctx.fillText(formatDate(new Date()), PAD, H - 52);
    ctx.textAlign = 'right';
    const host = (typeof location !== 'undefined' && location.host) || '';
    ctx.fillText(`${slogan} · ${host}`, W - PAD, H - 52);
  }

  async function generate(result, scores) {
    const r = result || {};
    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');

    paintBackground(ctx);
    paintHeader(ctx);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';

    // ---- 头像（居中，圆角）----
    const AVATAR = 260;
    const ax = (W - AVATAR) / 2;
    const ay = 140;
    let avatarImg = null;
    if (window.NBTIAvatar && typeof window.NBTIAvatar.generateSvgAvatar === 'function') {
      try {
        avatarImg = await svgToImage(window.NBTIAvatar.generateSvgAvatar(r.type));
      } catch (e) { avatarImg = null; }
    }
    ctx.save();
    roundRectPath(ctx, ax, ay, AVATAR, AVATAR, 32);
    ctx.clip();
    if (avatarImg) {
      ctx.drawImage(avatarImg, ax, ay, AVATAR, AVATAR);
    } else {
      ctx.fillStyle = COLORS.panel;
      ctx.fillRect(ax, ay, AVATAR, AVATAR);
      ctx.fillStyle = COLORS.textFaint;
      ctx.font = `400 22px ${FONT_STACK}`;
      ctx.fillText(r.type || 'NBTI', W / 2, ay + AVATAR / 2 + 8);
    }
    ctx.restore();
    roundRectPath(ctx, ax, ay, AVATAR, AVATAR, 32);
    ctx.strokeStyle = 'rgba(244,114,182,0.45)';
    ctx.lineWidth = 3;
    ctx.stroke();

    // ---- 类型代码 / 名称 / 一句话 ----
    let y = ay + AVATAR + 76;
    ctx.fillStyle = COLORS.accent;
    ctx.font = `800 58px ${MONO_STACK}`;
    ctx.fillText(String(r.type || 'UNKNOWN'), W / 2, y);

    y += 52;
    ctx.fillStyle = COLORS.text;
    ctx.font = `700 34px ${FONT_STACK}`;
    ctx.fillText(String(r.name || ''), W / 2, y);

    y += 30;
    ctx.fillStyle = COLORS.textDim;
    ctx.font = `400 24px ${FONT_STACK}`;
    y = drawCenteredLines(ctx, wrapLines(ctx, r.oneline, W - PAD * 2 - 60, 3), y + 8, 36);

    // ---- 雷达图 ----
    const RADAR = 320;
    const ry = y + 24;
    let radarImg = null;
    if (window.NBTIRadar && typeof window.NBTIRadar.getRadarSvg === 'function') {
      try {
        radarImg = await svgToImage(window.NBTIRadar.getRadarSvg(scores, { size: RADAR, colors: COLORS.radar }));
      } catch (e) { radarImg = null; }
    }
    if (radarImg) {
      ctx.drawImage(radarImg, (W - RADAR) / 2, ry, RADAR, RADAR);
    } else {
      ctx.strokeStyle = COLORS.line;
      ctx.strokeRect((W - RADAR) / 2, ry, RADAR, RADAR);
    }
    y = ry + RADAR + 30;

    // ---- meta 三条（弹性高度，给底部留出 120px）----
    const metas = [
      ['🎬 名场面', r.scene],
      ['🎯 适配岗位', r.adapt],
      ['⚠️ 翻车场景', r.crash]
    ].filter(m => m[1]);

    const metaMaxBottom = H - 120;
    ctx.textAlign = 'left';
    for (const [label, value] of metas) {
      if (y + 34 > metaMaxBottom) break;
      ctx.font = `600 22px ${FONT_STACK}`;
      ctx.fillStyle = COLORS.accent;
      ctx.fillText(label, PAD + 8, y + 22);
      const labelWidth = ctx.measureText(label).width + 24;
      ctx.font = `400 22px ${FONT_STACK}`;
      ctx.fillStyle = COLORS.textDim;
      const lines = wrapLines(ctx, value, W - PAD * 2 - 16 - labelWidth, 2);
      lines.forEach((line, i) => {
        if (y + 22 + i * 32 > metaMaxBottom) return;
        ctx.fillText(line, PAD + 8 + (i === 0 ? labelWidth : 0), y + 22 + i * 32);
      });
      y += lines.length * 32 + 12;
    }

    // ---- 底部：日期 + 域名 slogan ----
    paintFooter(ctx, '测测你是哪种职场生物');

    return canvas;
  }

  async function download(result, scores, filename) {
    const canvas = await generate(result, scores);
    const type = (result && result.type) || 'result';
    const name = filename || `nbti-${String(type).toLowerCase()}-poster.png`;
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

  // 好友名查询：优先 NBTICompat.TYPES，查不到回退类型码
  function lookupName(type) {
    const t = String(type || '').toUpperCase();
    if (window.NBTICompat && window.NBTICompat.TYPES && window.NBTICompat.TYPES[t]) {
      return window.NBTICompat.TYPES[t].name;
    }
    return String(type || 'UNKNOWN');
  }

  async function drawCompatAvatar(ctx, type, x, y, size) {
    let img = null;
    if (window.NBTIAvatar && typeof window.NBTIAvatar.generateSvgAvatar === 'function') {
      try {
        img = await svgToImage(window.NBTIAvatar.generateSvgAvatar(type));
      } catch (e) { img = null; }
    }
    ctx.save();
    roundRectPath(ctx, x, y, size, size, 28);
    ctx.clip();
    if (img) {
      ctx.drawImage(img, x, y, size, size);
    } else {
      ctx.fillStyle = COLORS.panel;
      ctx.fillRect(x, y, size, size);
      ctx.fillStyle = COLORS.textFaint;
      ctx.font = `400 20px ${FONT_STACK}`;
      ctx.textAlign = 'center';
      ctx.fillText(String(type || '???'), x + size / 2, y + size / 2 + 7);
    }
    ctx.restore();
    roundRectPath(ctx, x, y, size, size, 28);
    ctx.strokeStyle = 'rgba(244,114,182,0.45)';
    ctx.lineWidth = 3;
    ctx.stroke();
  }

  // 合拍海报：mine {type,name}（分享页当前用户）、theirs {type}、compat 为 NBTICompat.getCompat 返回结构
  async function generateCompat(mine, theirs, compat) {
    const m = mine || {};
    const t = theirs || {};
    const c = compat || {};
    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');

    paintBackground(ctx);
    paintHeader(ctx);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'alphabetic';

    // ---- 左右头像 + 中间 VS 徽章 ----
    const AV = 200;
    const GAP = 110;
    const ay = 150;
    const leftX = (W - AV * 2 - GAP) / 2;
    const rightX = leftX + AV + GAP;
    await drawCompatAvatar(ctx, m.type, leftX, ay, AV);
    await drawCompatAvatar(ctx, t.type, rightX, ay, AV);

    // VS 圆形徽章
    const badgeX = W / 2;
    const badgeY = ay + AV / 2;
    ctx.beginPath();
    ctx.arc(badgeX, badgeY, 46, 0, Math.PI * 2);
    ctx.fillStyle = COLORS.accent;
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.35)';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = '#ffffff';
    ctx.font = `800 38px ${FONT_STACK}`;
    ctx.fillText('VS', badgeX, badgeY + 13);

    // ---- 两侧类型码 / 名称 ----
    const nameOf = (side, fallbackType) => String(side.name || lookupName(fallbackType));
    ctx.font = `800 30px ${MONO_STACK}`;
    ctx.fillStyle = COLORS.accent;
    ctx.fillText(String(m.type || '???'), leftX + AV / 2, ay + AV + 44);
    ctx.fillText(String(t.type || '???'), rightX + AV / 2, ay + AV + 44);
    ctx.font = `700 24px ${FONT_STACK}`;
    ctx.fillStyle = COLORS.text;
    const leftName = wrapLines(ctx, nameOf(m, m.type), AV + 30, 1);
    const rightName = wrapLines(ctx, nameOf(t, t.type), AV + 30, 1);
    if (leftName[0]) ctx.fillText(leftName[0], leftX + AV / 2, ay + AV + 80);
    if (rightName[0]) ctx.fillText(rightName[0], rightX + AV / 2, ay + AV + 80);

    // ---- 合拍指数（大字 + 进度条）----
    let y = ay + AV + 170;
    ctx.fillStyle = COLORS.textDim;
    ctx.font = `600 24px ${FONT_STACK}`;
    ctx.fillText('合 拍 指 数', W / 2, y);

    y += 100;
    const hasScore = typeof c.score === 'number';
    ctx.fillStyle = COLORS.accent;
    ctx.font = `800 110px ${FONT_STACK}`;
    ctx.fillText(hasScore ? String(c.score) : '--', W / 2 - 24, y);
    if (hasScore) {
      ctx.font = `700 44px ${FONT_STACK}`;
      ctx.fillText('%', W / 2 + 74, y - 44);
    }

    if (hasScore) {
      const BAR_W = 420;
      const barX = (W - BAR_W) / 2;
      const barY = y + 36;
      ctx.fillStyle = COLORS.panel;
      ctx.fillRect(barX, barY, BAR_W, 12);
      ctx.fillStyle = COLORS.accent;
      ctx.fillRect(barX, barY, Math.max(0, Math.min(100, c.score)) / 100 * BAR_W, 12);
    }

    // ---- 组合名 + verdict ----
    y += hasScore ? 130 : 96;
    ctx.fillStyle = COLORS.text;
    ctx.font = `700 40px ${FONT_STACK}`;
    ctx.fillText(String(c.title || ''), W / 2, y);

    y += 34;
    ctx.fillStyle = COLORS.textDim;
    ctx.font = `400 24px ${FONT_STACK}`;
    y = drawCenteredLines(ctx, wrapLines(ctx, c.verdict, W - PAD * 2 - 40, 5), y + 10, 38);

    // ---- 底部 ----
    paintFooter(ctx, '测测你们是绝配还是互怼');

    return canvas;
  }

  async function downloadCompat(mine, theirs, compat, filename) {
    const canvas = await generateCompat(mine, theirs, compat);
    const mType = String((mine && mine.type) || 'me').toLowerCase();
    const tType = String((theirs && theirs.type) || 'ta').toLowerCase();
    const name = filename || `nbti-compat-${mType}-${tType}.png`;
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

  window.NBTIPoster = { generate, download, generateCompat, downloadCompat };
})();
