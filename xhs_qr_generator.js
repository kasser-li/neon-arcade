// 使用 Puppeteer 生成小红书登录二维码
const puppeteer = require('puppeteer-core');

async function generateQR(userId) {
    const browser = await puppeteer.launch({
        executablePath: '/snap/bin/chromium',
        headless: true,
        args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 720 });
    
    // 访问小红书
    await page.goto('https://www.xiaohongshu.com/explore', { waitUntil: 'networkidle2' });
    
    // 等待二维码出现
    await page.waitForSelector('.qrcode-img, img[class*="qr"], canvas[class*="qr"]', { timeout: 30000 });
    
    // 截图二维码
    const qrPath = `/tmp/xhs_qr_${userId}_${Date.now()}.png`;
    const qrElement = await page.$('.qrcode-img, img[class*="qr"], canvas[class*="qr"]');
    
    if (qrElement) {
        await qrElement.screenshot({ path: qrPath });
        console.log(`QR_PATH:${qrPath}`);
        
        // 等待120秒
        await new Promise(r => setTimeout(r, 120000));
        
        // 获取 cookies
        const cookies = await page.cookies();
        const xhsCookies = cookies.filter(c => c.domain.includes('xiaohongshu'));
        
        if (xhsCookies.find(c => c.name === 'a1')) {
            console.log(`COOKIES:${JSON.stringify(xhsCookies)}`);
        } else {
            console.log('LOGIN_TIMEOUT');
        }
    } else {
        console.log('QR_NOT_FOUND');
    }
    
    await browser.close();
}

const userId = process.argv[2] || 'default';
generateQR(userId).catch(e => {
    console.error('ERROR:', e.message);
    process.exit(1);
});
