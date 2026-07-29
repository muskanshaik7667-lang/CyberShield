const puppeteer = require('puppeteer');

(async () => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        
        page.on('console', msg => {
            console.log(`[CONSOLE_${msg.type().toUpperCase()}] ${msg.text()}`);
        });
        
        page.on('pageerror', err => {
            console.log(`[PAGE_ERROR] ${err.message}`);
        });

        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0', timeout: 10000 }).catch(e => console.log('Timeout waiting for network idle'));
        
        // Check if UI rendered
        const rootContent = await page.evaluate(() => {
            const root = document.getElementById('root');
            return root ? root.innerHTML.trim() : '';
        });
        
        if (rootContent.length === 0) {
            console.log('[UI_STATUS] Blank Screen (Empty #root)');
        } else {
            console.log('[UI_STATUS] Visually rendered UI found (Content length: ' + rootContent.length + ')');
        }
        
        await browser.close();
    } catch (e) {
        console.error("Puppeteer error:", e);
    }
})();
