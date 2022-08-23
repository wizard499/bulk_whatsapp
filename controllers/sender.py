from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--profile-directory=Default")
options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

os.system("")
os.environ["WDM_LOG_LEVEL"] = "0"


class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def start(numbers, message="Hello there!"):
    sent_success,failures= [],[]
    delay = 15

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get('https://web.whatsapp.com')
    for idx, number in enumerate(numbers):
        number = number[1]
        if number == "":
            continue
        try:
            url = 'https://web.whatsapp.com/send?phone=' + number + '&text=' + message
            sent = False
            for i in range(1):
                if not sent:
                    driver.get(url)
                    try:
                        click_btn = WebDriverWait(driver, delay).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='compose-btn-send']")))
                    except Exception as e:
                        failures.append(number)
                        print(style.RED + f"\nFailed to send message to: {number}, retry ({i + 1}/3)")
                        print("Make sure your phone and computer is connected to the internet.")
                        print("If there is an alert, please dismiss it." + style.RESET)
                    else:
                        sleep(1)
                        click_btn.click()
                        sent = True
                        sent_success.append(number)
                        sleep(3)
                        print(style.GREEN + 'Message sent to: ' + number + style.RESET)
        except Exception as e:
            print(style.RED + 'Failed to send message to ' + number + str(e) + style.RESET)
    driver.close()
    return sent_success,failures
