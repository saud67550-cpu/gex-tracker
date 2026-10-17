import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

async def get_gex_data(ticker="TSLA"):
    # الانتقال المباشر لصفحة التيكر لتفادي حظر خانات البحث
    url = f"https://quantwheel.com"
    
    async with async_playwright() as p:
        # تشغيل المتصفح مع إعدادات إضافية لتخطي أنظمة الحماية
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        # تحديد أبعاد الشاشة ومحاكاة متصفح حقيقي
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        print(f"جاري فتح المنصة وسحب البيانات الحية...")
        # استخدام مهلة انتظار أطول لضمان تحميل كامل البيانات بالخلفية
        await page.goto(url, wait_until="load", timeout=60000)
        
        # إذا كان السهم المطلوب مختلف عن الافتراضي، نستخدم كود البحث الاحتياطي
        if ticker.upper() != "TSLA":
            try:
                search_input = page.locator("input[type='text'], .ticker-search-input").first
                await search_input.click()
                await search_input.fill(ticker)
                await search_input.press("Enter")
                await page.wait_for_timeout(4000)
            except Exception:
                pass
        else:
            # مهلة استقرار لقراءة قيم سهم تسلا الافتراضي
            await page.wait_for_timeout(7000)
        
        # سحب الأرقام مباشرة من شاشات العرض الرقمية (Dashboard Metrics)
        # الكود يبحث عن القيم المرافقة للعناوين الأساسية في منصة QuantWheel
        try:
            current_price = await page.locator("div:has-text('Current Price') + div, [class*='price']").first.inner_text()
        except:
            current_price = "N/A"
            
        try:
            call_wall = await page.locator("div:has-text('Call Wall') + div, [class*='call-wall']").first.inner_text()
        except:
            call_wall = "N/A"
            
        try:
            put_wall = await page.locator("div:has-text('Put Wall') + div, [class*='put-wall']").first.inner_text()
        except:
            put_wall = "N/A"
        
        extracted_data = {
            "Date_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ticker": ticker.upper(),
            "Current_Price": current_price.replace('$', '').strip(),
            "Call_Wall": call_wall.replace('$', '').strip(),
            "Put_Wall": put_wall.replace('$', '').strip()
        }
        
        await browser.close()
        return extracted_data

def save_to_csv(data, filename="gex_market_data.csv"):
    df_new = pd.DataFrame([data])
    try:
        df_old = pd.read_csv(filename)
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        df_combined.to_csv(filename, index=False)
    except FileNotFoundError:
        df_new.to_csv(filename, index=False)
    print(f"✅ تم تحديث ملف البيانات بنجاح: {filename}")

if __name__ == "__main__":
    data_result = asyncio.run(get_gex_data("TSLA"))
    save_to_csv(data_result)
