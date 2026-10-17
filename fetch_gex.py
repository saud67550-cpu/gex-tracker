import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

async def get_gex_data(ticker="TSLA"):
    url = f"https://quantwheel.com"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"جاري الانتقال إلى الموقع وسحب بيانات السهم: {ticker}...")
        await page.goto(url, wait_until="networkidle")
        
        search_input = page.locator("input[placeholder*='Search'], input[type='text']").first
        await search_input.fill(ticker)
        await search_input.press("Enter")
        
        await page.wait_for_timeout(5000) 
        
        current_price = await page.locator("text=Current Price >> xpath=../following-sibling::div").first.inner_text()
        call_wall = await page.locator("text=Call Wall >> xpath=../following-sibling::div").first.inner_text()
        put_wall = await page.locator("text=Put Wall >> xpath=../following-sibling::div").first.inner_text()
        
        extracted_data = {
            "Date_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ticker": ticker,
            "Current_Price": current_price.strip(),
            "Call_Wall": call_wall.strip(),
            "Put_Wall": put_wall.strip()
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
    print(f"✅ تم حفظ وتحديث البيانات بنجاح في ملف: {filename}")

if __name__ == "__main__":
    data_result = asyncio.run(get_gex_data("TSLA"))
    save_to_csv(data_result)
