from selenium import webdriver
from selenium.common import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class SongsFinder:

    def __init__(self, email: str, password: str):
        # init selenium webdriver
        self.__choice = None
        self.__driver = webdriver.Chrome()
        self.__driver.maximize_window()
        self.__driver.get("https://open.spotify.com/collection/tracks")

        # enter login page
        self.__login_label = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[3]/div/div[2]/div[1]/header/div[5]/button[2]')))
        self.__login_label.click()

        # login
        self.__login(email, password)

        time.sleep(1)
        # close cookies info
        self.__cookie_button = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
        self.__cookie_button.click()

        # select only playlists to show on the left bar
        playlist_button = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/nav/div[2]/div[1]/div[1]/div/div/div[1]/div/button[1]')))
        playlist_button.click()

        time.sleep(1)
        self.__init_playlists()
        self.__driver.minimize_window()

    def __login(self, email, password):
        login_input = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable(
            (By.ID, 'login-username')))
        login_input.send_keys(email)

        passw_input = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable(
            (By.ID, 'login-password')))
        passw_input.send_keys(password)

        login_button = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="login-button"]/span[1]')))
        login_button.click()

        time.sleep(0.5)
        try:
            self.__driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div/div[1]/div/span')
        except NoSuchElementException:
            return

        print("Invalid data")
        self.__driver.close()

    def __init_playlists(self):
        # get all playlists
        elements = self.__driver.find_elements(By.CSS_SELECTOR, "li[role = 'listitem'] span")
        elements.pop(1)
        elements = [item for item in elements if len(item.text) > 0]
        elements = elements[1::2]
        self.__playlists = {i: elements[i] for i in range(len(elements))}

    def get_songs(self):
        for key, value in self.__playlists.items():
            print(str(key) + ": " + value.text)

        # choice a playlist to download
        choice = input("Enter a playlist number ('q' to exit): ")
        try:
            choice = int(choice)
        except ValueError:
            return -1

        # select first clickable parent element, to enter a playlist
        el = WebDriverWait(self.__playlists[choice], 10).until(EC.visibility_of_element_located((By.XPATH, '..')))
        while True:
            try:
                el = el.find_element(by=By.XPATH, value='..')
                el.click()
                break
            except ElementClickInterceptedException:
                pass

        songs = []
        # try to get main playlist grid where song titles are located
        try:
            main_playlist_grid = WebDriverWait(self.__driver, 5).until(EC.visibility_of_element_located(
                (By.XPATH,
                 '//*[@id="main"]/div/div[2]/div[4]/div[1]/div[2]/div[2]/div/div/div[2]/main/div[1]/section/div[2]/div[3]/div[1]/div[2]/div[2]')))
        except TimeoutException:

            # try to click return button from folder
            try:
                back_arrow = WebDriverWait(self.__driver, 5).until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/nav/div[2]/div[1]/div[1]/header/div/div/button[2]')))
                back_arrow.click()
                time.sleep(1)
                print("IT IS FOLDER NOT A PLAYLIST")
                self.__init_playlists()
                return None
            except TimeoutException:
                pass

            print("NO SONGS FOUND IN A PLAYLIST")
            return None

        last_element = None

        # get song titles and artists
        while True:
            temp = self.__driver.find_elements(by=By.CSS_SELECTOR, value="a div[dir='auto']")
            for item in temp:
                parent = item.find_element(by=By.XPATH, value='..')
                parent = parent.find_element(by=By.XPATH, value='..')
                try:
                    artist = parent.find_element(by=By.CSS_SELECTOR, value="span a[dir='auto']")
                except NoSuchElementException:
                    print("Song imported to spotify, skipped")
                    continue
                item = str(item.text + " - " + artist.text)
                songs.append(item)

            self.__driver.maximize_window()

            # scroll to bottom, in order to render all elements
            new_elements = main_playlist_grid.find_elements(by=By.CSS_SELECTOR, value='div[role="row"]')
            if new_elements[-1] == last_element:
                number_of_songs = int(last_element.get_attribute("aria-rowindex")) - 1
                break
            last_element = new_elements[-1]

            ActionChains(self.__driver).scroll_to_element(new_elements[-1]).perform()
            time.sleep(0.5)

        self.__driver.minimize_window()
        # remove duplicates from the list
        songs = list(dict.fromkeys(songs))
        return songs, self.__playlists[choice], number_of_songs
