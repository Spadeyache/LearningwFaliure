const { chromium } = require('C:/Users/magic/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base = '\\\\wsl.localhost\\Ubuntu\\home\\ubuntu\\faliure\\work\\portfolio-preview\\';
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 768, height: 1000 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('file://wsl.localhost/Ubuntu/home/ubuntu/faliure/work/portfolio-preview/storyboard-preview.html', { waitUntil: 'domcontentloaded' });
  const frame = page.frames().find(f => f !== page.mainFrame());
  await frame.locator('.sb-step').first().waitFor();
  for (const width of [768, 320]) {
    await page.setViewportSize({ width, height: 1200 });
    await page.screenshot({ path: base + 'storyboard-' + width + '.png', fullPage: true });
    console.log(width, await frame.evaluate(() => ({ overflow: document.documentElement.scrollWidth > innerWidth, states: document.querySelectorAll('.sb-step').length })));
  }
  console.log({ errors });
  await browser.close();
})().catch(error => { console.error(error.message); process.exit(1); });
