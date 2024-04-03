import pandas as pd
import time
import os
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
# from seleniumFunction import *
from selenium.webdriver.chrome.options import Options


# ==================== GLOBAL VARIABLES
# Set Chrome options:
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox') 
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-application-cache")
chrome_options.add_argument("--disable-cache")
chrome_options.add_argument("--disk-cache-size=0")


#==================== CLASS:
class CrawlingData:
    def __init__(self):
        self.citiesData = self.citiesData()
        self.sectionData = self.sectionData()
        self.edited_sectionData = self.edited_sectionData()
        for sectionName,sectionLink in zip(self.edited_sectionData.sectionName,self.edited_sectionData.edited_sectionLink):
            hotelId(sectionName,sectionLink)
            # gethotelInfos(sectionName)
        # print(self.edited_sectionData.sectionName[21],self.edited_sectionData.edited_sectionLink[21])
        # hotelId(self.edited_sectionData.sectionName[21],self.edited_sectionData.edited_sectionLink[21])
        # gethotelInfos(self.edited_sectionData.sectionName[21]) 
        # All hotel reviews
        # sectionNames = [self.edited_sectionData.sectionName[21]]
        # folder_path = "hotelData"
        # files = os.listdir(folder_path)
        # sectionNames = [sectionName.split('.')[0] for sectionName in files]
        # hotelReviews(sectionNames)


    def citiesData(self):
        try:
            df = pd.read_csv('dataset/citiesData.csv')
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
            df = pd.read_csv('dataset/sectionData.csv')
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
            sample_df = pd.read_csv('dataset/edited_sectionData.csv')
        except FileNotFoundError:
            sample_df = self.sectionData
            sample_df['edited_sectionLink'] = ''
            sample_df.to_csv('edited_sectionData.csv', index=False, encoding='utf-8-sig')

            for _ in range(5):
                for sectionLink in sample_df.sectionLink:
                    index_to_add_column = sample_df.index[sample_df['sectionLink'] == sectionLink][0]
                    if sample_df['edited_sectionLink'][index_to_add_column] in ['0', '1', '']:
                        sample_df.loc[index_to_add_column, 'edited_sectionLink'] = getsectionLink(sectionLink)
                        sample_df.to_csv('sectionData1.csv', index=False, encoding='utf-8-sig')
        return sample_df



#====================== FUNCTIONS    
def scrollPage(driver: webdriver):
    scroll_step = 100

    scroll_position = 0

    # Loop until reaching the end of the page
    while True:
        # Scroll down by the scroll step
        driver.execute_script("window.scrollTo(0, {});".format(scroll_position))

        # Update the scroll position
        scroll_position += scroll_step

        # Break the loop if reaching the end of the page
        if scroll_position >= driver.execute_script("return document.body.scrollHeight"):
            break

    # Set it back to see the next page button
    end_position = driver.execute_script("return document.body.scrollHeight") - 800
    driver.execute_script("window.scrollTo(0, {});".format(end_position))


def getsectionLink(link):
    driver = webdriver.Chrome()
    try: 
        driver.get(link)
        backdrop = driver.find_element(By.CSS_SELECTOR, ".SearchboxBackdrop")
        # Execute JavaScript to remove the element from the DOM
        driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", backdrop)
        time.sleep(5)
        button = driver.find_element(By.XPATH, '//*[@id="contentReact"]/article/div[1]/div/div[2]/div[3]/button/div')
        button.click();
    except NoSuchElementException as e:
        return 0
    except WebDriverException as e:
        return 1
    time.sleep(5)
    current_url = driver.current_url
    return current_url


# def appendCSV(new_data, file_path):
#     try:
#         # Read existing data from CSV file (if it exists)
#         existing_df = pd.read_csv(file_path)
#     except FileNotFoundError:
#         # If the file doesn't exist, create an empty DataFrame
#         existing_df = pd.DataFrame()
#     print(existing_df.head())
#     # Append new data to existing DataFrame
#     existing_df = pd.concat([existing_df, new_data], ignore_index=True)
#     # Save the updated DataFrame back to the CSV file
#     existing_df.to_csv(file_path, index=False, encoding='utf-8-sig')


def appendCSV(data: dict, filepath:str, first = False):
    if len(filepath.split('/')) > 1:
        directory = '/'.join(filepath.split('/')[:-1])
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        if first == False:
            with open(filepath, mode='a', newline='',encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=data.keys())
                
                # Write the header (fieldnames)
        #         writer.writeheader()

                # Determine the number of rows (length of any list in the dictionary)
                num_rows = len(next(iter(data.values())))
                
                # Write each row of data
                for i in range(num_rows):
                    row = {key: data[key][i] for key in data.keys()}
                    writer.writerow(row)
        else:


            with open(filepath, mode='w', newline='',encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=data.keys())
                
                # Write the header (fieldnames)
                writer.writeheader()

                # Determine the number of rows (length of any list in the dictionary)
                num_rows = len(next(iter(data.values())))
                
                # Write each row of data
                for i in range(num_rows):
                    row = {key: data[key][i] for key in data.keys()}
                    writer.writerow(row)
    except AttributeError:
        with open(filepath, mode='w', newline='') as file:
            pass
            

def idData(driver: webdriver, hotelId: list):
    hotelLink = []
    for id in hotelId:
        elem = driver.find_element(By.CSS_SELECTOR, f'a[property-id="{id}"]')
        hotelLink.append(elem.get_attribute('href'))
    data = {
        'hotelId': hotelId,
        'hotelLink': hotelLink
    }
    # df = pd.DataFrame(data)
    return data
        
             
def hotelId(sectionName,sectionLink): # Link
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(sectionLink)
    time.sleep(5)
    
    if not os.path.exists("hotelData"):
        os.makedirs("hotelData")

    scrollPage(driver)
    pageNum = int((driver.find_element(By.CSS_SELECTOR, 'div[data-selenium="pagination"]').text).split()[3])
    # Create empty DataFrame
    elements = driver.find_elements(By.CSS_SELECTOR, 'li[data-selenium="hotel-item"]')
    hotelId = [element.get_attribute("data-hotelid") for element in elements]
    data = idData(driver, hotelId)
    file_path = f"hotelData/{sectionName}.csv"
    # Save the filtered DataFrame to a CSV file
    appendCSV(data,file_path,first = True)
        
    # For loop for second page -->
    for _ in range(pageNum - 1):
        try:
            time.sleep(5)
            # Loop until reaching the end of the page
            scrollPage(driver)
            elements = driver.find_elements(By.CSS_SELECTOR, 'li[data-selenium="hotel-item"]')
            hotelId = [element.get_attribute("data-hotelid") for element in elements]
            data = idData(driver, hotelId)
            appendCSV(data, file_path)            
            # button = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-selenium="pagination-next-btn"]'))
            # )
            
            time.sleep(2)
            button = driver.find_element(By.CSS_SELECTOR, 'button[data-selenium="pagination-next-btn"]')
            button.click()
        except Exception as e:
            print('Done',sectionName)
            print("Break for loop",e)
            break


def reviewInfomation(driver: webdriver):
    try:
        # DateTime
        dates = driver.find_elements(By.CSS_SELECTOR, 'span[class="Review-statusBar-date "]')
        date = [date.text for date in dates]
            # Filtering
        phrase = "Đã nhận xét vào"
        date = [each for each in date if each.startswith(phrase)]
        reviewDate = [" ".join(day.split(" ")[4:]) for day in date]

        # ReviewersInfo
        reviewersInfo = driver.find_elements(By.CSS_SELECTOR, 'div[data-info-type="reviewer-name"]')
        infos = [reviewerInfo.text for reviewerInfo in reviewersInfo]
        reviewerName = [info.split(" ")[0] for info in infos]
        national = [" ".join(info.split(" ")[2:4]) for info in infos]

        # GroupsName
        groupsName = driver.find_elements(By.CSS_SELECTOR, 'div[data-info-type="group-name"]')
        group = [groupName.text for groupName in groupsName]

        # RoomTypes
        # roomsType = driver.find_elements(By.CSS_SELECTOR, 'div[data-info-type="room-type"]')
        # room = [roomType.text for roomType in roomsType]

        # StaysDetail
        staysDetail = driver.find_elements(By.CSS_SELECTOR, 'div[data-info-type="stay-detail"]')
        stay = [stayDetail.text for stayDetail in staysDetail]
        
        # Review Title:
        reviewtitles = driver.find_elements(By.CSS_SELECTOR, 'h3[data-testid="review-title"]')
        reviewtitle = [reviewtitle.text for reviewtitle in reviewtitles]
        
        # Comments
        comments = driver.find_elements(By.CSS_SELECTOR, 'p[data-selenium="comment"]')
        comment = [comment.text for comment in comments]

        # Scores
        scores = driver.find_elements(By.CSS_SELECTOR, 'div[class="Review-comment-leftScore"]')
        score = [score.text for score in scores]

        data = {
            'reviewDate': reviewDate,
            'reviewerName': reviewerName,
            'national': national,
            'groupName': group,
            # 'roomType': room,
            'reviewTitle': reviewtitle,
            'comment':comment,
            'score': score
        }
        # df = pd.DataFrame(data)
        return data
    except:
        pass

    

def hotelReviews(sectionNames):
    for sectionName in sectionNames:
        section_df = pd.read_csv(f"hotelData/{sectionName}.csv")
        for hotelId,hotelLink in zip(section_df.hotelId,section_df.hotelLink):
            hotel = "/".join([sectionName,str(hotelId)])
            file_path = f"HotelReview/{hotel}.csv"
            if not os.path.exists(file_path):
                driver = webdriver.Chrome()
                driver.get(hotelLink)
                while True:
                    data = reviewInfomation(driver)
                    appendCSV(data,file_path)
                    try:
                        button = driver.find_element(By.CSS_SELECTOR, 'i.ficon.ficon-24.ficon-carrouselarrow-right' )
                        # Move it to button element to able to click
                        driver.execute_script("arguments[0].scrollIntoView(); window.scrollBy(0, -200);", button)
                        time.sleep(2)
                        button.click()
                    except Exception as e:
                        break


def gethotelInfos(sectionName):
    file_path = f"hotelData/{sectionName}.csv"
    df = pd.read_csv(file_path)
    for hotelLink in df.hotelLink:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(hotelLink)
        time.sleep(5)
        hotelName = driver.find_element(By.CSS_SELECTOR, 'p[data-selenium="hotel-header-name"]').text
        hotelAddress = driver.find_element(By.CSS_SELECTOR, 'span[data-selenium="hotel-address-map"]').text
        index_to_add_column = df.index[df['hotelLink'] == hotelLink][0]
        df.loc[index_to_add_column, 'hotelName'] = hotelName
        df.loc[index_to_add_column, 'hotelAddress'] = hotelAddress
        df.to_csv(file_path, index=False, encoding='utf-8-sig')