const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  const html = await page.evaluate(() => document.body.innerHTML);
  const styles = await page.evaluate(() => {
    const style = window.getComputedStyle(document.body);
    return {
      bg: style.backgroundColor,
      color: style.color,
      display: style.display,
      visibility: style.visibility,
      opacity: style.opacity
    };
  });
  console.log('STYLES:', styles);
  console.log('HTML SNIPPET:', html.substring(0, 1500));
  await browser.close();
})();
