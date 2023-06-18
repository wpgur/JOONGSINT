from flask import Blueprint, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time, re, os
from urllib.parse import urljoin
from datetime import datetime


domain_module = Blueprint("domain_module", __name__)

@domain_module.route("/domain_result", methods=["POST"])
def domain_result():

    class WebCrawler:
        def __init__(self, options=None):
            if options is None:
                options = Options()
                options.headless = True
            self.driver = webdriver.Chrome('chromedriver.exe', options=options)
            self.start_time = datetime.today().strftime("%Y%m%d%H%M%S")  
            self.folder_path = './capture_log'
            self.log_path = './crawling_log'
            self.all_url = []
            self.complete_url = []
            self.result = {}
            self.all_keyword = []
            self.all_email = []
            self.all_phone = []
            

        def login_instargram(self, target_url, login_name, login_pw):
            insta_url = 'https://www.instagram.com'
            self.driver.implicitly_wait(10)
            self.driver.get(insta_url)
            time.sleep(3)

            username_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='username']")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")

            username_input.send_keys(login_name)
            password_input.send_keys(login_pw)

            login_button = self.driver.find_element(By.XPATH , "//button[@type='submit']")
            login_button.click()

            print('인스타그램 로그인')
            time.sleep(3)
            self.driver.get(target_url)
            time.sleep(3)
            print('인스타그램 진입성공')

        def login_facebook(self, target_url, login_name, login_pw):
            fb_url = 'https://www.facebook.com'
            self.driver.implicitly_wait(10)
            self.driver.get(fb_url)
            time.sleep(3)

            username_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='email']")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='pass']")

            username_input.send_keys(login_name)
            password_input.send_keys(login_pw)

            login_button = self.driver.find_element(By.XPATH , "//button[@type='submit']")
            login_button.click()

            print('페이스북 로그인')
            time.sleep(3)
            self.driver.get(target_url)
            time.sleep(3)
            print('페이스북 진입성공')

        def HTML_SRC(self, url, url_search=0):
            try:
                self.driver.get(url)

                # 페이지 로딩이 완료될 때까지 대기
                while True:
                    page_state = self.driver.execute_script('return document.readyState;')
                    if page_state == 'complete':
                        break
                    time.sleep(1)

                # SPA 웹 페이지의 HTML 소스 코드 가져오기
                html = self.driver.execute_script('return document.getElementsByTagName("html")[0].innerHTML;')

                # BeautifulSoup을 이용하여 데이터 추출
                soup = BeautifulSoup(html, 'html.parser')

                if(url_search==1):
                    return soup

                keywords = re.findall(r"[가-힣]{2,10}", soup.text)
                for keyword in keywords:
                    if keyword not in self.all_keyword:
                        self.all_keyword.append(keyword)

                emails = re.findall(r'\b[\w.-]+?@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}\b', soup.text)
                for email in emails:
                    if email not in self.all_email:
                        self.all_email.append(email)

                phones = re.findall(r"\d{2,3}-\d{3,4}-\d{4}", soup.text)
                for phone in phones:
                    if phone not in self.all_phone:
                        self.all_phone.append(phone)

                invalid_chars = r'[\\/:\*\?"<>\|]+'
                # 파일 이름으로 사용할 수 없는 문자들을 '_'로 치환
                filename = re.sub(invalid_chars, '_', url) + '.png'
                self.driver.set_window_size(1920, 1080)
                # 페이지 로딩이 완료될 때까지 대기
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
                self.driver.save_screenshot(f'{self.folder_path}/{filename}')
            except:
                pass


        def url_append(self, url, depth=1):
            try:
                if (depth < 1) : return
                depth -= 1
                self.complete_url.append(url)
                
                soup = self.HTML_SRC(url, 1)
                print('a')

                for link in soup.find_all("a"):

                    url_add = urljoin(url, link.get("href"))
                    
                    if url_add not in self.all_url:
                        self.all_url.append(url_add)
                
                for url_one in (set(self.all_url) - set(self.complete_url)):
                    self.url_append(url_one, depth)
                
            except:
                return


        def run(self, root_url):
            
            self.url_append(root_url, 2)
            
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)

            for url in self.all_url:
                print("[*] Target URL:" ,url, '###')
                self.HTML_SRC(url)

            self.result['keyword'] = self.all_keyword
            self.result['email'] = self.all_email
            self.result['phone'] = self.all_phone

            for key in self.result:
                fp = open(f'{self.log_path}/{self.start_time}_{key}.txt','w', encoding='utf-8')
                fp.write(str(self.result[key]))
                fp.close()

            return self.result



    # url = 'http://joongsint.64bit.kr'
    url = 'http://'+ request.cookies.get('Domain')+'/'
    print(url)

    crawling = WebCrawler()
    result = crawling.run(url)

    # ins_id = request.cookies.get("insta_id")
    # ins_pw = request.cookies.get("insta_pw")
    # fb_id = request.cookies.get("face_id")
    # fb_pw = request.cookies.get("face_pw")
    # crawling.login_instargram(url, ins_id, ins_pw)
    # crawling.login_facebook(url, fb_id, fb_pw)
        
    return render_template("domain_result.html", result=result)