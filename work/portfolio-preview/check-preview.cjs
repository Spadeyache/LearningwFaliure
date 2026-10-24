const { chromium } = require('C:/Users/magic/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base = '\\\\wsl.localhost\\Ubuntu\\home\\ubuntu\\faliure\\work\\portfolio-preview\\';
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 780, height: 1200 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('file://wsl.localhost/Ubuntu/home/ubuntu/faliure/work/portfolio-preview/learning-preview.html', { waitUntil: 'domcontentloaded' });
  const frame = page.frameLocator('iframe');
  await frame.locator('.learning-belief').waitFor();
  await page.screenshot({ path: base + 'learning-preview-desktop.png', fullPage: true });
  for (let i = 0; i < 4; i++) {
    await frame.locator('[data-learning-step="' + i + '"]').click();
    if (await frame.locator('[data-learning-step="' + i + '"]').getAttribute('aria-pressed') !== 'true') throw Error('Step did not update');
    console.log(i, await frame.locator('.learning-belief').textContent());
  }
  await page.screenshot({ path: base + 'learning-preview-final-state.png', fullPage: true });
  await page.setViewportSize({ width: 320, height: 1600 });
  const live = page.frames().find(f => f !== page.mainFrame());
  console.log(JSON.stringify({ mobileOverflow: await live.evaluate(() => document.documentElement.scrollWidth > innerWidth), errors }));
  await page.screenshot({ path: base + 'learning-preview-mobile.png', fullPage: true });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  console.log('reducedMotion', await frame.locator('.learning-cube').evaluate(el => getComputedStyle(el).transitionDuration));
  await browser.close();
  if (errors.length) process.exitCode = 1;
})().catch(error => { console.error(error.stack); process.exit(1); });
