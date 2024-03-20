from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import numpy as np
import pandas as pd
import time

# Set Chrome options for running in headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')  # Required when running as root user. Otherwise, you would get no sandbox errors.


def scrollPage(driver: webdriver):
    scroll_step = 50

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
    driver.get(link)

    backdrop = driver.find_element(By.CSS_SELECTOR, ".SearchboxBackdrop")
    # Execute JavaScript to remove the element from the DOM
    driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", backdrop)

    time.sleep(5)
    button = driver.find_element(By.XPATH, '//*[@id="contentReact"]/article/div[1]/div/div[2]/div[3]/button/div')
    button.click();
    time.sleep(5)
    current_url = driver.current_url
    return current_url



def gethotelId(sectionLink): # Link
    driver = webdriver.Chrome()
    driver.get(sectionLink)
    scrollPage(driver)
    pageNum = int((driver.find_element(By.CSS_SELECTOR, 'div[data-selenium="pagination"]').text).split()[3])
    # Create empty DataFrame
    elements = driver.find_elements(By.CSS_SELECTOR, 'li[data-selenium="hotel-item"]')
    hotelId = [element.get_attribute("data-hotelid") for element in elements]
    df = idData(driver, hotelId)
    # For loop for second page -->
    for _ in range(pageNum - 1):
        # Loop until reaching the end of the page
        scrollPage(driver)
        time.sleep(5)
        elements = driver.find_elements(By.CSS_SELECTOR, 'li[data-selenium="hotel-item"]')
        hotelId = [element.get_attribute("data-hotelid") for element in elements]
        df_new = idData(driver, hotelId)
        df = pd.concat([df, df_new], ignore_index=True)
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-selenium="pagination-next-btn"]'))
            )
            button.click()
        except Exception as e:
            print(f"An error occurred: {e}")
    return df


def idData(driver: webdriver, hotelId: list):
    hotelLink = []
    for id in hotelId:
        elem = driver.find_element(By.CSS_SELECTOR, f'a[property-id="{id}"]')
        hotelLink.append(elem.get_attribute('href'))
    data = {
        'hotelId': hotelId,
        'hotelLink': hotelLink
    }
    df = pd.DataFrame(data)
    return df

def reviewInfomation(driver: webdriver):
    try:
        # DateTime
        dates = driver.find_elements(By.CSS_SELECTOR, 'span[class="Review-statusBar-date "]')
        date = [date.text for date in dates]
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
        roomsType = driver.find_elements(By.CSS_SELECTOR, 'div[data-info-type="room-type"]')
        room = [roomType.text for roomType in roomsType]

        # StaysDetail
        staysDetail = driver.find_elements(By.CSS_SELECTOR, 'div[data-info-type="stay-detail"]')
        stay = [stayDetail.text for stayDetail in staysDetail]

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
            'roomType': room,
            'comment':comment,
            'score': score
        }
        df = pd.DataFrame(data)
        return df
    except:
        print('There are something missing...')