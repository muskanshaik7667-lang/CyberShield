const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.text().includes('Supabase client initialized')) {
        console.log(msg.text());
    }
    if (msg.type() === 'error') {
        console.log('Browser Error:', msg.text());
    }
  });

  try {
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
  } catch (error) {
    console.error("Navigation error:", error);
  } finally {
    await browser.close();
  }
})();
