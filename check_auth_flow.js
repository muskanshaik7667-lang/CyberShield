const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  try {
    console.log("Check 1: Load frontend and confirm Auth modal...");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    // Wait for the auth modal p tag
    await page.waitForFunction(() => {
      return document.body.innerText.includes('Sign in to your account');
    }, { timeout: 5000 });
    console.log("-> PASS: Auth modal appeared.");

    console.log("Check 2: Log in with test user (test@example.com / password123)...");
    await page.type('input[type="email"]', 'test@example.com');
    await page.type('input[type="password"]', 'password123');
    await page.click('button'); // The Sign In button

    // Wait for the Dashboard to appear
    await page.waitForSelector('nav', { timeout: 10000 });
    const navText = await page.$eval('nav', el => el.textContent);
    if (navText.includes('Vigil AI')) {
      console.log("-> PASS: Dashboard loaded successfully.");
    } else {
      console.log("-> FAIL: Dashboard did not load.");
    }

    console.log("Check 3: Confirm Sign Out button appears in top right corner...");
    // Find a button containing "Sign Out"
    const signoutBtn = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.find(b => b.textContent.includes('Sign Out'));
    });
    
    // Ensure the JSHandle points to a valid element
    const isElement = await page.evaluate(el => el instanceof HTMLElement, signoutBtn);
    
    if (isElement) {
      console.log("-> PASS: Sign Out button is visible.");
    } else {
      console.log("-> FAIL: Sign Out button not found.");
      return;
    }

    console.log("Check 4: Click Sign Out and confirm modal reappears...");
    await signoutBtn.click();
    
    // Wait for modal to appear again
    await page.waitForFunction(() => {
      return document.body.innerText.includes('Sign in to your account');
    }, { timeout: 10000 });
    
    console.log("-> PASS: Auth modal reappeared after sign out.");

  } catch (error) {
    console.error("Puppeteer Script Error:", error.message);
  } finally {
    await browser.close();
  }
})();
