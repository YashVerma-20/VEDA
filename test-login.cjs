const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('console', msg => console.log('BROWSER:', msg.text()));
  try {
    await page.goto('http://localhost:3000/login');
    await page.waitForTimeout(1000);
    // Click "LOGIN AS ADMIN"
    await page.click('text="LOGIN AS ADMIN"');
    await page.waitForTimeout(2000);
    const url = page.url();
    console.log('URL after login:', url);
    const html = await page.evaluate(() => document.body.innerHTML);
    console.log('HTML LEN after login:', html.length);
  } catch (e) {
    console.log('ERROR:', e.message);
  }
  await browser.close();
})();
