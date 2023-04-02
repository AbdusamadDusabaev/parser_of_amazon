import csv
import datetime
from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


domain = "https://www.amazon.com"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
log_file_name = Path("logs", f"log-{datetime.datetime.now()}.txt")
headless_mode = True


def run() -> None:
    write_log(message="The program started", message_type="INFO")
    start_time = time.time()
    main()
    stop_time = time.time()
    write_log(message=f"The program ran for {stop_time - start_time} seconds", message_type="INFO")


def main() -> None:
    mode = input("Input parsing mode (query - for analysis by search query, url - for analysis by url): >>> ").lower()
    if mode != "query" and mode != "url":
        print("[ERROR] Input valid mode")
        return None

    print("Init browser...")
    browser = init_browser()
    try:
        if mode == "query":
            parse_via_query(browser=browser)
        else:
            parse_via_url(browser=browser)
    finally:
        browser.close()
        browser.quit()


def write_log(message: str, message_type: str) -> None:
    with open(log_file_name, "a", encoding="utf-8") as file:
        file.write(f"[{message_type}] ({datetime.datetime.now()}) {message}\n")


def init_browser() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-notifications")
    if headless_mode:
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--profile-directory=Profile_1")
    browser = webdriver.Chrome(options=options)
    return browser


def parse_via_query(browser: webdriver.Chrome) -> None:
    dirt_query_list = input("Enter the text of requests separated by commas (phone, charger, headphones): ").split(",")
    query_list = [query.strip() for query in dirt_query_list]
    for query in query_list:
        start_time = time.time()
        create_file_csv(file_name=query)
        write_log(message=f'The analysis of the search query "{query}" has begun...', message_type="INFO")
        get_info_via_query(browser=browser, query=query)
        stop_time = time.time()
        write_log(message=f'Analysis of the search query "{query}" is finished', message_type="INFO")
        write_log(message=f"It took {stop_time - start_time} seconds to analyze\n", message_type="INFO")


def parse_via_url(browser: webdriver.Chrome) -> None:
    urls = input("Enter the url in the format (name of the file to be written: url-address) separated by commas: ")
    urls = urls.split(",")
    file_names = [url.split(":")[0].strip() for url in urls]
    urls = [url.split(":")[1].strip() for url in urls]
    for index in range(len(urls)):
        start_time = time.time()
        create_file_csv(file_name=file_names[index])
        write_log(message=f'The analysis of the url "{urls[index]}" has begun...', message_type="INFO")
        get_info_via_url(browser=browser, start_url=urls[index], file_name=file_names[index])
        stop_time = time.time()
        write_log(message=f'Analysis of the url "{urls[index]}" is finished', message_type="INFO")
        write_log(message=f"It took {stop_time - start_time} seconds to analyze\n", message_type="INFO")


def create_file_csv(file_name: str) -> None:
    path = Path("result", f"{file_name}.csv")
    write_csv_raw(path=path, raw=["Product", "About item", "Full Price", "Purchase Price",
                                  "Rating", "Reviews", "Characteristics", "Link to Product"])


def write_csv_raw(path: Path, raw: list) -> None:
    with open(path, "a", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(raw)


def get_info_via_query(browser: webdriver.Chrome, query: str) -> None:
    browser.get(url=domain)
    search_form_xpath = "/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[2]/div[1]/input"
    search_form = browser.find_element(By.XPATH, search_form_xpath)
    search_form.send_keys(query)
    search_form.send_keys(Keys.ENTER)
    start_url = browser.current_url
    get_info_via_url(browser=browser, start_url=start_url, file_name=query)


def get_info_via_url(start_url: str, file_name: str, browser: webdriver.Chrome) -> None:
    browser.get(url=start_url)
    time.sleep(3)
    response = browser.page_source
    bs_object = BeautifulSoup(response, "lxml")
    max_page = int(bs_object.find(name="span", class_="s-pagination-item s-pagination-disabled").text.strip())
    all_product_links = get_all_product_links(browser=browser, max_page=max_page, start_url=start_url)
    for product_link in all_product_links:
        try:
            product_info = get_product_info(browser=browser, product_url=product_link)
            write_csv_raw(path=Path("result", f"{file_name}.csv"), raw=product_info)
            write_log(message=f"Product '{product_info[0]}' was written to csv file", message_type="INFO")
        except Exception as ex:
            write_log(message=f"{ex}\n", message_type="ERROR")
            continue


def get_all_product_links(browser: webdriver.Chrome, max_page: int, start_url: str) -> list:
    all_product_links = list()
    for page_index in range(1, max_page):
        url = f"{start_url}&page={page_index}"
        product_tag_list_from_page = get_product_tag_list_from_page(browser=browser, url=url)
        product_links_from_page = [domain + product_tag_from_page.a["href"]
                                   for product_tag_from_page in product_tag_list_from_page]
        all_product_links.extend(product_links_from_page)
    return all_product_links


def get_product_tag_list_from_page(browser: webdriver.Chrome, url: str) -> list:
    browser.get(url=url)
    time.sleep(5)
    response = browser.page_source
    bs_object = BeautifulSoup(response, "lxml")
    product_tag_list_from_page = bs_object.find_all(name="div", attrs={"data-component-type": "s-search-result"})
    return product_tag_list_from_page


def get_product_info(browser: webdriver.Chrome, product_url: str) -> list:
    browser.get(url=product_url)
    wait = WebDriverWait(driver=browser, timeout=30)
    wait.until(expected_conditions.presence_of_element_located((By.TAG_NAME, "h1")))
    response = browser.page_source
    bs_object = BeautifulSoup(response, "lxml")

    title = bs_object.h1.text.strip()
    reviews = get_product_reviews(bs_object=bs_object)
    rating = get_product_rating(bs_object=bs_object)
    purchase_price = get_product_purchase_price(bs_object=bs_object)
    full_price = get_product_full_price(bs_object=bs_object, purchase_price=purchase_price)
    about_item = get_product_about_item(bs_object=bs_object)
    characteristics = get_product_characteristics(bs_object=bs_object)

    product_info = [title, about_item, full_price, purchase_price, rating, reviews, characteristics, product_url]
    return product_info


def get_product_reviews(bs_object: BeautifulSoup) -> str:
    reviews = bs_object.find(name="span", attrs={"id": "acrCustomerReviewText"})
    if reviews is None:
        reviews = "No customer reviews"
        return reviews

    reviews = reviews.text.strip()
    return reviews


def get_product_rating(bs_object: BeautifulSoup) -> str:
    rating_tag = bs_object.find(name="span", class_="a-icon-alt")
    if rating_tag is None:
        rating = "No customer reviews"
        return rating

    rating = rating_tag.text.strip()
    return rating


def get_product_purchase_price(bs_object: BeautifulSoup) -> str:
    variable_purchase_price_classes = ["a-price a-text-price a-size-medium apexPriceToPay",
                                       "a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]
    for variable_purchase_price_class in variable_purchase_price_classes:
        variable_purchase_price_tag = bs_object.find(name="span", class_=variable_purchase_price_class)
        if variable_purchase_price_tag is not None:
            purchase_price = variable_purchase_price_tag.span.text.strip()
            return purchase_price

    purchase_price = "No information"
    return purchase_price


def get_product_full_price(bs_object: BeautifulSoup, purchase_price: str) -> str:
    promotion_block_tag = bs_object.find(name="div", id="apex_desktop")
    if promotion_block_tag is None:
        full_price = purchase_price
        return full_price

    full_price_tag = promotion_block_tag.find(name="span", class_="a-price a-text-price")
    if full_price_tag is not None:
        full_price = full_price_tag.span.text.strip()
        return full_price

    full_price = purchase_price
    return full_price


def get_product_about_item(bs_object: BeautifulSoup) -> str:
    about_item_block_tag = bs_object.find(name="div", attrs={"id": "feature-bullets"})
    if about_item_block_tag is not None:
        about_item_list_tags = about_item_block_tag.find_all(name="li", attrs={})
        about_item_list = [about_item_element.text.strip() for about_item_element in about_item_list_tags]
        about_item = "; ".join(about_item_list)
        return about_item

    about_item = bs_object.find(name="div", class_="a-expander-content a-expander-partial-collapse-content")
    if about_item is not None:
        about_item = about_item.text.strip()
        return about_item

    about_item = "No information"
    return about_item


def get_product_characteristics(bs_object: BeautifulSoup) -> str:
    characteristics_block_tag = bs_object.find(name="div", class_='a-section a-spacing-small a-spacing-top-small')
    if characteristics_block_tag is not None:
        characteristics_table = characteristics_block_tag.table.tbody
        characteristic_tags = characteristics_table.find_all(name="tr")
        characteristics = [f'{characteristic.td.text.strip()}: {characteristic.find_all(name="td")[1].text.strip()}'
                           for characteristic in characteristic_tags]
        characteristics = "; ".join(characteristics)
        return characteristics

    characteristics = "No characteristics"
    return characteristics


if __name__ == "__main__":
    run()
