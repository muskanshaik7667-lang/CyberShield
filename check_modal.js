const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
        console.log('Browser Error:', msg.text());
    }
  });

  try {
    // Navigate without waiting for idle so we can catch the Loading state
    await page.goto('http://localhost:5173', { waitUntil: 'domcontentloaded' });
    
    // Check for loading state immediately
    const loadingText = await page.evaluate(() => document.body.innerText);
    if (loadingText.includes('Loading...')) {
        console.log('Loading state detected: true');
    } else {
        console.log('Loading state detected: false');
    }

    // Wait for the modal to appear
    await page.waitForSelector('h2', { timeout: 5000 });
    const h2Text = await page.$eval('h2', el => el.textContent);
    
    if (h2Text.includes('VigilAI')) {
        console.log('Auth modal rendered: true');
    } else {
        console.log('Auth modal rendered: false (Text found: ' + h2Text + ')');
    }
    
  } catch (error) {
    console.error("Puppeteer error:", error.message);
  } finally {
    await browser.close();
  }
})();
