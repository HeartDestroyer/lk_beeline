# utils/parse.py

#region imports

import os
import shutil
import time
import zipfile
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import element_to_be_clickable, presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

#endregion

def login(driver: webdriver.Chrome, login_str: str, password_str: str, url: str = "https://my.beeline.ru/login.xhtml?") -> None:
    """
    Метод для входа в ЛК Билайн
    """
    driver.get(url)

    time.sleep(2)

    login_input = driver.find_element(By.ID, "loginFormB2B:loginForm:login")
    password_input = driver.find_element(By.ID, "loginFormB2B:loginForm:passwordPwd")

    login_input.send_keys(login_str)
    password_input.send_keys(password_str)

    login_button = driver.find_element(By.ID, "loginFormB2B:loginForm:j_idt82")
    login_button.click()
    
    time.sleep(3)

def create_report(driver: webdriver.Chrome, wait: WebDriverWait, url: str = "https://my.beeline.ru/b/report/udreport.xhtml") -> None:
    """
    Метод для создания отчета в ЛК Билайн
    """
    driver.get(url)

    time.sleep(5)

    # Открываем детализацию
    driver.find_element(By.ID, "j_idt856:j_idt863").click()

    # Выбираем опции
    wait.until(element_to_be_clickable((By.ID, "udReportForm:j_idt880:selectAllBox"))).click()

    # Выбор периода
    wait.until(element_to_be_clickable((By.ID, "udReportForm:closeDateList:j_idt1061"))).click()
    wait.until(element_to_be_clickable((By.ID, "udReportForm:closeDateList:j_idt1061_1"))).click()

    # Выбор типа звонка
    wait.until(element_to_be_clickable((By.ID, "udReportForm:j_idt1120:j_idt1134:1:j_idt1135"))).click()
    time.sleep(3)
    
    wait.until(element_to_be_clickable((By.ID, "udReportForm:j_idt1120:j_idt1134:2:j_idt1135"))).click()
    time.sleep(3)
    
    wait.until(element_to_be_clickable((By.ID, "udReportForm:j_idt1120:j_idt1134:5:j_idt1135"))).click()
    time.sleep(3)
    
    element = driver.find_element(By.ID, "udReportForm:j_idt1120:j_idt1134:7:j_idt1135")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    time.sleep(1)
    element.click()

    # Заказать отчёт
    driver.find_element(By.ID, "udReportForm:j_idt1198").click()
    time.sleep(3)

    # Отправляем отчёт на сборку
    checkbox_container = driver.find_element(
        By.XPATH,
        "//div[@id='j_idt1200:requestUserServiceParamsForm:emailCheckbox']/div[contains(@class, 'ui-chkbox-box')]",
    )
    checkbox_container.click()
    driver.find_element(By.ID, "j_idt1200:requestUserServiceParamsForm:j_idt1237").click()

    time.sleep(3)

def download(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """
    Метод для скачивания файла из ЛК Билайн
    """
    request_link = wait.until(presence_of_element_located((By.XPATH, "//div[contains(@class, 'request-created')]/a")))
    
    # 6 минут ожидания формирования отчета на стороне Билайна
    time.sleep(360)
    
    driver.get(request_link.get_attribute("href"))
    download_button = wait.until(element_to_be_clickable((By.ID, "j_idt343:j_idt424:0:j_idt440")))
    download_button.click()
    
    # 3 минуты на скачивание файла
    time.sleep(180)

def read_file(path: str) -> list[str]:
    """
    Метод для чтения файла из директории
    """
    files = os.listdir(path)
    if not files:
        raise FileNotFoundError("В директории нет скачанных файлов")
        
    file_path = Path(path) / files[0]
    
    if file_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(file_path.resolve(), "r") as zip_ref:
            with zip_ref.open(zip_ref.filelist[0].filename) as file:
                return file.read().decode("cp1251").splitlines()
                
    with file_path.open("rb") as file:
        return file.read().decode("cp1251").splitlines()

def parse_from_lk(lk_login: str, password: str) -> list[str]:
    """
    Метод для парсинга данных из ЛК Билайн
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    path = os.path.join(os.getcwd(), "download")
    prefs = {
        "download.default_directory": path,
        "directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options = options)
    wait = WebDriverWait(driver, 120)

    try:
        login(driver, lk_login, password)

        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok = True)

        create_report(driver, wait)
        download(driver, wait)

        return read_file(path)
    finally:
        driver.close()
        driver.quit()
