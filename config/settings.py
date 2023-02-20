# import os
# # bot father
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
#
# options = Options()
# options.headless = True
# options.add_argument("--window-size=1920,1200")
#
#
# dir_path = os.path.dirname(os.path.realpath(__file__))
# DRIVER_PATH = os.path.join(dir_path, 'chromedriver')
# driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

PROF_INFO = {
    'username': "alevtinanur89@gmail.com",
    'password': "Dmitrii19891989!"
}

DB_INFO = {
    'host': "localhost",
    'user': "admin_bot",
    'password': "123",
    'db_name': "base_bot"
}
PG_URL = f'postgresql: //{DB_INFO.get("user")}:{DB_INFO.get("password")}@{DB_INFO.get("host")}/{DB_INFO.get("db_name")}'

# options = Options()
# # options = webdriver.ChromeOptions()
# options.headless = False
# # options.add_argument("--window-size=1920,1200")
#
# #Local\Google\Chrome\User Data
# options.add_argument("user-data-dir=C:\\Users\\User\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
# # options.add_argument("user-data-dir=~/Library/Application Support/Google/Chrome/Default")
# dir_path = os.path.dirname(os.path.realpath(__file__))
# DRIVER_PATH = os.path.join(dir_path, 'chromedriver')
# driver = None
# driver.minimize_window()
# driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
# driver.minimize_window()