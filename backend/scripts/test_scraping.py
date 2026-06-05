"""Quick test: navigate to fincaraiz, find detail pages, extract data."""
import asyncio
import re
import sys
sys.path.insert(0, "/app")


async def test():
    """Test scraping against fincaraiz live site."""
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()

        # Step 1: Go to listing page
        url = "https://www.fincaraiz.com.co/venta/casas/bogota/bogota-dc"
        print(f"1. Navigating to listing: {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)

        # Step 2: Find detail links
        links = await page.query_selector_all("a[href]")
        detail_urls = []
        for link in links:
            href = await link.get_attribute("href")
            if href and re.search(r"/\d{5,}", href):
                if href.startswith("/"):
                    href = "https://www.fincaraiz.com.co" + href
                if "fincaraiz" in href and "/inmobiliarias/" not in href:
                    detail_urls.append(href)

        print(f"2. Found {len(detail_urls)} detail URLs")
        for u in detail_urls[:3]:
            print(f"   {u}")

        if not detail_urls:
            print("ERROR: No detail URLs found!")
            await browser.close()
            return

        # Step 3: Navigate to first detail page
        detail_url = detail_urls[0]
        print(f"\n3. Navigating to detail: {detail_url}")
        await page.goto(detail_url, wait_until="networkidle", timeout=30000)

        final_url = page.url
        print(f"   Final URL: {final_url}")

        # Step 4: Test Codigo_Inmueble regex
        match = re.search(r"/(\d+)$", final_url)
        codigo = match.group(1) if match else None
        print(f"\n4. Codigo_Inmueble regex: {codigo}")

        # Step 5: Test key selectors
        print("\n5. Testing selectors:")
        selectors = {
            "h1.property-title": "Titulo",
            ".main-price": "Precio",
            ".property-price-tag .main-price": "Precio2",
            ".property-location-tag p:first-child": "Municipio",
            ".property-location-tag p:last-child": "Barrio",
            ".property-description": "Descripcion",
            ".owner-name-text": "Dueno",
            "h1": "H1",
        }
        for sel, name in selectors.items():
            el = await page.query_selector(sel)
            if el:
                text = await el.text_content()
                print(f"   OK {name} ({sel}): {text.strip()[:60] if text else 'empty'}")
            else:
                print(f"   MISS {name} ({sel})")

        # Step 6: Test meta tags
        print("\n6. Testing meta tags:")
        for prop in ["og:url", "og:image"]:
            el = await page.query_selector(f'meta[property="{prop}"]')
            if el:
                content = await el.get_attribute("content")
                print(f"   OK {prop}: {content[:80] if content else 'empty'}")
            else:
                print(f"   MISS {prop}")

        # Step 7: Test technical sheet
        print("\n7. Testing technical sheet (label extraction):")
        rows = await page.query_selector_all(".technical-sheet .ant-row.ant-row-space-between")
        print(f"   Found {len(rows)} technical sheet rows")
        for row in rows[:5]:
            text = await row.text_content()
            if text:
                print(f"   Row: {text.strip()[:80]}")

        await browser.close()
        print("\nDONE - Test completed successfully")


if __name__ == "__main__":
    asyncio.run(test())
