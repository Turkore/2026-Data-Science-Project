from bs4 import BeautifulSoup
from curl_cffi import requests
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor
import time
import re
import random
import csv


def get_links(categories, target_count):
    links = []
    target_count_region = 40
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        })

        page.route("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ico}", lambda route: route.abort())

        for category in categories:
            if len(links) >= target_count:
                break
    
        # randomise numbers
            rand_regions = random.sample(range(1,10001), 350)

            for regions in rand_regions:
                if len(links) >= target_count:
                    break

                if regions:
                    print(f"Sniffing API of {regions}th neighbourhood...")
                    list_url = f"https://www.daangn.com/kr/buy-sell/s/?in={regions}&search={category}"

        #Request url 
                try:
                    with page.expect_response(
                        lambda r: "search" in r.url
                        and r.status == 200
                        and r.request.resource_type in ["fetch","xhr"]
                        and "application/json" in r.headers.get("content-type", ""),
                        timeout = 2000
                    ) as response_info:
                        page.goto(list_url, wait_until ="domcontentloaded")
                        page.evaluate("window.scrollTo(0,document.body.scrollHeight)")
                        page.wait_for_timeout(500)
                    
                    api_response = response_info.value
                    json_data = api_response.json()
                    articles = json_data.get("fleamarketArticles",[] )
                    region_count = 0

                    for article in articles:
                        if region_count >= target_count_region:
                            print(f"{regions}th region reached a limit, move to next region")
                            break

                        if len(links) >= target_count:
                            break

                        title = article.get("title", "")
                        if "filteredname" not in title.replace(" ", ""): #or "24년" not in title.lower().replace(" ", ""):
                            continue
                        if "excludename" in title or "excludename" in title:
                            continue

                        base_info = {
                            "title": title.lower().replace(" ", ""),
                            "content": article.get("content", ""),
                            "price": article.get("price", "0").split(".")[0],
                            "date": article.get("createdAt", "")[:10],
                            "url": "https://www.daangn.com" + article.get("id", ""),
                            "seller": article.get("user", {}).get("nickname", "알수없음"),
                            "sold": "판매완료" if article.get("status") != "Ongoing" else "판매중",
                            #"region": article.get("region", {}).get("name", "알수없음")
                        }
                        
                        if base_info["url"] not in [x["url"] for x in links]:
                            links.append(base_info)
                            region_count += 1
                        

                        print(f"received vaild links: {len(links)}")

                    if region_count > 0:
                        time.sleep(random.uniform(1.0, 2.0))

                except Exception:
                    continue
            

        browser.close()

    return links

                    
#analyse and parsing
def parse_others(item):
    if not isinstance(item, dict) or "url" not in item:
        return None
    

    url = item["url"]
    try:
        article_res = requests.get(url,impersonate="chrome116", timeout= 4)
        if article_res.status_code !=200:
            return None

        article_res.encoding = "utf-8"
        article_soup = BeautifulSoup(article_res.text, 'html.parser')

            #crawling heart, interest, view
        chat_info = article_soup.select_one('span._1pwsqmm0._1pwsqmm2').get_text(strip= True)
        items = re.split(r'·', chat_info)
        pure_stats = [re.sub(r'[^0-9]', '', i) for i in items]
        item['heart'] = pure_stats[0]
        item['interest'] = pure_stats[1]
        item['view'] = pure_stats[2]

            #crawling temperature
        temp_el = article_soup.select_one('span.yzp7msi.yzp7msp')
        temp_pure = temp_el.get_text(strip=True) if temp_el else "36.5"
        item["temperature"] = re.sub(r'[^0-9.]', '', temp_pure)

            #crawling region
        item["region"] = article_soup.select_one('a.r4hjxer').get_text(strip=True)

            #crawling image number
        image = article_soup.find_all('img', class_= '_1wus0xp0')
        item["image"] = len(image)

        return item

    except Exception as e:
        print(f" Error (PASS): {e}")
        return None


def multithreading(articles):
    other_data = []
    total = len(articles)
    print(f"total: {total}, multithreading...")

    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(parse_others, articles)

        for i, res in enumerate(results, 1):
            if res:
                other_data.append(res)
            if i % 50 == 0 or i == total:
                print(f"{i}/{total} completed...")
    
    return other_data




def main():
    # add categories
    categories = ["enteryourproduct"]
    target_count = 2000

    st = time.time()

    links = get_links(categories, target_count)

    final_data = multithreading(links)

    data_name = ['date', 'title', 'content', 'heart', 'interest', 'view', 'price', 'temperature', 'seller', 'sold', 'image', 'region', 'url']


    filename = "enteryourproductname.csv"
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=data_name)
        writer.writeheader()
        for d in final_data:
            fd = {k: d.get(k, "0" if k in ['heart','interest','view','image'] else "Unknown") for k in data_name}
            writer.writerow(fd)

    et = time.time()

    print(f"total time: {round((et-st)/ 60,2)}min")


if __name__ == "__main__":
    main()

