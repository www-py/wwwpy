from playwright.sync_api import sync_playwright


def run(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://example.com")
    print(page.title())
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
