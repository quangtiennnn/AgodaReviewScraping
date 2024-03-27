import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from seleniumFunction import idData,gethotelId,scrollPage,getsectionLink
from selenium.webdriver.chrome.options import Options

# Set Chrome options for running in headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')  # Required when running as root user. Otherwise, you would get no sandbox errors.

class CrawlingData:
    def __init__(self):
        self.citiesData = self.citiesData()
        self.sectionData = self.sectionData()
        self.edited_sectionData = self.edited_sectionData()


    def citiesData(self):
        try:
            df = pd.read_csv('citiesData.csv')
            return df
        except FileNotFoundError:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(
                "https://www.agoda.com/vi-vn/country/vietnam.html?site_id=1891474&tag=fe872c99-9477-72c0-54cf-6841dc26bb51&gad_source=1&device=c&network=g&adid=683003463985&rand=6822283655025895958&expid=&adpos=&aud=kwd-4997135212&gclid=EAIaIQobChMIwYTniPnwhAMVPix7Bx2zCAo8EAAYASAAEgKRtvD_BwE&pslc=1")
            # CSS_SELECTOR
            time.sleep(5)
            elems = driver.find_elements(By.CSS_SELECTOR, "#all-states-container [href]")
            cities = [elem.text.split('\n')[0] for elem in elems]
            df = pd.DataFrame(cities, columns=['cityName'])
            # LINK FOR EACH CITY
            df['cityLink'] = [elem.get_attribute('href') for elem in elems]
            df.to_csv('citiesData.csv', index=False, encoding='utf-8-sig')
            return df


    def sectionData(self):
        try:
            df = pd.read_csv('sectionData.csv')
            return df
        except FileNotFoundError:
            driver = webdriver.Chrome(options=chrome_options)
            df = pd.DataFrame()
            for href,city in zip(self.citiesData.cityLink,self.citiesData.cityName):
                driver.get(href)
                time.sleep(5)
                elems = driver.find_elements(By.CSS_SELECTOR, '#neighbor-container [href]')
                section = [elem.text.split('\n')[0] for elem in elems]
                sectionLink = [elem.get_attribute('href') for elem in elems]
                data = {
                    'sectionName': section,
                    'cityName': city,
                    'sectionLink': sectionLink
                }
                df_new = pd.DataFrame(data)
                df = pd.concat([df, df_new], ignore_index=True)
            df.drop_duplicates(inplace=True)
            df.to_csv('sectionData.csv', index=False, encoding='utf-8-sig')
            return df

    def edited_sectionData(self):
        try:
            sample_df = pd.read_csv('edited_sectionData.csv')
        except FileNotFoundError:
            sample_df = self.sectionData
            sample_df['edited_sectionLink'] = ''
            sample_df.to_csv('edited_sectionData.csv', index=False, encoding='utf-8-sig')

        for _ in range(2):
            for sectionLink in sample_df.sectionLink:
                index_to_add_column = sample_df.index[sample_df['sectionLink'] == sectionLink][0]
                if sample_df['edited_sectionLink'][index_to_add_column] in ['0', '1', '']:
                    sample_df.loc[index_to_add_column, 'edited_sectionLink'] = getsectionLink(sectionLink)
                    sample_df.to_csv('sectionData1.csv', index=False, encoding='utf-8-sig')
        return sample_df








