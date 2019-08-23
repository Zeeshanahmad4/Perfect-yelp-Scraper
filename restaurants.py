# coding: utf-8
import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv
from selenium.webdriver.chrome.options import Options
import random
from lxml import html
import requests
import re
import urllib
import unicodecsv as csv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def link_assembler(file_path, name):
    fieldnames = ['Grade']

    with open(file_path, "ab") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # writer.writeheader()
        writer.writerow({
            "Grade": name,
        })


def end_data(file_path, Name, Category, Address, Phone, Price_range, Health_rating, Info, Working_hours, Ratings, Ratings_histogram, Claimed_status, Reviews, Website, Url):
    fieldnames = ['name', 'category', 'address', 'phone', 'price_range', 'health_rating', 'info',
                  'working_hours', 'ratings', 'ratings_histogram', 'claimed_status', 'reviews', 'website', 'url']

    with open(file_path, "ab") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, encoding='utf-8')
        # writer.writeheader()
        writer.writerow({
            "name": Name,
            "category": Category,
            "address": Address,
         			"phone": Phone,
         			"price_range": Price_range,
         			"health_rating": Health_rating,
         			"info": Info,
         			"working_hours": Working_hours,
            "ratings": Ratings,
         			"ratings_histogram": Ratings_histogram,
         			"claimed_status": Claimed_status,
         			"reviews": Reviews,
         			"website": Website,
         			"url": Url
        })


def parse(url):
	headers = {
	    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
	response = requests.get(url, headers=headers, verify=False).text
	parser = html.fromstring(response)
	print ("Scraping this Resaurants")
	raw_name = parser.xpath("//h1[contains(@class,'page-title')]//text()")
	raw_claimed = parser.xpath(
	    "//span[contains(@class,'claim-status_icon--claimed')]/parent::div/text()")
	raw_reviews = parser.xpath(
	    "//div[contains(@class,'biz-main-info')]//span[contains(@class,'review-count rating-qualifier')]//text()")
	raw_category = parser.xpath(
	    '//div[contains(@class,"biz-page-header")]//span[@class="category-str-list"]//a/text()')
	hours_table = parser.xpath("//table[contains(@class,'hours-table')]//tr")
	details_table = parser.xpath("//div[@class='short-def-list']//dl")
	raw_map_link = parser.xpath("//a[@class='biz-map-directions']/img/@src")
	raw_phone = parser.xpath(".//span[@class='biz-phone']//text()")
	raw_address = parser.xpath(
	    '//div[@class="mapbox-text"]//div[contains(@class,"map-box-address")]//text()')
	raw_wbsite_link = parser.xpath(
	    "//span[contains(@class,'biz-website')]/a/@href")
	raw_price_range = parser.xpath(
	    "//dd[contains(@class,'price-description')]//text()")
	raw_health_rating = parser.xpath(
	    "//dd[contains(@class,'health-score-description')]//text()")
	rating_histogram = parser.xpath(
	    "//table[contains(@class,'histogram')]//tr[contains(@class,'histogram_row')]")
	raw_ratings = parser.xpath(
	    "//div[contains(@class,'biz-page-header')]//div[contains(@class,'rating')]/@title")

	working_hours = []
	for hours in hours_table:
		raw_day = hours.xpath(".//th//text()")
		raw_timing = hours.xpath("./td//text()")
		day = ''.join(raw_day).strip().encode('utf-8')
		timing = ''.join(raw_timing).strip().replace(u"\n        \n                Closed now", "").replace(u"\n        \n        \n            Special hours", "").replace(
		    u"\n        \n                Open now", "").replace(u"Closed\n        \n            Special hours", "").encode('utf-8')
		working_hours.append({day: timing})
	info = []
	for details in details_table:
		raw_description_key = details.xpath('.//dt//text()')
		raw_description_value = details.xpath('.//dd//text()')
		description_key = ''.join(raw_description_key).strip()
		description_value = ''.join(raw_description_value).strip()
		info.append({description_key: description_value})

	ratings_histogram = []
	for ratings in rating_histogram:
		raw_rating_key = ratings.xpath(".//th//text()")
		raw_rating_value = ratings.xpath(".//td[@class='histogram_count']//text()")
		rating_key = ''.join(raw_rating_key).strip()
		rating_value = ''.join(raw_rating_value).strip()
		ratings_histogram.append({rating_key: rating_value})

	name = ''.join(raw_name).strip().encode('utf-8')
	phone = ''.join(raw_phone).strip()
	address = ' '.join(' '.join(raw_address).split())
	health_rating = ''.join(raw_health_rating).strip()
	price_range = ''.join(raw_price_range).strip()
	claimed_status = ''.join(raw_claimed).strip()
	reviews = ''.join(raw_reviews).strip()
	category = ','.join(raw_category)
	cleaned_ratings = ''.join(raw_ratings).strip()

	if raw_wbsite_link:
		decoded_raw_website_link = urllib.unquote(raw_wbsite_link[0])
		website = re.findall("biz_redir\?url=(.*)&website_link",
		                     decoded_raw_website_link)[0]
	else:
		website = ''

	if raw_ratings:
		ratings = re.findall("\d+[.,]?\d+", cleaned_ratings)[0].encode('utf-8')
	else:
		ratings = 0

	data = {'working_hours': working_hours,
         'info': info,
         'ratings_histogram': ratings_histogram,
         'name': name,
         'phone': phone,
         'ratings': ratings,
         'address': address,
         'health_rating': health_rating,
         'price_range': price_range,
         'claimed_status': claimed_status,
         'reviews': reviews,
         'category': category,
         'website': website,
         'url': url
         }
	return data


succ_flag = ""
start = "&start="
urlList = ["https://www.yelp.com/search?find_desc=restaurants&find_loc=Chicago%2C%20IL&l=p%3AIL%3AChicago%3A%3A%5BAlbany_Park%2CAndersonville%2CArcher_Heights%2CAshburn%2CAuburn_Gresham%2CAustin%2CAvalon_Park%2CAvondale%2CBack_of_the_Yards%2CBelmont_Central%2CBeverly%2CBrainerd%2CBridgeport%2CBrighton_Park%2CBronzeville%2CBucktown%2CBurnside%2CCabrini-Green%2CCalumet_Heights%2CCanaryville%2CChatham%2CChicago_Lawn%2CChinatown%2CClearing%2CCragin%5D", "https://www.yelp.com/search?find_desc=restaurants&find_loc=Chicago%2C%20IL&ns=1&l=p%3AIL%3AChicago%3A%3A%5BDePaul%2CDouglas%2CDunning%2CEast_Garfield_Park%2CEast_Side%2CEdgewater%2CEdison_Park%2CEnglewood%2CForest_Glen%2CFulton_Market%2CGage_Park%2CGalewood%2CGarfield_Ridge%2CGold_Coast%2CGoose_Island%2CGrand_Boulevard%2CGreater_Grand_Crossing%2CGreektown%2CHegewisch%2CHermosa%2CHumboldt_Park%2CHyde_Park%2CIrving_Park%2CJefferson_Park%2CJeffery_Manor%2CKenwood%2CLakeview%2CLawndale%2CLincoln_Park%2CLincoln_Square%5D", "https://www.yelp.com/search?find_desc=restaurants&find_loc=Chicago%2C%20IL&ns=1&l=p%3AIL%3AChicago%3A%3A%5BLittle_Village%2CLogan_Square%2CNear_North_Side%5D",
           "https://www.yelp.com/search?find_desc=restaurants&find_loc=Chicago%2C%20IL&ns=1&l=p%3AIL%3AChicago%3A%3A%5BMagnificent_Mile%2CMarquette_Park%2CMcKinley_Park%2CMontclare%2CMorgan_Park%2CMount_Greenwood%2CNear_Southside%2CNear_West_Side%2CNew_City%2CNoble_Square%2CNorth_Center%2CNorth_Park%2CNorwood_Park%2CO%27Hare%2COakland%2COld_Town%2CPilsen%2CPortage_Park%2CPrinter%27s_Row%2CPullman%2CRavenswood%5D", "https://www.yelp.com/search?find_desc=restaurants&find_loc=Chicago%2C%20IL&ns=1&l=p%3AIL%3AChicago%3A%3A%5BRiver_East%2CRiver_North%2CRiver_West%2CRogers_Park%2CRoscoe_Village%2CRoseland%2CSauganash%2CScottsdale%2CSouth_Chicago%2CSouth_Deering%2CSouth_Loop%2CSouth_Shore%2CStreeterville%2CThe_Loop%5D", "https://www.yelp.com/search?find_desc=restaurants&find_loc=Chicago%2C%20IL&ns=1&l=p%3AIL%3AChicago%3A%3A%5BTri-Taylor%2CUkrainian_Village%2CUniversity_Village%2CUptown%2CWashington_Heights%2CWashington_Park%2CWest_Elsdon%2CWest_Englewood%2CWest_Garfield_Park%2CWest_Lawn%2CWest_Loop%2CWest_Pullman%2CWest_Rogers_Park%2CWest_Town%2CWicker_Park%2CWoodlawn%2CWrigleyville%5D"]
linksalist = []
options = Options()
options.headless = True
#PROXY = "36.67.23.117:8888" # IP:PORT or HOST:PORT
#options.add_argument('--proxy-server=%s' % PROXY)
driver = selenium.webdriver.Chrome(chrome_options=options)
driver.set_page_load_timeout(10000)
for i in urlList:
    e = 30
    d = -30
    for k in range(30):
        d += e
        f = i+"{}{}".format(start, d)
        driver.get(f)
        # l = random.randint(0,4)
        # sleep(l)
        childlinks = driver.find_elements_by_class_name(
            "heading--h3__373c0__1n4Of")
        for j in childlinks:
            try:
                b = j.find_element_by_tag_name("a")
                c = b.get_attribute("href")
                adlink = "https://www.yelp.com/adredir?"
                adchecker = c[:29]
                if adlink == adchecker:
                    pass
                else:
                    link_assembler("restaurants_urls.csv", c)
                    linksalist.append(c)
            except:
                pass
        for row in linksalist:
            while True:
                try:
                    scraped_data = parse(row)
                    l = random.randint(0, 15)
                    sleep(l)
                    print(row)
                    succ_flag = scraped_data['address']
                    if succ_flag != "":
                        break
                    print("Error!Retrying this Page")
                except:
                    pass
		    # print("Scraped successfully")
            end_data("unfilterd.csv", scraped_data['name'], scraped_data['category'], scraped_data['address'], scraped_data['phone'], scraped_data['price_range'], scraped_data['health_rating'], scraped_data['info'],
                     scraped_data['working_hours'], scraped_data['ratings'], scraped_data['ratings_histogram'], scraped_data['claimed_status'], scraped_data['reviews'], scraped_data['website'], scraped_data['url'])

	    linksalist = []

with open('unfilterd.csv', 'r') as in_file, open('filterd_endata.csv', 'wb') as out_file:
    seen = set()  # set for fast O(1) amortized lookup
    for line in in_file:
        if line in seen:
            continue  # skip duplicate

        seen.add(line)
        out_file.write(line)
