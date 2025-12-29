import sys
import requests
from playwright.sync_api import sync_playwright

# Configuration
BASE_URL = "https://booking.ezcms.vn/hotel/BeDetailHotel"
HOTEL_CODE = "832C74"
NTFY_TOPIC = "vtk_homestay_tracker"
KEYWORDS = ["MOUNTAIN VIEW", "Mountain View", "DELUXE"]

DATES_TO_CHECK = [
    {"check_in": "2026-04-06", "check_out": "2026-04-07"},
    {"check_in": "2026-04-07", "check_out": "2026-04-08"},

]

def send_notification(message):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
                      data=message.encode(encoding='utf-8'))
        print(f"Notification sent: {message}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

def check_availability():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        for date in DATES_TO_CHECK:
            check_in = date["check_in"]
            check_out = date["check_out"]
            
            url = (
                f"{BASE_URL}?hotel_code={HOTEL_CODE}"
                f"&check_in={check_in}&check_out={check_out}"
                "&num_of_rooms=1&num_of_adults=2&num_of_children=0"
                "&promo_code=&rate_code=&room_code=&lang=en&currency=VND"
            )
            
            print(f"Checking {check_in} to {check_out}...")
            
            page = context.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait a bit more to ensure dynamic content loads if networkidle isn't enough
                page.wait_for_timeout(5000) 
                
                content = page.content()
                
                # Check for keywords
                found_keywords = [kw for kw in KEYWORDS if kw in content]
                
                if found_keywords:
                    msg = f"FOUND {', '.join(found_keywords)} for {check_in}!\n{url}"
                    print(msg)
                    send_notification(msg)
                else:
                    print(f"Nothing found for {check_in}.")
                    
            except Exception as e:
                print(f"Error checking {check_in}: {e}")
            finally:
                page.close()
                
        browser.close()

if __name__ == "__main__":
    check_availability()
