from playwright.sync_api import sync_playwright, expect
import time

def test_login_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # 1. Navigate to Login Page (since we are not logged in, root should redirect to login)
            print("Navigating to http://localhost:5173/ ...")
            page.goto("http://localhost:5173/")

            # Verify redirection to /login
            # Note: might take a moment
            print("Checking redirection...")
            page.wait_for_url("**/login")

            # 2. Check elements
            print("Checking UI elements...")
            expect(page.get_by_role("heading", name="Welcome back!")).to_be_visible()
            expect(page.get_by_role("button", name="Dev Login")).to_be_visible()
            expect(page.get_by_role("link", name="Discord")).to_be_visible()

            # 3. Perform Dev Login
            print(" performing login...")
            username = "frontend_verifier"
            page.get_by_placeholder("Your username").fill(username)
            page.get_by_role("button", name="Dev Login").click()

            # 4. Verify Dashboard
            print("Verifying dashboard...")
            page.wait_for_url("http://localhost:5173/")
            expect(page.get_by_role("heading", name="Galactic Ledger")).to_be_visible()
            expect(page.get_by_text(username)).to_be_visible()

            # Wait for planets to load
            expect(page.get_by_role("heading", name="Planets")).to_be_visible()

            # Wait a bit for data fetching and rendering
            time.sleep(2)

            # Take screenshot
            print("Taking screenshot...")
            page.screenshot(path="verification/login_verification.png")
            print("Screenshot saved.")

        except Exception as e:
            print(f"Test failed: {e}")
            page.screenshot(path="verification/error.png")
            raise

        finally:
            browser.close()

if __name__ == "__main__":
    test_login_flow()
