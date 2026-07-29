const puppeteer = require('puppeteer');
const http = require('http');

function fetchJson(url) {
    return new Promise((resolve, reject) => {
        http.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', err => reject(err));
    });
}

(async () => {
    try {
        console.log("--- RAW JSON FROM /scan ---");
        const scanRes = await fetchJson('http://localhost:5001/scan');
        console.log(scanRes.substring(0, 1000) + (scanRes.length > 1000 ? '...\n(truncated)' : ''));
        
        console.log("\n--- RAW JSON FROM /report ---");
        const reportRes = await fetchJson('http://localhost:5001/report');
        console.log(reportRes);
        
        console.log("\n--- FRONTEND UI CHECK ---");
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        
        page.on('console', msg => console.log(`[BROWSER CONSOLE] ${msg.type().toUpperCase()}: ${msg.text()}`));
        page.on('pageerror', err => console.log(`[BROWSER ERROR] ${err.message}`));
        
        // Wait for page to load
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
        
        console.log("Clicking scan button...");
        await page.waitForSelector('.gold-btn');
        await page.click('.gold-btn');
        
        console.log("Waiting for backend API calls to finish...");
        // Wait for the fetch requests to complete
        await new Promise(r => setTimeout(r, 4000));
        
        // Wait a bit more for React rendering and fetches to settle just in case
        await new Promise(r => setTimeout(r, 2000));
        
        const tableData = await page.evaluate(() => {
            const rows = Array.from(document.querySelectorAll('tbody tr'));
            const rowData = rows.map(tr => {
                const cells = Array.from(tr.querySelectorAll('td'));
                if (cells.length === 0) return null; // maybe expanded row
                
                // Usually the verdict is in a span inside a td
                const verdictSpan = tr.querySelector('span.rounded-full');
                if (!verdictSpan) return null;
                
                return {
                    id: cells[0] ? cells[0].innerText : '',
                    verdictText: verdictSpan.innerText,
                    verdictClasses: verdictSpan.className
                };
            }).filter(Boolean);
            
            // Extract pass_count stat card styling
            const passCard = Array.from(document.querySelectorAll('.glass-panel')).find(p => (p.textContent || '').toUpperCase().includes('EXPLOITED (PASS)'));
            const passCardClasses = passCard ? passCard.className : 'NOT FOUND';
            
            // Extract Shield Blocked (Fail) card styling
            const failCard = Array.from(document.querySelectorAll('.glass-panel')).find(p => (p.textContent || '').toUpperCase().includes('SHIELD BLOCKED (FAIL)'));
            const failCardClasses = failCard ? failCard.className : 'NOT FOUND';
            
            // Extract severity
            const severityHeader = Array.from(document.querySelectorAll('h4')).find(h => (h.textContent || '').toUpperCase().includes('RISK SEVERITY'));
            const severityText = severityHeader ? (severityHeader.nextElementSibling?.textContent || 'NOT FOUND') : 'NOT FOUND';
            
            return { rowData, passCardClasses, failCardClasses, severityText };
        });
        
        if (tableData.rowData.length === 0) {
            console.log("Results table is empty or could not be found.");
        } else {
            console.log(`\nFound ${tableData.rowData.length} rows in the results table.`);
            const passRow = tableData.rowData.find(r => r.verdictText.toLowerCase() === 'pass');
            if (passRow) {
                console.log(`\n--- PASS VERDICT ROW ---`);
                console.log(`Text: ${passRow.verdictText}`);
                console.log(`Classes applied: ${passRow.verdictClasses}`);
            } else {
                console.log(`\n--- PASS VERDICT ROW ---\nNone found.`);
            }
            
            const failRow = tableData.rowData.find(r => r.verdictText.toLowerCase() === 'fail');
            if (failRow) {
                console.log(`\n--- FAIL VERDICT ROW ---`);
                console.log(`Text: ${failRow.verdictText}`);
                console.log(`Classes applied: ${failRow.verdictClasses}`);
            } else {
                console.log(`\n--- FAIL VERDICT ROW ---\nNone found.`);
            }
            
            console.log(`\n--- STAT CARDS ---`);
            console.log(`Exploited (Pass) Card Classes: ${tableData.passCardClasses}`);
            console.log(`Shield Blocked (Fail) Card Classes: ${tableData.failCardClasses}`);
            
            console.log(`\n--- SEVERITY VALUE ---`);
            console.log(`Severity: ${tableData.severityText}`);
        }
        
        await browser.close();
    } catch (e) {
        console.error("Script error:", e);
    }
})();
