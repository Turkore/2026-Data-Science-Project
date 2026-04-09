from bs4 import BeautifulSoup
import requests
import time
import re
import random
import csv


# 카테고리 추가 
categories = ["에어팟+4", "에어팟+4+미개봉"]


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 기본적 셋팅
links = []
target_count = 20
csv_attach = []


print("Collecting")

for category in categories:
    if len(links) >= target_count:
        break
    
    #숫자 랜덤화 하여 동별 검색 참고: 3부터 10000 정도 까지 동 있음.
    rand_regions = random.sample(range(1,10001), 10)

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


#분석 과 파싱
for i, url in enumerate(links):
    print(f"arraying {1+i}/{len(links)}th articles: {url}")

    try:
        article_res = requests.get(url,headers=headers)
        article_res.encoding = "utf-8"
        article_soup = BeautifulSoup(article_res.text, 'html.parser')

        title = article_soup.find('h1').get_text(strip=True) if article_soup.find('h1') else "None"

        paragraphs = article_soup.find_all('p')
        content = "\n".join([p.get_text(strip=True) for p in paragraphs[:1]])
        
        chat_info = article_soup.select_one('span._1pwsqmm0._1pwsqmm2').get_text(strip= True)

        price = article_soup.select_one('h3').get_text(strip=True)
        price_info = re.sub(r'[^0-9]', '', price)

        items = re.split(r'·', chat_info)
        pure_chat = [re.sub(r'[^0-9]', '', i) for i in items]

        temp_el = article_soup.select_one('span.yzp7msi.yzp7msp.yzp7mss.yzp7mst.yzp7msw.yzp7msn')
        temp_pure = temp_el.get_text(strip=True) if temp_el else "36.5"
        temp = re.sub(r'[^0-9.]', '', temp_pure)



        csv_export = {
            "title" : title,
            "content" : content,
            "heart" : pure_chat[0],
            "interest" : pure_chat[1],
            "view" : pure_chat[2],
            "price" : price_info,
            "temperature" : temp
        }

        csv_attach.append(csv_export)

        time.sleep(1) 

    except Exception as e:
        print(f" Error (PASS): {e}")
        continue

filename = "ninjin.csv"
with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
    writer = csv.DictWriter(file, fieldnames=['title' , 'content', 'heart', 'interest', 'view', 'price', 'temperature'])
    writer.writeheader()
    for csv_writing in csv_attach:
        writer.writerow(csv_writing)
