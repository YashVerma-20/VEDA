const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  let redirects = 0;
  page.on('request', request => {
    if (request.isNavigationRequest()) redirects++;
  });
  try {
    await page.goto('http://localhost:3000');
    // Set localStorage
    await page.evaluate(() => {
      localStorage.setItem('veda-demo-role', 'ADMIN');
    });
    // Go to / to test if there's an infinite loop when logged in
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    const html = await page.evaluate(() => document.body.innerHTML);
    console.log('REDIRECTS on /:', redirects);
    
    // Now try /vehicles
    redirects = 0;
    await page.goto('http://localhost:3000/vehicles');
    await page.waitForTimeout(3000);
    console.log('REDIRECTS on /vehicles:', redirects);

  } catch (e) {
    console.log('ERROR:', e.message);
  }
  await browser.close();
})();
