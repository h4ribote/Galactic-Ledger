from playwright.sync_api import sync_playwright
import time
import os

def run():
    print("Starting Playwright verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to frontend
        try:
            print("Navigating to http://localhost:5173")
            page.goto("http://localhost:5173", timeout=30000)

            # Wait for title
            print("Waiting for title...")
            page.wait_for_selector("text=Galactic Ledger", timeout=10000)

            # Wait for planet list (Table)
            # Depending on initialization, it might take a moment for planets to load
            print("Waiting for table...")
            page.wait_for_selector("table", timeout=20000)

            # Take screenshot
            screenshot_path = os.path.abspath("verification/verification_frontend.png")
            page.screenshot(path=screenshot_path)
            print(f"Screenshot taken: {screenshot_path}")

        except Exception as e:
            print(f"Error: {e}")
            # Take error screenshot
            page.screenshot(path="verification/verification_error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run()
