import sys
import requests
from playwright.sync_api import sync_playwright

# Configuration
BASE_URL = "https://booking.ezcms.vn/hotel/BeDetailHotel"
HOTEL_CODE = "832C74"
NTFY_TOPIC = "vtk_homestay_tracker"

# Search Orders: Define specific combinations of dates and keywords to search for.
SEARCH_ORDERS = [
    {
        "check_in": "2026-04-06",
        "check_out": "2026-04-07",
        "keywords": []  # Empty list means "ALL rooms", no filtering
    },
    {
        "check_in": "2026-04-07",
        "check_out": "2026-04-08",
        # Case insensitive matching will be applied
        "keywords": ["Deluxe Mountain View", "PREMIUM DELUXE MOUNTAIN PANORAMA", "Bungalow", "DELUXE MOUNTAIN VIEW BACONY", "PREMIUM DELUXE MOUNTAIN VIEW"]
    },
]

def send_notification(message):
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}",
                      data=message.encode(encoding='utf-8'))
        print(f"Notification sent.")
    except Exception as e:
        print(f"Failed to send notification: {e}")

def check_availability():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        for order in SEARCH_ORDERS:
            check_in = order["check_in"]
            check_out = order["check_out"]
            keywords = [k.lower() for k in order["keywords"]]
            
            url = (
                f"{BASE_URL}?hotel_code={HOTEL_CODE}"
                f"&check_in={check_in}&check_out={check_out}"
                "&num_of_rooms=1&num_of_adults=2&num_of_children=0"
                "&promo_code=&rate_code=&room_code=&lang=en&currency=VND"
            )
            
            print(f"Checking {check_in} to {check_out} for keywords: {order['keywords']}...")
            
            page = context.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait a bit more to ensure dynamic content loads
                page.wait_for_timeout(5000)
                
                # Parse available rooms
                room_cards = page.locator(".Hotel-DetailRoom .option.mb-3")
                count = room_cards.count()
                
                found_rooms = []
                
                for i in range(count):
                    card = room_cards.nth(i)
                    
                    # Extract Room Name
                    name_el = card.locator(".fs-20-replace.text-color-main")
                    if not name_el.count():
                        continue
                    room_name = name_el.inner_text().strip()
                    
                    # Extract Price
                    price_el = card.locator(".d-price .txt-price strong")
                    price = price_el.inner_text().strip() if price_el.count() else "N/A"
                    
                    # Extract Availability (Quantity)
                    qty_el = card.locator(".d-price .text-color-main").first
                    qty = qty_el.inner_text().strip() if qty_el.count() else "Unknown availability"
                    
                    # Check if this room matches any keyword, or if no keywords specific (match all)
                    if not keywords or any(k in room_name.lower() for k in keywords):
                        found_rooms.append({
                            "name": room_name,
                            "price": price,
                            "qty": qty
                        })

                if found_rooms:
                    lines = [f"FOUND rooms for {check_in} (-> {check_out}):"]
                    for room in found_rooms:
                        lines.append(f"- {room['name']}: {room['qty']} @ {room['price']}")
                    
                    lines.append(f"\nLink: {url}")
                    msg = "\n".join(lines)
                    print(msg)
                    send_notification(msg)
                else:
                    print(f"No matching rooms found for {check_in}.")
                    
            except Exception as e:
                print(f"Error checking {check_in}: {e}")
            finally:
                page.close()
                
        browser.close()

if __name__ == "__main__":
    check_availability()
