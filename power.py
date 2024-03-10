import streamlit as st
import pandas as pd
import json
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f'user-agent={ua.random}')

def load_country_data():
    df = pd.read_csv('data.csv')
    return df

# Function to generate keywords by combining product names with city-country pairs
def generate_keywords(product_names, city_country_pairs):
    keywords = []
    for product_name in product_names:
        for city, country in city_country_pairs:
            keywords.append(f"{product_name} {city} {country}")
    return keywords

# Function to scrape data for a given keyword
def scrape_data(keyword, driver, all_data):
    try:
        url = f"https://www.google.com/search?hl=en&tbs=lf:1,lf_ui:2&tbm=lcl&q={keyword}"
        driver.get(url)
        time.sleep(10)

        while True:
            companies = driver.find_elements(By.CSS_SELECTOR, ".rllt__details div:nth-child(1)")
            types = driver.find_elements(By.CSS_SELECTOR, ".rllt__details div:nth-child(2)")
            locations = driver.find_elements(By.CSS_SELECTOR, ".rllt__details div:nth-child(3)")
            html_links = driver.find_elements(By.CSS_SELECTOR, ".a-no-hover-decoration")
            website = driver.find_elements(By.CSS_SELECTOR, ".L48Cpd")

            for i in range(len(companies)):
                company_data = {
                    'Keyword': keyword,
                    'Company': companies[i].text if i < len(companies) else None,
                    'Type': types[i].text if i < len(types) else None,
                    'Location': locations[i].text if i < len(locations) else None,
                    'HTML': html_links[i].get_attribute('innerHTML') if i < len(html_links) else None,
                    'Website': website[i].get_attribute('href') if i < len(website) else None
                }
                all_data.append(company_data)
                #st.text(all_data)

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "#pnnext > span:nth-child(2)")
                next_button.click()
                time.sleep(2)
            except NoSuchElementException:
                break

    except WebDriverException as e:
        # Handle the WebDriverException
        pass

# Function to download data as a JSON file
def download_json(all_data, filename):
    json_str = json.dumps(all_data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}.json">Download JSON File</a>'
    return href

def main():
    st.title("Business Data Scraper")

    # Load country data
    country_data = load_country_data()

    with st.sidebar:
        # Dropdown for selecting region (previously continent)
        regions = country_data['region'].unique()
        selected_region = st.selectbox("Select a Region", regions)

        # Dropdown for selecting country based on region
        countries = country_data[country_data['region'] == selected_region]['country']
        selected_country = st.selectbox("Select a Country", countries)

        product_names = st.text_input("Enter Product Categories", "Category1, Category2").split(', ')
    if selected_country and product_names:
        city_country_pairs = [(selected_country, selected_country)]  # Adjust according to your need
        keywords = generate_keywords(product_names, city_country_pairs)

        if st.button("Start Scraping"):
            # Initialize Selenium WebDriver and scraping logic here
            driver = webdriver.Chrome()
            all_data = []
            for keyword in keywords:
                scrape_data(keyword, driver, all_data)

            st.success("Scraping completed.")
            st.markdown(download_json(all_data, "scraped_data"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
