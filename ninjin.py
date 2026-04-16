from bs4 import BeautifulSoup
import requests
import time
import re
import random
import csv


# add categories
categories = ["에어팟+4"]


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# basic setting
links = []
target_count = 100
csv_attach = []


print("Collecting")

for category in categories:
    if len(links) >= target_count:
        break
    
    # randomise numbers
    rand_regions = random.sample(range(1,10001), 20)

    for regions in rand_regions:
        if len(links) >= target_count:
            break

        if regions:
            print(f"Searching {regions}th neighbourhood...")
            list_url = f"https://www.daangn.com/kr/buy-sell/s/?in={regions}&search={category}"

        #Request url 
        try:   
            response = requests.get(list_url, headers= headers, timeout=10)
            response.encoding = 'utf-8'
        except requests.exceptions.RequestException as e:
            print(f" [{category}] category error: {e}")
            continue

        #Call BeautifulSoup

        soup = BeautifulSoup(response.text, 'html.parser')


        #Main
        for a in soup.find_all('a',attrs={'data-gtm' :'search_article'}):
            href = a["href"]
            ninjin = href if href.startswith('http') else "https://www.daangn.com" + href
            if ninjin not in links:
                links.append(ninjin) 
                if len(links) >= target_count:
                    break
        print(f"[{category}] searched successfully, links collected: {len(links)} ")
        time.sleep(1)


#analyse and parsing
for i, url in enumerate(links):
    print(f"arraying {1+i}/{len(links)}th articles: {url}")

    try:
        article_res = requests.get(url,headers=headers)
        article_res.encoding = "utf-8"
        article_soup = BeautifulSoup(article_res.text, 'html.parser')

        #crawling title
        title_el = article_soup.find('h1').get_text(strip=True) if article_soup.find('h1') else "None"
        title_check = title_el.lower().replace(" ", "")
        if "에어팟4" not in title_check and "airpod4" not in title_check and "airpods4" not in title_check:
            continue

        title = title_check

        #crawling contents
        paragraphs = article_soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs])
        
        chat_info = article_soup.select_one('span._1pwsqmm0._1pwsqmm2').get_text(strip= True)

        #crawling price
        price = article_soup.select_one('h3').get_text(strip=True)
        price_info = re.sub(r'[^0-9]', '', price)

        #crawling heart, interest, view
        items = re.split(r'·', chat_info)
        pure_chat = [re.sub(r'[^0-9]', '', i) for i in items]

        #crawling temperature
        temp_el = article_soup.select_one('span.yzp7msi.yzp7msp')
        temp_pure = temp_el.get_text(strip=True) if temp_el else "36.5"
        temp = re.sub(r'[^0-9.]', '', temp_pure)

        #crawling date
        update_date_el = article_soup.select_one('h2 time')
        update_raw = update_date_el["datetime"]

        #crwaling seller name
        seller = article_soup.select_one('.r4hjxee').get_text(strip=True)

        #crawling region
        region = article_soup.select_one('a.r4hjxer').get_text(strip=True)

        #crawling selling status
        sold_el = article_soup.select_one('span._4y5lbr5')
        sold = sold_el.get_text(strip=True) if sold_el else "판매중"

        #crawling image number
        image = article_soup.find_all('img', class_= '_1wus0xp0')
        image_count = len(image)





        csv_export = {
            "title" : title,
            "content" : content,
            "heart" : pure_chat[0],
            "interest" : pure_chat[1],
            "view" : pure_chat[2],
            "price" : price_info,
            "temperature" : temp,
            "date" : update_raw[:10],
            "url" : url,
            "seller" : seller,
            "sold" : sold , 
            "region" : region,
            "image" : image_count
        }

        csv_attach.append(csv_export)

        time.sleep(1) 

    except Exception as e:
        print(f" Error (PASS): {e}")
        continue

filename = "ninjin.csv"
with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.DictWriter(file, fieldnames=['date', 'title' , 'content', 'heart', 'interest', 'view', 'price', 'temperature', 'seller', 'sold' , 'image', 'region', 'url'])
    writer.writeheader()
    for csv_writing in csv_attach:
        writer.writerow(csv_writing)
