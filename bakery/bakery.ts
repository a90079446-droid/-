// 새벽 빵집: a baker carries a tray of fresh loaves past the shop window at dawn.
// Steam rises from the chimney and the loaves; the cat on the sill wakes and
// follows the baker with its head. Night slowly turns to morning.
import { el, pen, shape, blot, paint, limb, shoe, place, inkDefs, run, joint, f, PEN, PAPER, type Vec } from './lib/ink.ts';
import { gait } from './lib/gait.ts';
import { spring, pendulum, pointerWind, ease, clamp, smooth, wobble } from './lib/motion.ts';
import { palette, applyPalette, rgb, nightTint } from './lib/daynight.ts';

const W = 480, H = 270, GROUND = 224, SCALE = 0.95;
const q = new URLSearchParams(location.search);
const DAWN = Number(q.get('dawn') ?? 5.5); // second the dawn begins

const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': '새벽 빵집 앞을 지나가는 제빵사와 창가의 고양이 선화 애니메이션' });
const { filter, stripes } = inkDefs(svg, 'b');
document.querySelector('#stage')!.appendChild(svg);

// --- sky gradient (behind the ink filter)
const grad = el('linearGradient', { id: 'sky', x1: 0, y1: 0, x2: 0, y2: 1 }, svg.querySelector('defs')!);
const gTop = el('stop', { offset: 0 }, grad), gBot = el('stop', { offset: 1 }, grad);
el('rect', { x: 0, y: 0, width: W, height: H, fill: 'url(#sky)' }, svg);
const stars = el('g', {}, svg);
const starPts: Vec[] = [[30, 22], [70, 48], [118, 16], [205, 30], [372, 18], [420, 52], [455, 26], [392, 80]];
for (const [x, y] of starPts) el('circle', { cx: x, cy: y, r: 0.8, fill: '#f4ecd6' }, stars);
const moon = el('path', { d: 'M440 40 a11 11 0 1 0 8 18 a9 9 0 1 1 -8 -18Z', fill: '#f4ecd6' }, svg);

const scene = el('g', { filter }, svg);

// --- street
el('rect', { x: 0, y: GROUND, width: W, height: H - GROUND, class: 'pp', fill: PAPER }, scene);
pen(scene, 0.9).setAttribute('d', `M0 ${GROUND} Q240 ${GROUND - 0.6} ${W} ${GROUND} M0 ${GROUND + 10} Q240 ${GROUND + 10.5} ${W} ${GROUND + 10}`);
pen(scene, 0.5).setAttribute('d', Array.from({ length: 16 }, (_, i) => `M${i * 31 + 8} ${GROUND} q0.6 5 0 10`).join(' '));

// --- the shop
const shop = el('g', {}, scene);
const wall = shape(shop, 1.1);
wall.setAttribute('d', `M58 ${GROUND} L60 52 Q200 49 342 52 L344 ${GROUND}Z`);
// roof edge and chimney
pen(shop, 1).setAttribute('d', 'M50 53 Q200 47 352 53 M54 47 Q200 41 348 47');
shape(shop, 1).setAttribute('d', 'M292 47 L293 18 L313 18 L314 46Z');
pen(shop, 0.8).setAttribute('d', 'M289 18 L317 18 M290 14 L316 14 L317 18 M289 18 L290 14');
// brick hints
pen(shop, 0.45).setAttribute('d', 'M70 70 l14 0 M78 76 l12 0 M318 64 l13 0 M325 70 l11 0 M68 200 l12 0 M74 206 l13 0 M322 196 l12 0');
// sign
shape(shop, 1).setAttribute('d', 'M118 60 Q170 57 222 60 L221 80 Q170 82 119 80Z');
const sign = el('text', { x: 170, y: 75, 'text-anchor': 'middle', 'font-family': 'Georgia, serif', 'font-size': 13, 'letter-spacing': 3, fill: 'currentColor' }, shop);
sign.textContent = 'BAKERY';
pen(shop, 0.7).setAttribute('d', 'M134 60 L132 54 M206 60 L208 54');
// window glow + shelves + loaves
const glow = el('path', { d: 'M100 112 L240 112 L240 190 L100 190Z', fill: '#f3c56b' }, shop);
const winFrame = el('path', { d: 'M98 110 Q170 108 242 110 L242 192 L98 192Z', fill: 'none', stroke: 'currentColor', 'stroke-width': 1.2, 'stroke-linejoin': 'round' }, shop);
void winFrame;
pen(shop, 0.8).setAttribute('d', 'M170 110 L170 140 M100 140 Q170 139 240 140 M104 166 Q170 165 236 166');
const loaf = (x: number, y: number, w: number, c = '#d9a25b') => {
  paint(shop, c, 0.9).setAttribute('d', `M${x - w} ${y} Q${x - w} ${y - w * 0.8} ${x} ${y - w * 0.85} Q${x + w} ${y - w * 0.8} ${x + w} ${y}Z`);
  pen(shop, 0.6).setAttribute('d', `M${x - w * 0.4} ${y - w * 0.3} l${w * 0.25} -${w * 0.35} M${x + w * 0.05} ${y - w * 0.25} l${w * 0.25} -${w * 0.35}`);
};
[112, 128, 146, 192, 210, 226].forEach((x, i) => loaf(x, 139.4, i % 3 === 1 ? 7 : 6));
[116, 134, 152].forEach((x) => loaf(x, 165.4, 7, '#c98d48'));
// croissants on the lower right shelf
[[190, 165], [208, 165]].forEach(([x, y]) => paint(shop, '#e0ab62', 0.9).setAttribute('d', `M${x - 8} ${y} Q${x} ${y - 11} ${x + 8} ${y} Q${x + 4} ${y - 3} ${x} ${y - 3} Q${x - 4} ${y - 3} ${x - 8} ${y}Z`));
// sill
shape(shop, 1).setAttribute('d', 'M94 192 L246 192 L248 198 L92 198Z');
// awning with stripes and scallops
const awning = el('g', {}, shop);
el('path', { d: 'M92 88 L248 88 L256 104 L84 104Z', fill: stripes, stroke: 'currentColor', 'stroke-width': 1, 'stroke-linejoin': 'round' }, awning);
pen(awning, 1).setAttribute('d', 'M84 104' + Array.from({ length: 10 }, (_, i) => ` q8.6 7 17.2 0`).join(''));
// door
shape(shop, 1.1).setAttribute('d', `M268 ${GROUND} L268 106 Q294 102 320 106 L320 ${GROUND}`);
const doorGlow = el('path', { d: 'M276 116 Q294 113 312 116 L312 150 L276 150Z', fill: '#f3c56b' }, shop);
pen(shop, 0.8).setAttribute('d', 'M276 116 Q294 113 312 116 L312 150 L276 150Z M294 114 L294 150');
blot(shop).setAttribute('d', 'M311 168 a2 2 0 1 0 0.1 0Z');
// hanging bread sign on a bracket (swings)
pen(shop, 0.9).setAttribute('d', 'M342 92 L370 92 M346 92 L346 98');
const hangSign = el('g', {}, shop);
const hangSwing = pendulum(9, 0.8);

// lamp post
const post = el('g', {}, scene);
shape(post, 0.9).setAttribute('d', `M415 ${GROUND} L417 96 L421 96 L423 ${GROUND}Z`);
shape(post, 0.9).setAttribute('d', 'M408 96 L430 96 L426 80 L412 80Z');
const lampGlow = el('circle', { cx: 419, cy: 90, r: 24, fill: '#f3c56b' }, svg);
svg.insertBefore(lampGlow, scene);

// --- steam (chimney and tray)
type Wisp = { node: SVGPathElement; off: number };
const wisps = (parent: Element, n: number, w: number): Wisp[] =>
  Array.from({ length: n }, (_, i) => ({ node: pen(parent, w), off: i / n }));
const chimSteam = wisps(scene, 7, 1.1);
function drawSteam(ws: Wisp[], t: number, base: Vec, life: number, rise: number, spread: number, drift: number) {
  for (const s of ws) {
    const u = ((t / life) + s.off) % 1;
    const y0 = base[1] - u * rise, x0 = base[0] + drift * u * u * rise + wobble(t * 0.7 + s.off * 9) * spread * u;
    const len = 9 + 14 * u, a = Math.sin(t * 1.3 + s.off * 7) * (2 + 4 * u);
    s.node.setAttribute('d', `M${f(x0)} ${f(y0)} q${f(a)} ${f(-len * 0.5)} 0 ${f(-len)} q${f(-a)} ${f(-len * 0.5)} 0 ${f(-len)}`);
    s.node.setAttribute('stroke-opacity', f(smooth(0, 0.15, u) * (1 - smooth(0.55, 1, u))));
  }
}

// --- the cat on the sill (inside the window, in front of the shelves)
const cat = el('g', {}, shop);
const catTail = pen(cat, 1.2);
const catBody = shape(cat, 1.1);
const catHead = el('g', {}, cat);
const catFace = shape(catHead, 1.1);
const catEyes = pen(catHead, 0.8);
const tailSpring = spring(18, 3);
const CAT: Vec = [214, 192];

// --- the baker (figure space: feet on y 120, facing +x, ~95 tall)
const fig = el('g', {}, scene);
const farArm = limb(fig, 3.8);
const legs = [limb(fig, 4.4), limb(fig, 4.4)];
const shoes = [blot(fig), blot(fig)];
const apron = shape(fig);
const apronTie = pen(fig, PEN * 0.7);
const head = el('ellipse', { rx: 4, ry: 4.8, fill: PAPER, class: 'pp', stroke: 'currentColor', 'stroke-width': PEN }, fig);
const hat = shape(fig);
const hatBand = pen(fig, PEN * 0.7);
const nose = pen(fig, PEN * 0.7);
const trayG = el('g', {}, fig);
const tray = paint(trayG, '#8a6a4a', PEN * 0.8);
const trayLoaves = [paint(trayG, '#d9a25b', PEN * 0.7), paint(trayG, '#c98d48', PEN * 0.7), paint(trayG, '#d9a25b', PEN * 0.7)];
const trayScores = pen(trayG, PEN * 0.5);
const nearArm = limb(fig, 3.8);
const traySteamG = el('g', {}, scene);
const traySteam = wisps(traySteamG, 4, 0.8);

const walk = gait({ kind: 'walk' });
const wind = pointerWind(svg, 0.15);
const trayTilt = spring(50, 7);
let phase = 0, x = -30;

run((t, dt) => {
  wind.step(t);
  // --- light: night → dawn → morning
  // hold the night, then a quick dawn (the mid-dawn palette has little ink contrast)
  const tau = 0.2 + 0.11 * ease(clamp((t - DAWN) / 2.5, 0, 1));
  const P = palette(tau);
  applyPalette(svg, P);
  gTop.setAttribute('stop-color', rgb(P.top)); gBot.setAttribute('stop-color', rgb(P.bottom));
  stars.setAttribute('opacity', f(P.night)); moon.setAttribute('opacity', f(P.night * 0.9));
  glow.setAttribute('opacity', f(0.25 + 0.55 * P.lamp)); doorGlow.setAttribute('opacity', f(0.2 + 0.5 * P.lamp));
  lampGlow.setAttribute('opacity', f(0.35 * smooth(0.5, 0.9, P.lamp)));
  wall.setAttribute('fill', nightTint('#efe2cf', P, 0.7));
  wall.classList.remove('pp');

  // --- hanging sign swings in the wind
  const ha = hangSwing.step(-wind.value * 0.6 + wobble(t * 0.6) * 0.15, dt);
  hangSign.setAttribute('transform', `rotate(${f(ha * 57.3)} 358 92)`);
  if (!hangSign.firstChild) {
    pen(hangSign, 0.7).setAttribute('d', 'M352 92 L350 100 M364 92 L366 100');
    paint(hangSign, '#e7d3b0', 0.9).setAttribute('d', 'M346 100 Q358 97 370 100 L369 118 Q358 120 347 118Z');
    paint(hangSign, '#d9a25b', 0.8).setAttribute('d', 'M350 113 Q350 104 358 104 Q366 104 366 113Z');
    pen(hangSign, 0.5).setAttribute('d', 'M355 109 l2 -3 M360 109 l2 -3');
  }

  // --- chimney steam (the oven is on)
  drawSteam(chimSteam, t, [303, 14], 4, 60, 8, 0.25 + wind.value * 0.4);

  // --- baker walks on planted feet
  phase += dt / walk.period;
  x += walk.speed * SCALE * dt;
  if (x > W + 60) x = -60;
  place(fig, x, GROUND, 1, SCALE);
  const p = walk.pose(phase);
  const b = p.bob;
  p.feet.forEach((fo, i) => { legs[i].draw([p.hip, fo.knee, fo.ankle], [0.3, 0.8]); shoe(shoes[i], fo.ankle, fo.pitch); });
  fig.insertBefore(legs[p.front].g, apron); fig.insertBefore(shoes[p.front], apron);

  // white coat + apron, hem follows the forward knee
  const kF = p.feet[p.front].knee, aF = p.feet[p.front].ankle;
  const sh: Vec = [41, 41 + b], hemY = 90;
  const fx = Math.max(kF[0] + 2.6, 47);
  apron.setAttribute('d', `M${f(sh[0] - 7)} ${f(sh[1] + 1)} Q${f(sh[0])} ${f(sh[1] - 2.6)} ${f(sh[0] + 6)} ${f(sh[1] + 1)} Q${f(sh[0] + 9)} ${f(56 + b)} ${f(fx - 0.4)} ${f(72 + b)} Q${f(fx + 0.4)} ${f(82 + b * 0.5)} ${f(Math.max(fx, aF[0] - 4))} ${hemY} L${f(31)} ${hemY + 1} Q${f(31.5)} ${f(70 + b)} ${f(33)} ${f(62 + b)}Z`);
  apronTie.setAttribute('d', `M${f(33.4)} ${f(62 + b)} Q${f(40)} ${f(63.6 + b)} ${f(fx - 2)} ${f(62 + b)} M${f(34)} ${f(62 + b)} q-4 2 -5 6`);

  // head and tall baker's hat
  const hc: Vec = [43, 31 + b];
  head.setAttribute('cx', f(hc[0])); head.setAttribute('cy', f(hc[1]));
  nose.setAttribute('d', `M${f(hc[0] + 3.8)} ${f(hc[1] - 0.4)} q1.6 1.2 0 2`);
  const hy = hc[1] - 4.2;
  hat.setAttribute('d', `M${f(hc[0] - 4.6)} ${f(hy)} L${f(hc[0] - 5.4)} ${f(hy - 6)} Q${f(hc[0] - 9)} ${f(hy - 10)} ${f(hc[0] - 4)} ${f(hy - 13)} Q${f(hc[0])} ${f(hy - 17)} ${f(hc[0] + 4)} ${f(hy - 13)} Q${f(hc[0] + 9)} ${f(hy - 10)} ${f(hc[0] + 5.4)} ${f(hy - 6)} L${f(hc[0] + 4.6)} ${f(hy)}Z`);
  hatBand.setAttribute('d', `M${f(hc[0] - 5.2)} ${f(hy - 3)} Q${f(hc[0])} ${f(hy - 2)} ${f(hc[0] + 5.2)} ${f(hy - 3)}`);

  // tray held out in front at chest height; it lags the bob a little through a spring
  const tilt = trayTilt.step(-p.bob * 1.2 + wind.value * 0.4, dt);
  const T: Vec = [60, 54 + b * 0.6];
  trayG.setAttribute('transform', `rotate(${f(tilt)} ${f(T[0])} ${f(T[1])})`);
  tray.setAttribute('d', `M${f(T[0] - 15)} ${f(T[1])} L${f(T[0] + 15)} ${f(T[1])} L${f(T[0] + 13.5)} ${f(T[1] + 2.4)} L${f(T[0] - 13.5)} ${f(T[1] + 2.4)}Z`);
  const lx = [-9, 0, 9];
  trayLoaves.forEach((n, i) => { const c = T[0] + lx[i], w = i === 1 ? 5.4 : 4.6; n.setAttribute('d', `M${f(c - w)} ${f(T[1])} Q${f(c - w)} ${f(T[1] - w)} ${f(c)} ${f(T[1] - w * 1.05)} Q${f(c + w)} ${f(T[1] - w)} ${f(c + w)} ${f(T[1])}Z`); });
  trayScores.setAttribute('d', lx.map((d) => `M${f(T[0] + d - 2)} ${f(T[1] - 2)} l1.4 -2`).join(' '));
  // both hands under the tray rim; elbows from two-bone IK (bend backward)
  const shF: Vec = [sh[0] - 0.5, sh[1] + 2.2], shN: Vec = [sh[0] + 2, sh[1] + 2.6];
  const hF: Vec = [T[0] - 9, T[1] + 2.4], hN: Vec = [T[0] + 5, T[1] + 2.6];
  farArm.draw([shF, joint(shF, hF, 15, 15, -1), hF], [0.2, 0.5]);
  nearArm.draw([shN, joint(shN, hN, 15, 15, -1), hN], [0.2, 0.4]);
  // fresh-bread steam above the tray, in scene coordinates
  const tsx = x + SCALE * (T[0] - 40), tsy = GROUND + SCALE * (T[1] - 6 - 120);
  drawSteam(traySteam, t, [tsx, tsy], 1.6, 18, 2, -0.6);

  // --- cat: asleep, wakes as the baker nears, follows him with its head
  const near = smooth(30, 120, x) * (1 - smooth(300, 380, x));
  const awake = ease(clamp((x - 40) / 50, 0, 1)) * (1 - smooth(330, 400, x));
  const look = clamp((x + 20 - CAT[0]) / 120, -1, 1) * awake; // −1 left … +1 right
  const breathe = Math.sin(t * 2 * Math.PI / 3.4) * 0.5 * (1 - awake * 0.6);
  const [cx, cy] = CAT;
  catBody.setAttribute('d', `M${cx - 13} ${cy} Q${cx - 15} ${f(cy - 10 - breathe)} ${cx - 6} ${f(cy - 13 - breathe)} Q${cx + 2} ${f(cy - 15 - breathe - awake * 3)} ${cx + 8} ${f(cy - 9 - awake * 4)} Q${cx + 11} ${cy - 3} ${cx + 10} ${cy}Z`);
  const tailTip = tailSpring.step(wobble(t * 0.8) * (4 + 6 * awake) + near * 3, dt);
  catTail.setAttribute('d', `M${cx - 12} ${cy - 1} Q${cx - 22} ${cy} ${f(cx - 24 + tailTip * 0.3)} ${f(cy - 6 - tailTip * 0.2)} Q${f(cx - 26 + tailTip)} ${f(cy - 13)} ${f(cx - 20 + tailTip)} ${f(cy - 15 - tailTip * 0.3)}`);
  // head: lies low when asleep, lifts and turns when awake
  const hx = cx + 9 + look * 1.5, hyC = cy - 9 - awake * 9;
  catHead.setAttribute('transform', `translate(${f(hx)} ${f(hyC)}) rotate(${f(look * 12 - (1 - awake) * 18)})`);
  catFace.setAttribute('d', 'M-6 0 Q-6.4 -5 -4.6 -6 L-4.4 -10.4 L-1.6 -6.8 Q0 -7.3 1.6 -6.8 L4.4 -10.4 L4.6 -6 Q6.4 -5 6 0 Q0 4.8 -6 0Z');
  if (awake < 0.35) catEyes.setAttribute('d', 'M-3.6 -2.2 q1.2 1 2.4 0 M1.2 -2.2 q1.2 1 2.4 0');
  else { const e = look * 0.9; catEyes.setAttribute('d', `M${f(-2.6 + e)} -3 l0 1.6 M${f(2.2 + e)} -3 l0 1.6 M-1 0.4 l1 0.6 l1 -0.6`); }
});
