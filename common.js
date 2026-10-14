/* ============================================================
   R3D Flashcards — shared engine (all pages)
   i18n (ar/zh/en/es/fr) + review state machine + quiz engine
   + iOS-safe audio + lazy lesson-audio fetch.
   Loaded AFTER data.js.
   ============================================================ */
(function () {
'use strict';

// ---------------- storage ----------------
const LS = {
  get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};
const KEY = {
  lang: 'r3d-lang',
  review: 'r3d-review',                 // { 'l1:12': {s:'review'|'mastered', n:streak} }
  quiz: 'r3d-quiz',                     // { l1: {score,total,at} }
  meta: 'r3d-meta',                     // { 'quiz-l1': true }
  marks: l => 'r3d-marks-' + l,
  mig: l => 'r3d-mig-' + l
};

// ---------------- i18n ----------------
const I18N = {
  ar: {
    __name: 'العربية',
    'app.sub': '✅ نسخة الجوال · اضغط لتقلب · تعمل بدون إنترنت',
    'stats.progress': 'تقدم', 'stats.know': 'أعرفها', 'stats.review': 'أراجعها',
    'cat.all': 'الكل', 'cat.word': 'كلمات', 'cat.sent': 'جمل مفتاحية', 'cat.gram': 'قواعد',
    'tag.word': 'كلمة', 'tag.sent': 'جملة مفتاحية', 'tag.gram': 'قاعدة',
    'hint.flip': 'اضغط للقلب ↻ · 🔊 للنطق',
    'btn.listen': 'استمع', 'btn.example': 'المثال',
    'btn.prev': '‹ السابق', 'btn.know': '✓ أعرفها', 'btn.dunno': '✗ أراجعها', 'btn.next': 'التالي ›',
    'tool.shuffle': '🔀 خلط', 'tool.reset': '♻️ تصفير التقدم', 'tool.quiz': '📝 اختبار الدرس',
    'done.title': 'أحسنت! خلّصت كل البطاقات',
    'done.quiz': '📝 ابدأ اختبار الدرس',
    'footer.tts': 'نطق الكلمات: تحت الحرف الصيني بالبينيين مع علامات النغمات',
    'quiz.title': 'اختبار الدرس', 'quiz.progress': 'سؤال {n} من {total}',
    'quiz.dirZh': 'اختر المعنى الصحيح', 'quiz.dirAr': 'اختر الكلمة الصحيحة',
    'quiz.correct': '✅ صحيح!', 'quiz.wrong': '❌ خطأ — الصحيح: {x}',
    'quiz.score': 'نتيجتك: {s} / {t}', 'quiz.resultTitle': 'انتهى الاختبار',
    'quiz.wrongNote': '{n} كلمة دخلت مجموعة المراجعة تلقائياً',
    'quiz.again': '🔁 إعادة الاختبار', 'quiz.close': 'إغلاق',
    'confirm.reset': 'تصفير كل تقدم هذا الدرس؟',
    'lang.label': 'اللغة',
    'nav.index': '🏠 الرئيسية', 'nav.review': '📒 المراجعة',
    'index.title': 'بطاقات الاستذكار', 'index.sub': 'اضغط على الدرس — يعمل بدون إنترنت',
    'index.reviewBtn': '📒 مجموعة المراجعة',
    'index.reviewCount': '{n} كلمة للمراجعة', 'index.mastered': 'محكمة: {n}',
    'index.progress': 'التقدم: {p}%', 'index.quizScore': 'الاختبار: {s}/{t}',
    'index.noQuiz': 'ما اختبرت بعد', 'index.tip': '💡 في سفاري: زر المشاركة ← «إضافة إلى الشاشة الرئيسية»',
    'review.title': 'مجموعة المراجعة',
    'review.empty': 'ما فيه كلمات للمراجعة 🎉',
    'review.emptyTxt': 'كل الكلمات إما جديدة أو محكمة — اضغط ✗ على أي كلمة في الدروس ترجع هنا.',
    'review.remaining': 'للمراجعة: {n}', 'review.mastered': 'محكمة: {n}',
    'review.hint': 'اضغط للقلب ↻ · 🔊 للنطق',
    'review.know': '✓ أعرفها', 'review.dunno': '✗ لسه أراجعها',
    'review.back': '← رجوع', 'review.masteredToast': 'أصبحت محكمة ✅',
    'review.streak': 'إجابات صحيحة متتالية: {n}/2'
  },
  zh: {
    __name: '中文',
    'app.sub': '✅ 手机版 · 点击翻面 · 离线可用',
    'stats.progress': '进度', 'stats.know': '已掌握', 'stats.review': '待复习',
    'cat.all': '全部', 'cat.word': '生词', 'cat.sent': '重点句', 'cat.gram': '语法',
    'tag.word': '生词', 'tag.sent': '重点句', 'tag.gram': '语法',
    'hint.flip': '点击翻面 ↻ · 🔊 发音',
    'btn.listen': '发音', 'btn.example': '例句',
    'btn.prev': '‹ 上一个', 'btn.know': '✓ 已掌握', 'btn.dunno': '✗ 待复习', 'btn.next': '下一个 ›',
    'tool.shuffle': '🔀 随机', 'tool.reset': '♻️ 重置进度', 'tool.quiz': '📝 本课测验',
    'done.title': '太棒了！全部完成',
    'done.quiz': '📝 开始本课测验',
    'footer.tts': '发音：汉字下方为拼音（带声调）',
    'quiz.title': '本课测验', 'quiz.progress': '第 {n} / {total} 题',
    'quiz.dirZh': '选择正确的意思', 'quiz.dirAr': '选择正确的词语',
    'quiz.correct': '✅ 正确！', 'quiz.wrong': '❌ 错误 — 正确答案：{x}',
    'quiz.score': '得分：{s} / {t}', 'quiz.resultTitle': '测验结束',
    'quiz.wrongNote': '{n} 个词已自动加入复习集',
    'quiz.again': '🔁 再测一次', 'quiz.close': '关闭',
    'confirm.reset': '重置本课全部进度？',
    'lang.label': '语言',
    'nav.index': '🏠 首页', 'nav.review': '📒 复习',
    'index.title': '记忆卡片', 'index.sub': '点击课程 — 离线可用',
    'index.reviewBtn': '📒 复习集',
    'index.reviewCount': '{n} 个待复习', 'index.mastered': '已掌握：{n}',
    'index.progress': '进度：{p}%', 'index.quizScore': '测验：{s}/{t}',
    'index.noQuiz': '尚未测验', 'index.tip': '💡 Safari：分享按钮 ← “添加到主屏幕”',
    'review.title': '复习集',
    'review.empty': '没有待复习的词 🎉',
    'review.emptyTxt': '所有词都是新的或已掌握 — 在课程中按 ✗ 的词会回到这里。',
    'review.remaining': '待复习：{n}', 'review.mastered': '已掌握：{n}',
    'review.hint': '点击翻面 ↻ · 🔊 发音',
    'review.know': '✓ 已掌握', 'review.dunno': '✗ 仍需复习',
    'review.back': '← 返回', 'review.masteredToast': '已掌握 ✅',
    'review.streak': '连续答对：{n}/2'
  },
  en: {
    __name: 'English',
    'app.sub': '✅ Mobile version · tap to flip · works offline',
    'stats.progress': 'Progress', 'stats.know': 'Known', 'stats.review': 'Review',
    'cat.all': 'All', 'cat.word': 'Words', 'cat.sent': 'Key sentences', 'cat.gram': 'Grammar',
    'tag.word': 'Word', 'tag.sent': 'Key sentence', 'tag.gram': 'Grammar',
    'hint.flip': 'Tap to flip ↻ · 🔊 to play',
    'btn.listen': 'Listen', 'btn.example': 'Example',
    'btn.prev': '‹ Prev', 'btn.know': '✓ Know it', 'btn.dunno': '✗ Review', 'btn.next': 'Next ›',
    'tool.shuffle': '🔀 Shuffle', 'tool.reset': '♻️ Reset progress', 'tool.quiz': '📝 Lesson quiz',
    'done.title': 'Nice! You finished all cards',
    'done.quiz': '📝 Start the lesson quiz',
    'footer.tts': 'Pronunciation: pinyin with tones under each character',
    'quiz.title': 'Lesson quiz', 'quiz.progress': 'Question {n} of {total}',
    'quiz.dirZh': 'Choose the correct meaning', 'quiz.dirAr': 'Choose the correct word',
    'quiz.correct': '✅ Correct!', 'quiz.wrong': '❌ Wrong — correct: {x}',
    'quiz.score': 'Your score: {s} / {t}', 'quiz.resultTitle': 'Quiz complete',
    'quiz.wrongNote': '{n} word(s) added to the review set',
    'quiz.again': '🔁 Retry quiz', 'quiz.close': 'Close',
    'confirm.reset': 'Reset all progress for this lesson?',
    'lang.label': 'Language',
    'nav.index': '🏠 Home', 'nav.review': '📒 Review',
    'index.title': 'Flashcards', 'index.sub': 'Pick a lesson — works offline',
    'index.reviewBtn': '📒 Review set',
    'index.reviewCount': '{n} to review', 'index.mastered': 'Mastered: {n}',
    'index.progress': 'Progress: {p}%', 'index.quizScore': 'Quiz: {s}/{t}',
    'index.noQuiz': 'Not taken yet', 'index.tip': '💡 Safari: share button ← “Add to Home Screen”',
    'review.title': 'Review set',
    'review.empty': 'Nothing to review 🎉',
    'review.emptyTxt': 'All words are either new or mastered — mark any word ✗ in a lesson to bring it back here.',
    'review.remaining': 'To review: {n}', 'review.mastered': 'Mastered: {n}',
    'review.hint': 'Tap to flip ↻ · 🔊 to play',
    'review.know': '✓ Know it', 'review.dunno': '✗ Still reviewing',
    'review.back': '← Back', 'review.masteredToast': 'Mastered ✅',
    'review.streak': 'Consecutive correct: {n}/2'
  },
  es: {
    __name: 'Español',
    'app.sub': '✅ Versión móvil · toca para girar · funciona sin internet',
    'stats.progress': 'Progreso', 'stats.know': 'Sabidas', 'stats.review': 'Repasar',
    'cat.all': 'Todas', 'cat.word': 'Palabras', 'cat.sent': 'Frases clave', 'cat.gram': 'Gramática',
    'tag.word': 'Palabra', 'tag.sent': 'Frase clave', 'tag.gram': 'Gramática',
    'hint.flip': 'Toca para girar ↻ · 🔊 para escuchar',
    'btn.listen': 'Escuchar', 'btn.example': 'Ejemplo',
    'btn.prev': '‹ Anterior', 'btn.know': '✓ La sé', 'btn.dunno': '✗ Repasar', 'btn.next': 'Siguiente ›',
    'tool.shuffle': '🔀 Mezclar', 'tool.reset': '♻️ Reiniciar', 'tool.quiz': '📝 Quiz de la lección',
    'done.title': '¡Genial! Completaste todas las tarjetas',
    'done.quiz': '📝 Empezar el quiz de la lección',
    'footer.tts': 'Pronunciación: pinyin con tonos bajo cada carácter',
    'quiz.title': 'Quiz de la lección', 'quiz.progress': 'Pregunta {n} de {total}',
    'quiz.dirZh': 'Elige el significado correcto', 'quiz.dirAr': 'Elige la palabra correcta',
    'quiz.correct': '✅ ¡Correcto!', 'quiz.wrong': '❌ Incorrecto — correcto: {x}',
    'quiz.score': 'Tu puntuación: {s} / {t}', 'quiz.resultTitle': 'Quiz terminado',
    'quiz.wrongNote': '{n} palabra(s) añadidas a la lista de repaso',
    'quiz.again': '🔁 Repetir quiz', 'quiz.close': 'Cerrar',
    'confirm.reset': '¿Reiniciar todo el progreso de esta lección?',
    'lang.label': 'Idioma',
    'nav.index': '🏠 Inicio', 'nav.review': '📒 Repaso',
    'index.title': 'Tarjetas', 'index.sub': 'Elige una lección — funciona sin internet',
    'index.reviewBtn': '📒 Lista de repaso',
    'index.reviewCount': '{n} por repasar', 'index.mastered': 'Dominadas: {n}',
    'index.progress': 'Progreso: {p}%', 'index.quizScore': 'Quiz: {s}/{t}',
    'index.noQuiz': 'Aún sin hacer', 'index.tip': '💡 Safari: botón compartir ← “Añadir a pantalla de inicio”',
    'review.title': 'Lista de repaso',
    'review.empty': 'Nada que repasar 🎉',
    'review.emptyTxt': 'Todas las palabras son nuevas o están dominadas — marca cualquier palabra ✗ en una lección para traerla aquí.',
    'review.remaining': 'Por repasar: {n}', 'review.mastered': 'Dominadas: {n}',
    'review.hint': 'Toca para girar ↻ · 🔊 para escuchar',
    'review.know': '✓ La sé', 'review.dunno': '✗ Sigo repasando',
    'review.back': '← Volver', 'review.masteredToast': 'Dominada ✅',
    'review.streak': 'Correctas seguidas: {n}/2'
  },
  fr: {
    __name: 'Français',
    'app.sub': '✅ Version mobile · appuyez pour retourner · fonctionne hors ligne',
    'stats.progress': 'Progression', 'stats.know': 'Su', 'stats.review': 'À revoir',
    'cat.all': 'Tout', 'cat.word': 'Mots', 'cat.sent': 'Phrases clés', 'cat.gram': 'Grammaire',
    'tag.word': 'Mot', 'tag.sent': 'Phrase clé', 'tag.gram': 'Grammaire',
    'hint.flip': 'Appuyez pour retourner ↻ · 🔊 pour écouter',
    'btn.listen': 'Écouter', 'btn.example': 'Exemple',
    'btn.prev': '‹ Précédent', 'btn.know': '✓ Je sais', 'btn.dunno': '✗ À revoir', 'btn.next': 'Suivant ›',
    'tool.shuffle': '🔀 Mélanger', 'tool.reset': '♻️ Réinitialiser', 'tool.quiz': '📝 Quiz de la leçon',
    'done.title': 'Bravo ! Vous avez terminé toutes les cartes',
    'done.quiz': '📝 Commencer le quiz de la leçon',
    'footer.tts': 'Prononciation : pinyin avec tons sous chaque caractère',
    'quiz.title': 'Quiz de la leçon', 'quiz.progress': 'Question {n} sur {total}',
    'quiz.dirZh': 'Choisissez le bon sens', 'quiz.dirAr': 'Choisissez le bon mot',
    'quiz.correct': '✅ Correct !', 'quiz.wrong': '❌ Faux — correct : {x}',
    'quiz.score': 'Votre score : {s} / {t}', 'quiz.resultTitle': 'Quiz terminé',
    'quiz.wrongNote': '{n} mot(s) ajouté(s) à la liste de révision',
    'quiz.again': '🔁 Recommencer', 'quiz.close': 'Fermer',
    'confirm.reset': 'Réinitialiser toute la progression de cette leçon ?',
    'lang.label': 'Langue',
    'nav.index': '🏠 Accueil', 'nav.review': '📒 Révision',
    'index.title': 'Cartes', 'index.sub': 'Choisissez une leçon — fonctionne hors ligne',
    'index.reviewBtn': '📒 Liste de révision',
    'index.reviewCount': '{n} à réviser', 'index.mastered': 'Maîtrisés : {n}',
    'index.progress': 'Progression : {p}%', 'index.quizScore': 'Quiz : {s}/{t}',
    'index.noQuiz': 'Pas encore fait', 'index.tip': '💡 Safari : bouton partager ← “Sur l\'écran d\'accueil”',
    'review.title': 'Liste de révision',
    'review.empty': 'Rien à réviser 🎉',
    'review.emptyTxt': 'Tous les mots sont nouveaux ou maîtrisés — marquez n\'importe quel mot ✗ dans une leçon pour le ramener ici.',
    'review.remaining': 'À réviser : {n}', 'review.mastered': 'Maîtrisés : {n}',
    'review.hint': 'Appuyez pour retourner ↻ · 🔊 pour écouter',
    'review.know': '✓ Je sais', 'review.dunno': '✗ Je révise encore',
    'review.back': '← Retour', 'review.masteredToast': 'Maîtrisé ✅',
    'review.streak': 'Bonnes réponses d\'affilée : {n}/2'
  }
};
const LANGS = ['ar', 'zh', 'en', 'es', 'fr'];
let lang = LS.get(KEY.lang, 'ar');
if (!I18N[lang]) lang = 'ar';

// ---- authoritative translations lookup, built from data.js (R3D_DATA) ----
const GLOSS_LOOKUP = Object.create(null);
const TYPE_LOOKUP  = Object.create(null);
const SUB_LOOKUP   = Object.create(null);
(function buildLookups() {
  const all = window.R3D_DATA && window.R3D_DATA.cards;
  if (!all) return;
  for (const key in all) {
    const arr = all[key];
    for (const c of arr) {
      const ar = c.ar || '';
      if (ar && !(ar in GLOSS_LOOKUP)) GLOSS_LOOKUP[ar] = c.trans || {};
      const t = c.trans_type || {};
      if (c.type && !(c.type in TYPE_LOOKUP)) TYPE_LOOKUP[c.type] = t;
      const s = c.trans_sub || {};
      if (c.sub && !(c.sub in SUB_LOOKUP)) SUB_LOOKUP[c.sub] = s;
    }
  }
})();

function t(key, vars) {
  let s = (I18N[lang] && I18N[lang][key]) || (I18N.ar[key] || key);
  if (vars) for (const k in vars) s = s.split('{' + k + '}').join(String(vars[k]));
  return s;
}
function setLang(l) { if (!I18N[l]) return; lang = l; LS.set(KEY.lang, l); applyI18n(); }
// card gloss in the current UI language (falls back to Arabic, then English)
function gloss(card) {
  if (!card) return '';
  const tr = card.trans || {};
  if (tr[lang]) return tr[lang];
  if (tr.en) return tr.en;
  const found = GLOSS_LOOKUP[card.ar || ''];
  if (found && found[lang]) return found[lang];
  return card.ar || '';
}
function glossOf(front, lessonId) {
  const cards = (window.R3D_DATA && window.R3D_DATA.cards[lessonId]) || [];
  const c = cards.find(x => x.front === front);
  return c ? gloss(c) : '';
}
function cardType(card) {
  if (!card) return '';
  const tr = card.trans_type || {};
  if (tr[lang]) return tr[lang];
  const found = TYPE_LOOKUP[card.type || ''];
  if (found && found[lang]) return found[lang];
  return card.type || '';
}
function cardSub(card) {
  if (!card) return '';
  const tr = card.trans_sub || {};
  if (tr[lang]) return tr[lang];
  const found = SUB_LOOKUP[card.sub || ''];
  if (found && found[lang]) return found[lang];
  return card.sub || '';
}
function applyI18n() {
  document.documentElement.lang = lang;
  document.documentElement.dir = (lang === 'ar') ? 'rtl' : 'ltr';
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.getAttribute('data-i18n')); });
  document.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.getAttribute('data-i18n-title')); });
  const sel = document.getElementById('langSel');
  if (sel) sel.value = lang;
  window.dispatchEvent(new CustomEvent('r3d:lang', { detail: { lang: lang } }));
}
function mountLangSelector() {
  const box = document.getElementById('langBox');
  if (!box) return;
  box.innerHTML = '';
  const lab = document.createElement('span');
  lab.className = 'langlab'; lab.setAttribute('data-i18n', 'lang.label');
  const sel = document.createElement('select');
  sel.id = 'langSel';
  LANGS.forEach(l => {
    const o = document.createElement('option');
    o.value = l; o.textContent = I18N[l].__name || l;
    sel.appendChild(o);
  });
  sel.value = lang;
  sel.addEventListener('change', () => setLang(sel.value));
  box.appendChild(lab); box.appendChild(sel);
}

// ---------------- review state machine ----------------
// key format: 'lN:<cardIndex>'  |  state: new -> review -> mastered
// mastered = 2 consecutive correct answers (in review or quiz).
function reviewAll() { return LS.get(KEY.review, {}) || {}; }
function reviewGet(key) { const r = reviewAll(); return r[key] || { s: 'new', n: 0 }; }
function reviewSet(key, state, n) {
  const r = reviewAll();
  if (!state || state === 'new') {
    // a 'new' card can still carry a correct-answer streak without joining
    // the review set (only explicit ✗ or a quiz mistake puts it there)
    if (n) r[key] = { s: 'new', n: n };
    else delete r[key];
  } else r[key] = { s: state, n: n || 0 };
  LS.set(KEY.review, r);
  window.dispatchEvent(new CustomEvent('r3d:review'));
}
function reviewCount() { const r = reviewAll(); return Object.keys(r).filter(k => r[k].s === 'review').length; }
function masteredCount() { const r = reviewAll(); return Object.keys(r).filter(k => r[k].s === 'mastered').length; }
function answerCorrect(key) {
  const cur = reviewGet(key);
  if (cur.s === 'mastered') return 'mastered';
  const n = cur.n + 1;
  if (n >= 2) { reviewSet(key, 'mastered', n); return 'mastered'; }
  if (cur.s === 'review') { reviewSet(key, 'review', n); return 'review'; }
  reviewSet(key, 'new', n);      // new card: streak tracked, stays out of the review set
  return 'new';
}
function answerWrong(key) { reviewSet(key, 'review', 0); return 'review'; }
function parseKey(key) { const i = key.indexOf(':'); return { lesson: key.slice(0, i), idx: parseInt(key.slice(i + 1), 10) }; }
function cardByKey(key) {
  const p = parseKey(key);
  const meta = (window.R3D_DATA.lessons || []).find(l => l.id === p.lesson);
  const arr = window.R3D_DATA.cards[p.lesson];
  const card = arr && arr[p.idx];
  if (!meta || !card) return null;
  return { lesson: meta, idx: p.idx, card: card, key: key };
}

// ---------------- audio ----------------
const _blobs = {};
const curAudio = new Audio();
curAudio.preload = 'auto';
function blobUrl(uri) {
  if (_blobs[uri]) return _blobs[uri];
  try {
    const b64 = uri.split(',')[1] || '';
    const bin = atob(b64);
    const buf = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    _blobs[uri] = URL.createObjectURL(new Blob([buf], { type: 'audio/mpeg' }));
  } catch (e) { _blobs[uri] = uri; }
  return _blobs[uri];
}
let primed = false;
function primeAudio(uri) {
  if (primed || !uri) return;
  primed = true;
  try {
    curAudio.muted = true;
    curAudio.src = blobUrl(uri);
    const p = curAudio.play();
    if (p && p.catch) p.catch(function () {});
    curAudio.muted = false;
  } catch (e) {}
}
function play(uri) {
  if (!uri) return;
  try {
    curAudio.pause();
    curAudio.src = blobUrl(uri);
    curAudio.currentTime = 0;
    const p = curAudio.play();
    if (p && p.catch) p.catch(function () {});
  } catch (e) {}
}
// lazy: fetch the lesson file once, pull the card's audio data URI
const _lessonCache = {};
async function lessonAudio(lessonId, idx) {
  if (!_lessonCache[lessonId]) {
    const meta = (window.R3D_DATA.lessons || []).find(l => l.id === lessonId);
    if (!meta) return '';
    try {
      const html = await (await fetch(meta.file)).text();
      const m = html.match(/const CARDS = (\[[\s\S]*?\]);/);
      _lessonCache[lessonId] = m ? JSON.parse(m[1]) : [];
    } catch (e) { _lessonCache[lessonId] = []; }
  }
  const c = _lessonCache[lessonId][idx];
  return c ? (c.au || '') : '';
}
async function playCard(key) {
  const p = parseKey(key);
  const uri = await lessonAudio(p.lesson, p.idx);
  if (uri) play(uri);
}

// ---------------- marks (per lesson, original-index keyed) ----------------
const Marks = {
  load(l) { return LS.get(KEY.marks(l), {}) || {}; },
  save(l, m) { LS.set(KEY.marks(l), m); },
  migrate(l, cards) {   // cards: in-page CARDS array; one-time legacy migration
    if (LS.get(KEY.mig(l))) return LS.get(KEY.marks(l), {}) || {};
    const legacyKey = 'l' + String(l).slice(1) + '-marks';   // e.g. l1-marks
    const old = LS.get(legacyKey, {}) || {};
    const m = {};
    cards.forEach((c, i) => {
      if (old[c.front] === 'know') m[i] = 'know';
      else if (old[c.front] === 'dunno') m[i] = 'dunno';
    });
    LS.set(KEY.marks(l), m);
    LS.set(KEY.mig(l), true);
    Object.keys(m).forEach(i => { if (m[i] === 'dunno') reviewSet(l + ':' + i, 'review', 0); });
    return m;
  },
  resetLesson(l, total) {
    LS.set(KEY.marks(l), {});
    const r = reviewAll();
    Object.keys(r).forEach(k => { if (k.indexOf(l + ':') === 0) delete r[k]; });
    LS.set(KEY.review, r);
    const q = LS.get(KEY.quiz, {}) || {};
    delete q[l]; LS.set(KEY.quiz, q);
    const meta = LS.get(KEY.meta, {}) || {};
    delete meta['quiz-' + l]; LS.set(KEY.meta, meta);
  }
};

// ---------------- helpers ----------------
function stripHtml(s) { const d = document.createElement('div'); d.innerHTML = s || ''; return (d.textContent || '').trim(); }
function shuffleArr(a) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); const x = a[i]; a[i] = a[j]; a[j] = x; } return a; }

// ---------------- quiz engine ----------------
function buildQuiz(lessonId) {
  const arr = (window.R3D_DATA.cards[lessonId] || []).map((c, i) => ({ i: i, cat: c.cat, front: c.front, ar: gloss(c) }));
  const usable = arr.filter(c => c.cat !== 'gram' && c.front && c.ar);
  const qs = usable.map(c => {
    const dir = Math.random() < 0.5 ? 'zh2ar' : 'ar2zh';
    return { key: lessonId + ':' + c.i, dir: dir, front: c.front, ar: c.ar, ans: dir === 'zh2ar' ? c.ar : c.front };
  });
  qs.forEach(q => {
    const others = usable.filter(c => c.i !== parseInt(q.key.split(':')[1], 10));
    const vals = [];
    const seen = { };
    seen[q.ans] = 1;
    let guard = 0;
    while (vals.length < 3 && others.length && guard < 200) {
      guard++;
      const c = others[Math.floor(Math.random() * others.length)];
      const v = q.dir === 'zh2ar' ? c.ar : c.front;
      if (!seen[v]) { seen[v] = 1; vals.push(v); }
    }
    q.choices = shuffleArr([q.ans].concat(vals));
  });
  return shuffleArr(qs);
}

const Quiz = {
  root: null, lessonId: null, qs: [], cur: 0, score: 0, wrong: [],
  start(root, lessonId) {
    this.root = root; this.lessonId = lessonId;
    this.qs = buildQuiz(lessonId);
    this.cur = 0; this.score = 0; this.wrong = [];
    root.hidden = false;
    if (root.scrollIntoView) root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    this.renderQ();
  },
  renderQ() {
    const q = this.qs[this.cur];
    const root = this.root;
    root.innerHTML = '';
    const head = document.createElement('div');
    head.className = 'qhead';
    const b = document.createElement('b'); b.textContent = t('quiz.title');
    const p = document.createElement('span'); p.className = 'qprog';
    p.textContent = t('quiz.progress', { n: this.cur + 1, total: this.qs.length });
    head.appendChild(b); head.appendChild(p);
    root.appendChild(head);

    const dirLab = document.createElement('div');
    dirLab.className = 'qdir';
    dirLab.textContent = q.dir === 'zh2ar' ? t('quiz.dirZh') : t('quiz.dirAr');
    root.appendChild(dirLab);

    const prompt = document.createElement('div');
    prompt.className = 'qprompt' + (q.dir === 'zh2ar' ? '' : ' ar');
    prompt.textContent = q.dir === 'zh2ar' ? q.front : q.ar;
    root.appendChild(prompt);

    const choices = document.createElement('div');
    choices.className = 'qchoices';
    q.choices.forEach(ch => {
      const btn = document.createElement('button');
      btn.className = 'qchoice';
      btn.textContent = ch;
      btn.onclick = () => this.answer(q, ch, btn, choices);
      choices.appendChild(btn);
    });
    root.appendChild(choices);

    const fb = document.createElement('div');
    fb.className = 'qfb';
    root.appendChild(fb);
  },
  answer(q, ch, btn, choices) {
    const ok = ch === q.ans;
    if (ok) { btn.classList.add('ok'); this.score++; R3D.answerCorrect(q.key); }
    else {
      btn.classList.add('no');
      this.wrong.push(q.key);
      R3D.answerWrong(q.key);
      Array.from(choices.children).forEach(x => { if (x.textContent === q.ans) x.classList.add('ok'); });
    }
    Array.from(choices.children).forEach(x => { x.onclick = null; });
    const fb = this.root.querySelector('.qfb');
    if (fb) fb.textContent = ok ? t('quiz.correct') : t('quiz.wrong', { x: q.ans });
    setTimeout(() => {
      this.cur++;
      if (this.cur < this.qs.length) this.renderQ();
      else this.finish();
    }, ok ? 550 : 1500);
  },
  finish() {
    const store = LS.get(KEY.quiz, {}) || {};
    store[this.lessonId] = { score: this.score, total: this.qs.length, at: Date.now() };
    LS.set(KEY.quiz, store);
    const root = this.root;
    root.innerHTML = '';
    const head = document.createElement('div');
    head.className = 'qhead';
    const b = document.createElement('b'); b.textContent = t('quiz.resultTitle');
    const p = document.createElement('span'); p.className = 'qprog';
    p.textContent = t('quiz.score', { s: this.score, t: this.qs.length });
    head.appendChild(b); head.appendChild(p);
    root.appendChild(head);

    const sc = document.createElement('div');
    sc.className = 'qscore';
    const s = document.createElement('div'); s.className = 's';
    s.textContent = this.score + ' / ' + this.qs.length;
    sc.appendChild(s);
    if (this.wrong.length) {
      const note = document.createElement('div');
      note.className = 'qnote';
      note.textContent = t('quiz.wrongNote', { n: this.wrong.length });
      sc.appendChild(note);
    }
    root.appendChild(sc);

    const btns = document.createElement('div');
    btns.className = 'qbtns';
    const again = document.createElement('button');
    again.className = 'qbtn'; again.textContent = t('quiz.again');
    again.onclick = () => this.start(root, this.lessonId);
    const close = document.createElement('button');
    close.className = 'qbtn'; close.textContent = t('quiz.close');
    close.onclick = () => { root.hidden = true; root.innerHTML = ''; };
    btns.appendChild(again); btns.appendChild(close);
    root.appendChild(btns);
    window.dispatchEvent(new CustomEvent('r3d:quiz', { detail: { lesson: this.lessonId } }));
  },
  close() { if (this.root) { this.root.hidden = true; this.root.innerHTML = ''; } }
};

// ---------------- export ----------------
window.R3D = {
  LS: LS, KEY: KEY,
  t: t, setLang: setLang, applyI18n: applyI18n, getLang: () => lang,
  mountLangSelector: mountLangSelector,
  reviewAll: reviewAll, reviewGet: reviewGet, reviewSet: reviewSet,
  reviewCount: reviewCount, masteredCount: masteredCount,
  answerCorrect: answerCorrect, answerWrong: answerWrong,
  parseKey: parseKey, cardByKey: cardByKey,
  blobUrl: blobUrl, primeAudio: primeAudio, play: play,
  playCard: playCard, lessonAudio: lessonAudio,
  Marks: Marks, Quiz: Quiz,
  stripHtml: stripHtml, shuffleArr: shuffleArr, buildQuiz: buildQuiz,
  gloss: gloss, glossOf: glossOf, cardType: cardType, cardSub: cardSub
};

applyI18n();
})();
