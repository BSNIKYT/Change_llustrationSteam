import os
import time
import json
import random
import urllib
import shutil
import zipfile
import platform
import selenium
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


database = [
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3174974573',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3174975992',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=2925651080',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3177699585',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3177692126',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3177689204',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3177683242',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3177679918',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3177677644',
    'https://steamcommunity.com/sharedfiles/filedetails/?id=3177675403'
]

index_to_remove = 0


class NotFoundSuitableDriver(Exception):
    """Exception raised when no suitable driver is found."""
    pass


class NotLoginOrPasswordException(Exception):
    """Exception raised when login or password is not provided."""
    pass


class SteamLoginError(Exception):
    """Exception raised when there's an error during Steam login."""
    pass


class SteamDirrectoryNotfoundError(Exception):
    """Exception raised when the Steam directory is not found."""
    pass


win_driver_download_path = 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win%2F1217046%2Fchromedriver_win32.zip?generation=1698692359126601&alt=media'
lin_driver_download_path = 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1217044%2Fchromedriver_linux64.zip?generation=1698689249131026&alt=media'


class TwoFactorAuth():
    """Class to handle two-factor authentication."""

    def __init__(self, logger, login, INIT):
        """
        Initialize TwoFactorAuth class.

        Args:
            logger: The logger instance.
        """
        self.logger = logger
        self.login = login
        self.is_login_error_exists = INIT.is_login_error_exists
        self.is_2Fauth = INIT.is_2Fauth
        self.auth_ = False
        self.logger.info(
            text=f'TwoFactorAuth() has been initialized',
            login=login)
        self.priorities = [
            "Steam_mobile_element",
            "authentication_code_element"]  # , "passkey_element"]

    def auth(self, driver):
        """
        Authenticate the user with different methods.

        Args:
            driver: The Selenium WebDriver instance for interacting with the web page.
        """
        for priority in self.priorities:
            try:
                element = getattr(self, priority)
                element(driver)
                if self.auth_:
                    self.logger.debug(
                        text=f"[2FA][TwoFactorAuth] Authentication succeeded using {priority}.",
                        login=self.login)
                    break
            except SteamLoginError as err:
                raise SteamLoginError(err)
            except Exception as e:
                print(e)
                driver.save_screenshot('screenshot_2FAError.png')
                continue

    def Steam_mobile_element(self, driver):
        """
        Authenticate using Steam Mobile method.

        Args:
            driver: The Selenium WebDriver instance.
        """
        challenge_value_element = driver.find_element(
            By.CLASS_NAME, '_1mhmmseSBKL7v66ts9ZWnR').find_element(
            By.CLASS_NAME, '_7LmnTPGNvHEfRVizEiGEV')
        challenge_value = challenge_value_element.text.strip(
        ) if challenge_value_element else None

        self.logger.info(
            text=f"[2FA][SteamMobile] {challenge_value}",
            login=self.login)
        self.auth_ = False

        status = 'None'
        while status not in ('OK', 'Keyboard'):
            try:
                time.sleep(2)
                if self.is_2Fauth():
                    challenge_value_element = driver.find_element(
                        By.CLASS_NAME, '_1mhmmseSBKL7v66ts9ZWnR').find_element(
                        By.CLASS_NAME, '_7LmnTPGNvHEfRVizEiGEV')
                    challenge_value = challenge_value_element.text.strip(
                    ) if challenge_value_element else None
                    self.logger.debug(
                        text=f'[2FA][SteamMobile] {challenge_value}',
                        login=self.login)
                    if self.is_login_error_exists():
                        self.auth_ = False
                    else:
                        self.auth_ = True

                else:
                    status = 'OK'
                    self.auth_ = True
                    break
            except KeyboardInterrupt:
                self.logger.error(
                    text="[2FA][SteamMobile] KeyboardInterrupt",
                    login=self.login)
                status = 'Keyboard'
                break

    def authentication_code_element(self, driver):
        """
        Authenticate using an authentication code.

        Args:
            driver: The Selenium WebDriver instance.
        """
        authentication_code_element = driver.find_element(
            By.XPATH, "//div[contains(text(), 'Или введите код')]")
        authentication_code_element.click()

        def send_new_code(code):
            input_elements = driver.find_elements(
                By.CLASS_NAME, 'HPSuAjHOkNfMHwURXTns7')


            text_to_enter = code  # Ваш текст для ввода
            for i in range(min(len(input_elements), len(text_to_enter))):
                input_elements[i].send_keys(text_to_enter[i])

        def while_ok_or_keyboard():
            status = 'None'
            while status not in ('OK', 'Keyboard'):
                try:
                    time.sleep(0.5)
                    if self.is_2Fauth():
                        code = input(
                            '[2FA][Authenticator] Enter code from authenticator: ')
                        self.logger.debug(
                            f'[2FA][Authenticator] Enter code from authenticator: {code}', self.login)
                        send_new_code(code)
                        if self.is_login_error_exists():
                            self.auth_ = False
                        else:
                            self.auth_ = True
                    else:
                        self.logger.info(
                            tet='[2FA][Authenticator] Successfully authenticated',
                            login=self.login)
                        status = 'OK'
                        self.auth_ = True
                        break
                except KeyboardInterrupt:
                    self.logger.error(
                        text="[2FA][Authenticator] KeyboardInterrupt",
                        login=self.login)
                    status = 'Keyboard'
                    break

        while_ok_or_keyboard()



class InCodeLogger():
    def __init__(self, login='None', logger=None):
        self.login = login
        self.logger = logger
        if logger is not None:
            pass
        else:
            class LR():
                def __init__(self, login='None', print_bool=True):
                    self.login = login
                    self.DEBUG = True
                    self.print_bool = print_bool

                def info(self, login, text, *args):
                    val = 'INFO'
                    self.write(val, login, text, *args)

                def debug(self, login, text, *args):
                    val = 'DEBUG'
                    self.write(val, login, text, *args)

                def error(self, login, text, *args):
                    val = 'ERROR'
                    self.write(val, login, text, *args)

                def write(self, val, login, text, *args):
                    if self.print_bool:
                        debug_enabled = self.DEBUG
                        # if val != 'DEBUG' or debug_enabled or val == 'INFO':
                        if True:
                            if args != ():
                                print(f"[{val}][{login}] {text} # {args}")
                            else:
                                print(f"[{val}][{login}] {text}")

            self.logger = LR(login)
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.error = self.logger.error


class DownloadDriver():
    def check(self):
        if self.platform_system == 'Windows' or self.platform_system == 'Linux':
            if self.platform_system == 'Windows':
                driver_path = os.path.join(
                    self.WDir,
                    'modules',
                    'chromedriver',
                    'Windows',
                    'chromedriver.exe')
            elif self.platform_system == 'Linux':
                driver_path = os.path.join(
                    self.WDir, 'modules', 'chromedriver', 'Linux', 'chromedriver')
            elif platform.machine().startswith('arm'):
                driver_path = os.path.join(
                    '/usr/lib/chromium-browser/chromedriver')

            if not os.path.exists(driver_path):
                try:
                    self.exc_chrome_driver_filepath = os.path.dirname(
                        driver_path)
                    if not os.path.exists(self.exc_chrome_driver_filepath):
                        os.makedirs(self.exc_chrome_driver_filepath)

                    os.chdir(self.exc_chrome_driver_filepath)
                    self.download()
                    self.unzip()
                    os.chdir(self.WDir)

                    return True
                except Exception as err:
                    print(f"Error: {err}")
                    return False
            else:
                return True
        else:
            raise NotFoundSuitableDriver(
                'Unknown platform system %s' %
                self.platform_system, 'None')

    def __init__(self, logger):
        self.logger = logger
        self.WDir = os.path.join(os.getcwd())
        self.platform_system = platform.system()
        self.installed = self.check()
        self.logger.debug(
            text='Initial DownloadDriver().platform is %s' %
            self.platform_system, login='None')

    def download(self):
        if self.platform_system == 'Windows':
            url = win_driver_download_path
        elif self.platform_system == 'Linux':
            url = lin_driver_download_path
        urllib.request.urlretrieve(url, 'chromedriver.zip')

    def unzip(self):
        try:
            with zipfile.ZipFile('chromedriver.zip', 'r') as zip_ref:
                zip_ref.extractall('.')
                all_files = zip_ref.namelist()
                extracted_folder = all_files[0].split('/')[0]
                source_dir = os.path.join(os.getcwd(), extracted_folder)
                target_dir = self.exc_chrome_driver_filepath

                for item in all_files:
                    item_path = os.path.join(os.getcwd(), item)
                    if os.path.isfile(item_path):
                        shutil.move(item_path, target_dir)

                os.rmdir(source_dir)

        except Exception as err:
            print(f"Error while unzipping: {err}")

        finally:
            os.remove('chromedriver.zip')

    def move_files(self, source_dir):
        current_dir = os.getcwd()
        source_path = os.path.join(current_dir, source_dir)

        if os.path.exists(source_path) and os.path.isdir(source_path):
            files = os.listdir(source_path)
            for file in files:
                file_path = os.path.join(source_path, file)
                if os.path.isfile(file_path):
                    shutil.move(file_path, current_dir)
                elif os.path.isdir(file_path):
                    self.move_files(file_path)


class InitLogin():
    def __init__(self, logger, login, password, warnings_ignore, reconnect):
        self.logger = logger
        self.login = login
        self.password = password
        self.warnings_ignore = warnings_ignore
        self.reconnect = reconnect
        self.desetup()
        self._login()
        self.start()

    def setup_service(self):
        if platform.system() == 'Windows':
            service = Service(
                executable_path=os.path.join(
                    os.getcwd(),
                    'modules',
                    'chromedriver',
                    'Windows',
                    'chromedriver.exe'))
        elif platform.system() == 'Linux':
            service = Service(
                executable_path=os.path.join(
                    os.getcwd(),
                    'modules',
                    'chromedriver',
                    'Linux',
                    'chromedriver'))
        else:
            service = None
        return service


    def desetup(self):
        service = self.setup_service()
        options = webdriver.ChromeOptions()
        for option in [
                "window-size=1200x600", '--log-level=3']:  # '--headless'
            options.add_argument(option)

        try:
            if service is not None:
                self.driver = webdriver.Chrome(
                    service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            self.logger.debug(
                text=f'Initial InitLogin().get called with servise: {service}',
                login=self.login)
        except selenium.common.exceptions.NoSuchDriverException as err:
            installed = DownloadDriver(self.logger).installed
            self.logger.error(
                text=f'Driver is not installed: {installed}',
                login='None')
            if not installed:
                print('[SELENIUM] Chrome driver has not been installed!')
                return
            return InitLogin(self.logger, self.login, self.password).get()

    def _login(self):
        driver = self.driver
        self.logger.info(
            text=f'Initial InitLogin().get called with login: {self.login}',
            login=self.login)
        driver.get(
            'https://steamcommunity.com/profiles/76561199651395850/edit/showcases')
        form_locator = (By.CLASS_NAME, "_3Tsg92fl5YHs5NNgpidiWj")
        form = WebDriverWait(
            driver, 15).until(
            EC.presence_of_element_located(form_locator))

        username_input = form.find_element(
            By.CLASS_NAME, "_2eKVn6g5Yysx9JmutQe7WV")
        username_input.send_keys(self.login)

        password_input = form.find_element(
            By.XPATH, "//input[@type='password']")
        password_input.send_keys(self.password)

        login_button = form.find_element(
            By.CSS_SELECTOR, "button[type='submit']")

        time.sleep(5)

        login_button.click()
        driver.implicitly_wait(10)

        driver.implicitly_wait(5)

        if self.is_many_requests():
            self.logger.error(text=f'Many requests', login=self.login)
            raise SteamLoginError('Many requests')

        if self.is_login_error_exists():
            self.logger.error(
                text=f'Password or username is incorrect',
                login=self.login)
            raise SteamLoginError('Password or username is incorrect')

        if self.time_is_up():
            self.logger.error(text=f'Time is up', login=self.login)
            raise SteamLoginError('Time is up')

        self.auth = False
        two_factor_auth = self.is_2Fauth()


        try:
            if two_factor_auth:
                TWA = TwoFactorAuth(self.logger, self.login, self)
                TWA.auth(driver)
                self.auth = TWA.auth_
            else:
                self.auth = True
        except SteamLoginError as e:
            self.auth = False

        if self.auth:
            self.logger.info(
                text=f'Authentication success by {self.login}',
                login=self.login)
            time.sleep(5)
            self.driver.refresh()
            self.working_link = driver.current_url
            self.driver.get(self.working_link)

            self.driver.refresh()
            self.working_link = driver.current_url
        else:
            self.logger.info(
                text=f'Authentication failed by {self.login}',
                login=self.login)

    def start(self):
        if self.auth:
            driver = self.driver

            # driver.get(driver.current_url.replace("/edit/showcases", "/edit/info"))

            actual_links = []
            for link in database:
                ll = self.get_illustration_server_name(link)
                # print('ll',ll)
                actual_links.append({link: ll})

            driver.get(self.working_link)
            time.sleep(5)

            if self.get_lens_bard() > 0:
                self.logger.info(
                    text=f'Count of custom storefronts: {self.get_lens_bard()}',
                    login=self.login)
                self.logger.info(
                    text=f'Link to custom storefront: {self.get_link_illustration()}',
                    login=self.login)
                self.COUNT = 0
                self.SUCCESS = None
                self.start_loop()
            else:
                self.logger.error(
                    text=f'Custom storefronts not found',
                    login=self.login)
                driver.quit()

    def start_loop(self):
        while True:
            out = self.click_illustration()
            if out == 'NotFoundIllustration':
                self.SUCCESS = False
                self.logger.error(
                    text='Illustration not found',
                    login=self.login)

                driver = self.driver

                self.driver.save_screenshot(
                    'screenshot_NotFoundIllustration.png')

                select_elements = driver.find_elements(
                    By.CSS_SELECTOR, "select[name='profile_showcase[]']")

                selected_descriptions = []

                for ind, select_element in enumerate(select_elements, start=1):
                    selected_index = select_element.get_property(
                        "selectedIndex")
                    selected_option = select_element.find_elements(
                        By.TAG_NAME, "option")[selected_index]
                    selected_description = selected_option.get_attribute(
                        "title")
                    selected_descriptions.append(selected_description)


                for ind, description in enumerate(
                        selected_descriptions, start=1):
                    print(f'[INDEX] {ind}) {description}')

                while True:
                    try:
                        index_to_remove = int(
                            input('[INDEX] Введите индекс элемента для замены: '))
                        if 0 < index_to_remove <= len(selected_descriptions):
                            print(index_to_remove)
                            break
                        else:
                            print('Такого индекса нет')
                    except ValueError:
                        print('Пожалуйста, введите целое число.')

                    except KeyboardInterrupt:
                        break

                for ind, select_element in enumerate(select_elements, start=1):
                    print(ind, select_elements)
                    if ind == int(index_to_remove):
                        Select(select_element).select_by_visible_text(
                            "Витрина иллюстраций")
                        self.edit_save()
                        self.SUCCESS = False
                        continue


            time.sleep(10)
            random_image = self.get_random_image_url()
            self.SUCCESS = None
            try:
                out = self.click_illustration_by_link(random_image)
                if out == 'NotFoundError':
                    self.close_frame()
                    self.logger.error(
                        text=f'Image not found: {random_image}',
                        login=self.login)

                else:
                    time.sleep(4)
                    self.edit_save()
                    self.SUCCESS = True
                    self.logger.info(
                        text=f'[{self.COUNT}] Success changed image....',
                        login=self.login)
            except selenium.common.exceptions.NoSuchElementException:
                self.SUCCESS = False
                self.driver.save_screenshot('screenshot_main.png')
                try:
                    time.sleep(2)
                    self.close_frame()
                except BaseException:
                    self.driver.refresh()
                self.count_error += 1
                self.logger.info(
                    text=f'[{self.COUNT}] Error changed image....',
                    login=self.login)
            self.COUNT += 1
            time.sleep(60)


    def get_random_image_url(self):

        try:
            image_urls = database
            for image_url in image_urls:
                if image_url == '':
                    image_urls.remove(image_url)
                elif image_url is None:
                    image_urls.remove(image_url)
                elif image_url == 'None':
                    image_urls.remove(image_url)
                elif 'error' in image_url.capitalize():
                    image_urls.remove(image_url)

            if image_urls:
                random_image_url = random.choice(image_urls)
                self.logger.debug(
                    text=f'(get_random_image_url) Random Image URL: {random_image_url}',
                    login=self.login)
                return random_image_url
            else:

                self.logger.debug(
                    text=f'(get_random_image_url) No images found',
                    login=self.login)
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None


    def edit_save(self):
        '''Метод для сохранения изменений'''

        time.sleep(3)

        save_button = WebDriverWait(
            self.driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Сохранить')]")))

        save_button.click()

        self.logger.debug(text='Successfully saved changes', login=self.login)

    def get_illustrations(self):

        iframe = self.driver.find_element(
            By.CLASS_NAME, "publishedfile_modal_iframe")
        self.driver.switch_to.frame(iframe)
        self.logger.debug(
            text=f'(get_illustrations) Switched to iframe...',
            login=self.login)


        imgs = []
        try:
            images = WebDriverWait(
                self.driver,
                10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     ".publishedfile_popup_items .publishedfile_popup_screenshot img")))
            self.logger.debug(
                text=f'(get_illustrations) Successfully got frame images...',
                login=self.login)
            for image in images:
                src = image.get_attribute("src")
                self.logger.debug(
                    text=f'(get_illustrations) Successfully got frame image... {src}',
                    logon=self.login)
                imgs.append(src)

        except Exception as e:
            print(
                'Изображения не найдены или не могут быть получены:',
                type(e).__name__,
                e)

        self.driver.switch_to.default_content()
        self.logger.debug(
            text=f'(get_illustrations) Switched to default content...',
            login=self.login)

        return imgs

    def click_illustration_by_link(self, link):

        self.driver.get(link)
        link = self.get_illustration_server_name(link)
        self.driver.get(self.working_link)
        time.sleep(5)

        try:
            link = str(link)

            self.click_illustration()
            time.sleep(5)
            iframe = self.driver.find_element(
                By.CLASS_NAME, "publishedfile_modal_iframe")
            self.driver.switch_to.frame(iframe)
            images = WebDriverWait(
                self.driver,
                10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     ".publishedfile_popup_items .publishedfile_popup_screenshot img")))
            err_lib = 0
            for image in images:

                src = str(image.get_attribute("src"))
                aaa = src
                qa = link

                q = aaa.split('/')
                asd = qa.split('/')
                q = asd[0] + '//' + asd[2] + '/' + asd[3] + \
                    '/' + q[4] + '/' + q[5] + '/' + asd[-1]
                if q == link:

                    self.logger.debug(
                        text=f'(get_illustrations) Successfully clicked frame image... {"/".join(src.split("/")[-3:])}',
                        login=self.login)
                    image.click()
                    time.sleep(3)
                    return
                else:
                    err_lib += 1


            if err_lib == len(images):
                return 'NotFoundError'

        except Exception as err:

            self.logger.error(
                "The image in the database was not found in the list of available images, most likely you are using an image from someone else's profile. (DEV)")
            return 'NotFoundError'


        self.driver.switch_to.default_content()

    def close_frame(self):
        self.logger.debug(
            text=f'(close_frame) Closing frame...',
            login=self.login)
        self.driver.find_element(By.CLASS_NAME, "newmodal_close").click()

    def click_illustration(self):
        try:
            self.logger.debug(
                text=f'(click_illustration) Clicking illustration...',
                login=self.login)
            self.driver.find_element(
                By.CSS_SELECTOR,
                '.screenshot_showcase_screenshot').click()
            return
        except selenium.common.exceptions.ElementNotInteractableException:
            return 'NotFoundIllustration'
        except selenium.common.exceptions.NoSuchElementException:
            return 'NotFoundIllustration'


    def get_lens_bard(self):
        self.driver.save_screenshot("screenshot.png")
        try:
            select_elements = self.driver.find_elements(By.TAG_NAME, "select")
            lens = 0
            for select in select_elements:
                if select.get_attribute("id") != 'replay_select_form':
                    lens += 1
            return lens
        except selenium.common.exceptions.NoSuchElementException:
            return 0

    def get_link_illustration(self):
        element = self.driver.find_element(
            By.CSS_SELECTOR,
            '.profile_customization.myart .screenshot_showcase_screenshot')
        href_value = element.get_attribute("href")
        return href_value

    def is_warning_get_illustration_server_name(self):
        try:

            elements = self.driver.find_elements(
                By.CLASS_NAME, "contentcheck_desc_ctn")

            if elements == []:
                return False

            for element in elements:
                header = element.find_element(
                    By.CLASS_NAME, "contentcheck_header").text
                self.logger.debug(text="", login=self.login)
                self.logger.debug(text="", login=self.login)
                self.logger.info(
                    text=f"                    {self.driver.current_url}",
                    login=self.login)
                if header == 'ЭТОТ ОБЪЕКТ СОДЕРЖИТ КОНТЕНТ, КОТОРЫЙ ВЫ ПРЕДПОЧЛИ СКРЫТЬ:':
                    self.logger.info(
                        text=f'                         {header}',
                        login=self.login)
                    descriptors = element.find_elements(
                        By.CLASS_NAME, "contentcheck_descriptor")
                    for descriptor in descriptors:
                        self.logger.info(
                            text=f'                    {descriptor.text}',
                            login=self.login)
                else:
                    print(f'HEADER ERROR -> {header}')
                    return False
                self.driver.save_screenshot('test.png')

            return True
        except selenium.common.exceptions.NoSuchElementException as err:
            return False

    def get_illustration_server_name(self, link):

        self.driver.get(link)
        self.driver.implicitly_wait(50)
        self.driver.implicitly_wait(10)
        time.sleep(2)
        is_warning = self.is_warning_get_illustration_server_name()
        if is_warning:
            if self.warnings_ignore:

                show_button = WebDriverWait(
                    self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//button/span[contains(text(), 'Показать объект')]/..")))


                show_button.click()
                self.logger.debug(text="", login=self.login)
                self.logger.debug(
                    text="                                     Action: Show",
                    login=self.login)
                self.logger.debug(text="", login=self.login)
                self.logger.debug(text="", login=self.login)
                time.sleep(2)
                img_element = self.driver.find_element(
                    By.CSS_SELECTOR, ".actualmediactn a img")
            else:

                cancel_button = WebDriverWait(
                    self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//button/span[contains(text(), 'Отмена')]/..")))
                cancel_button.click()
                self.logger.debug(text="", login=self.login)
                self.logger.debug(
                    text="                                     Action: Cansel",
                    login=self.login)
                self.logger.debug(text="", login=self.login)
                self.logger.debug(text="", login=self.login)
                return
        else:
            img_element = self.driver.find_element(
                By.CSS_SELECTOR, ".actualmediactn a img")
        src_value = img_element.get_attribute("src")
        self.logger.debug(
            text=f'Successfully got illustration from {src_value.split("/")[-1]} from {link.split("/")[-1]}',
            login=self.login)

        return src_value

    def is_many_requests(self):
        try:
            error_message_element = self.driver.find_element(
                By.CSS_SELECTOR, "div._3gFescNPzR2aYp1VjmG3wz")

            error_message = error_message_element.text
            print(error_message)
            return True
        except selenium.common.exceptions.NoSuchElementException:
            return False

    def is_login_error_exists(self):
        """
        Check if there's a login error on the page.

        Args:
            driver: The Selenium WebDriver instance.

        Returns:
            bool: True if a login error exists, False otherwise.
        """
        if self.time_is_up():
            self.logger.error(text=f'Time is up', login=self.login)
            raise SteamLoginError('Time is up')

        try:
            self.driver.find_elements(
                By.CLASS_NAME, "customization_edit_area ui-sortable")
            return False
        except selenium.common.exceptions.NoSuchElementException:
            return True

    def time_is_up(self):
        """
        Check if two-factor authentication is enabled.

        Args:
            driver: The Selenium WebDriver instance.

        Returns:
            bool: True if 2FA is enabled, False otherwise.
        """
        time_is_up = False
        try:
            if self.driver.find_elements(By.CLASS_NAME, '_3gFescNPzR2aYp1VjmG3wz')[
                    0].text == 'Истёк срок действия запроса на вход в аккаунт':
                time_is_up = True
            else:
                time_is_up = False
        except BaseException:
            time_is_up = False
        return time_is_up

    def is_2Fauth(self):
        """
        Check if two-factor authentication is enabled.

        Args:
            driver: The Selenium WebDriver instance.

        Returns:
            bool: True if 2FA is enabled, False otherwise.
        """
        two_factor_auth = False
        try:
            if self.driver.find_elements(By.CLASS_NAME, 'QApnTTqEcicVcDQujTXyf')[
                    0].text == 'У вас настроен мобильный аутентификатор для защиты аккаунта.':
                two_factor_auth = True
            else:
                two_factor_auth = False
        except BaseException:
            two_factor_auth = False
        return two_factor_auth

    def is_auth(self):
        """
        Check if two-factor authentication is enabled.

        Args:
            driver: The Selenium WebDriver instance.

        Returns:
            bool: True if 2FA is enabled, False otherwise.
        """
        i = False
        try:
            if self.driver.find_elements(
                    By.CLASS_NAME, '_3gFescNPzR2aYp1VjmG3wz'):
                i = False
            else:
                i = True
        except BaseException:
            i = True
        return i


class GetTokenMech():
    def __init__(self, logger_, new_data_=False, data_=None):
        self.logger = logger_
        self.tokens = {}
        self.data = data_
        self.logger.debug(
            text=f'Initial GetTokenMech called with new_data: {new_data_}',
            login='None')
        self.get_tokens()

    def get_tokens(self):
        threads = []
        for user in self.data:
            login = user['login']
            password = user['password']
            offline = user['offline']
            reconnect = user['reconnect']
            ignore_all_warnings_pictures = user['ignore_all_warnings_pictures']

            if not offline:
                thread = threading.Thread(
                    target=self.auth,
                    args=(
                        login,
                        password,
                        ignore_all_warnings_pictures,
                        reconnect))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    def auth(self, login, password, ignore_all_warnings_pictures, reconnect):
        InitLogin(
            self.logger,
            login,
            password,
            ignore_all_warnings_pictures,
            reconnect)



class MainInitLoginPasswordHandler():
    def __init__(self, logger=None, new_data=False, data=None):
        L = InCodeLogger(logger)
        GetTokenMech(logger_=L, new_data_=new_data, data_=data)


class MainClass():
    def __init__(self):
        import json
        with open('config.json', 'r') as json_file:
            self.data = json.load(json_file)['data']

    def run(self):
        MainInitLoginPasswordHandler(new_data=True, data=self.data)


if __name__ == '__main__':
    MainClass().run()
