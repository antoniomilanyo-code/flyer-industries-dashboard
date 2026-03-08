const puppeteer = require('puppeteer');
const fs = require('fs');

function getCredentials() {
    const credsFile = '/root/.openclaw/workspace/crafted_reports/.mokapos_credentials';
    let email = null, password = null;
    if (fs.existsSync(credsFile)) {
        const content = fs.readFileSync(credsFile, 'utf8');
        const lines = content.split('\n');
        for (const line of lines) {
            if (line.startsWith('EMAIL=')) email = line.split('=', 2)[1]?.trim();
            if (line.startsWith('PASSWORD=')) password = line.split('=', 2)[1]?.trim();
        }
    }
    return { email, password };
}

function parseRp(value) {
    if (!value || value === '0') return 0;
    const cleaned = value.replace(/Rp[.\s]*/i, '').replace(/[.,]/g, '');
    return parseFloat(cleaned) || 0;
}

function getMonthlyPeriodDates() {
    const today = new Date();
    let startDate, endDate;
    
    if (today.getDate() >= 21) {
        startDate = new Date(today.getFullYear(), today.getMonth(), 21);
        endDate = new Date(today.getFullYear(), today.getMonth() + 1, 20);
    } else {
        startDate = new Date(today.getFullYear(), today.getMonth() - 1, 21);
        endDate = new Date(today.getFullYear(), today.getMonth(), 20);
    }
    
    return {
        start: startDate.toISOString().split('T')[0],
        end: endDate.toISOString().split('T')[0],
        startFormatted: `${startDate.getDate()}/${startDate.getMonth() + 1}/${startDate.getFullYear()}`,
        endFormatted: `${endDate.getDate()}/${endDate.getMonth() + 1}/${endDate.getFullYear()}`,
        startDateObj: startDate,
        endDateObj: endDate
    };
}

async function getMokaposRevenue() {
    const { email, password } = getCredentials();
    if (!email || !password) {
        console.log(JSON.stringify({ error: 'No credentials' }));
        process.exit(1);
    }
    
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    });
    
    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1366, height: 768 });
        
        console.log('Logging in...');
        await page.goto('https://backoffice.mokapos.com/login', { 
            waitUntil: 'networkidle2', timeout: 60000 
        });
        
        await page.waitForSelector('input[type="text"]', { timeout: 10000 });
        await page.type('input[type="text"]', email);
        
        let buttons = await page.$$('button');
        for (const btn of buttons) {
            const text = await btn.evaluate(el => el.textContent);
            if (text && (text.includes('Next') || text.includes('LANJUT'))) {
                await btn.click(); break;
            }
        }
        
        await new Promise(r => setTimeout(r, 2000));
        await page.waitForSelector('input[type="password"]', { timeout: 10000 });
        await page.type('input[type="password"]', password);
        
        buttons = await page.$$('button');
        for (const btn of buttons) {
            const text = await btn.evaluate(el => el.textContent);
            if (text && (text.includes('Sign In') || text.includes('Masuk'))) {
                await btn.click(); break;
            }
        }
        
        await new Promise(r => setTimeout(r, 10000));
        
        console.log('Logged in successfully');
        
        // Get period dates
        const period = getMonthlyPeriodDates();
        const today = new Date();
        const todayStr = today.toISOString().split('T')[0];
        
        // Navigate to Sales Report
        console.log('Navigating to Sales Reports...');
        await page.goto('https://backoffice.mokapos.com/reports/sales', { 
            waitUntil: 'networkidle0', timeout: 60000 
        });
        
        console.log('Waiting for page to load...');
        await new Promise(r => setTimeout(r, 10000));
        
        // Take screenshot for debugging (optional, save to file)
        // await page.screenshot({ path: '/tmp/mokapos_reports.png', fullPage: true });
        
        // Get the full page content
        const pageContent = await page.content();
        const pageText = await page.evaluate(() => document.body.innerText);
        
        console.log('Page loaded, extracting data...');
        console.log('Page text length:', pageText.length);
        
        // Look for Sales Summary section
        const salesData = await page.evaluate(() => {
            const result = {
                gross_sales: 0,
                net_sales: 0,
                transactions: 0,
                found: false,
                debug_info: []
            };
            
            // Try to find by common Mokapos data attributes
            const elements = document.querySelectorAll('*');
            
            for (const el of elements) {
                const text = el.textContent || '';
                const cleanText = text.trim();
                
                // Look for gross/net sales indicators
                if (cleanText.includes('Gross Sales') || cleanText.includes('Penjualan Kotor')) {
                    result.debug_info.push(`Found Gross label: ${cleanText.substring(0, 100)}`);
                    // Check next siblings or parent for value
                    const parent = el.parentElement;
                    if (parent) {
                        const siblingText = parent.textContent;
                        const match = siblingText.match(/Rp[.\s]*([\d.,]+)/);
                        if (match && !result.gross_sales) {
                            result.gross_sales = match[1];
                            result.found = true;
                        }
                    }
                }
                
                if (cleanText.includes('Net Sales') || cleanText.includes('Penjualan Bersih')) {
                    result.debug_info.push(`Found Net label: ${cleanText.substring(0, 100)}`);
                    const parent = el.parentElement;
                    if (parent) {
                        const siblingText = parent.textContent;
                        const match = siblingText.match(/Rp[.\s]*([\d.,]+)/);
                        if (match && !result.net_sales) {
                            result.net_sales = match[1];
                        }
                    }
                }
            }
            
            // Also try to get all monetary values
            const bodyText = document.body.innerText;
            const rpMatches = [...bodyText.matchAll(/Rp[.\s]*([\d.,]+)/gi)];
            result.all_amounts = rpMatches.map(m => m[1]).slice(0, 20);
            
            // Get transactions
            const transMatch = bodyText.match(/(\d+)\s*(?:Transactions|Transaksi)/i);
            if (transMatch) {
                result.transactions = parseInt(transMatch[1]);
            }
            
            return result;
        });
        
        console.log('Sales data from reports:', JSON.stringify(salesData, null, 2));
        
        // If reports page didn't have data, get from dashboard
        let dashboardData = null;
        if (!salesData.found || parseRp(salesData.gross_sales) === 0) {
            console.log('No data from reports, checking dashboard...');
            
            await page.goto('https://backoffice.mokapos.com/dashboard', { 
                waitUntil: 'networkidle0', timeout: 60000 
            });
            await new Promise(r => setTimeout(r, 8000));
            
            dashboardData = await page.evaluate(() => {
                const result = { gross_sales: '', net_sales: '', transactions: 0, amounts: [] };
                const bodyText = document.body.innerText;
                
                const rpMatches = [...bodyText.matchAll(/Rp[.\s]*([\d.,]+)/gi)];
                result.amounts = rpMatches.map(m => m[1]).filter(v => v && v !== '0');
                
                if (result.amounts.length > 0) result.gross_sales = result.amounts[0];
                if (result.amounts.length > 1) result.net_sales = result.amounts[1];
                
                const transMatch = bodyText.match(/(\d+)\s*(?:Transactions|Transaksi)/i);
                if (transMatch) result.transactions = parseInt(transMatch[1]);
                
                return result;
            });
            
            console.log('Dashboard data:', JSON.stringify(dashboardData, null, 2));
        }
        
        // Determine final values
        const useReportsData = salesData.found && parseRp(salesData.gross_sales) > 0;
        
        const finalGross = useReportsData ? salesData.gross_sales : (dashboardData?.gross_sales || '0');
        const finalNet = useReportsData ? salesData.net_sales : (dashboardData?.net_sales || '0');
        const finalTrans = useReportsData ? salesData.transactions : (dashboardData?.transactions || 0);
        
        const dailyGross = dashboardData?.gross_sales || finalGross;
        const dailyNet = dashboardData?.net_sales || finalNet;
        const dailyTrans = dashboardData?.transactions || finalTrans;
        
        const result = {
            success: true,
            source: useReportsData ? 'mokapos_reports' : 'mokapos_dashboard',
            outlet: 'CRAFTED BERAWA',
            monthly_period: {
                start: period.start,
                end: period.end,
                start_formatted: period.startFormatted,
                end_formatted: period.endFormatted
            },
            daily_revenue: {
                gross_sales: parseRp(dailyGross),
                net_sales: parseRp(dailyNet),
                transactions: dailyTrans
            },
            monthly_cumulative_revenue: {
                gross_sales: parseRp(finalGross),
                net_sales: parseRp(finalNet),
                transactions: finalTrans,
                data_source: useReportsData ? 'reports_page' : 'dashboard_single_day'
            },
            debug: {
                sales_data_found: salesData.found,
                reports_amounts: salesData.all_amounts,
                dashboard_amounts: dashboardData?.amounts || []
            },
            timestamp: new Date().toISOString()
        };
        
        console.log(JSON.stringify(result, null, 2));
        
    } catch (error) {
        console.log(JSON.stringify({ error: error.message, stack: error.stack }));
    } finally {
        await browser.close();
    }
}

getMokaposRevenue();
