const { chromium } = require('C:/Users/magic/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const base = '\\\\wsl.localhost\\Ubuntu\\home\\ubuntu\\faliure\\work\\portfolio-preview\\';
(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  await page.goto('http://localhost:8000/index.html', { waitUntil: 'domcontentloaded' });
  await Promise.race([page.evaluate(() => document.fonts.ready), page.waitForTimeout(3500)]);
  await page.screenshot({ path: base + 'current-homepage.png', fullPage: false });
  console.log(JSON.stringify(await page.locator('.headline').evaluate(el => ({ text: el.textContent, font: getComputedStyle(el).fontFamily, color: getComputedStyle(el).color }))));
  await browser.close();
})().catch(error => { console.error(error.message); process.exit(1); });
