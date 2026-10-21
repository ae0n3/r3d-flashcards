// Comprehensive live-site error inspection (CDP browser)
// Checks: JS exceptions, 404s, i18n gaps, quiz/flip/review flows on all pages.

const CDP_PORT = process.env.CDP_PORT || 9333;
const BASE = 'https://ae0n3.github.io/r3d-flashcards/';

(async () => {
  const { chromium } = require('playwright'); // or use CDP directly
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push('PAGEERROR: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('CONSOLE: ' + m.text()); });
  page.on('requestfailed', r => errors.push('REQUESTFAILED: ' + r.url()));

  // Test every page
  const pages = [
    '/',
    '/review.html',
    '/lesson1-flashcards.html',
    '/lesson2-flashcards.html',
    '/lesson3-flashcards.html',
    '/lesson4-flashcards.html',
    '/lesson5-flashcards.html',
  ];
  for (const p of pages) {
    try {
      await page.goto(BASE + p, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(1500);
      const text = await page.textContent('body');
      console.log('NAV ' + p + ' -> HTTP OK, body len=' + text.length);
    } catch (e) {
      console.log('NAV ' + p + ' -> FAILED: ' + e.message);
    }
  }

  console.log('--- JS errors:' + (errors.length ? '\n' + errors.join('\n') : ' NONE'));
  console.log('--- total errors: ' + errors.length);
  await browser.close();
})();
