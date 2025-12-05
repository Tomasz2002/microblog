import unittest
import threading
import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from app.models import User
from config import TestingConfig

class SeleniumCase(unittest.TestCase):
    client = None
    
    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') 
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        cls.driver.implicitly_wait(10)
        cls.app = create_app(TestingConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()
        threading.Thread(target=cls.app.run, kwargs={'port': 5000, 'use_reloader': False}).start()
        time.sleep(2)
        cls.base_url = 'http://localhost:5000'

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.app_context.pop()

    def setUp(self):
        db.session.remove()
        db.drop_all()
        db.create_all()
        self.driver.delete_all_cookies()

    def get_unique_user_data(self):
        unique_id = uuid.uuid4().hex[:6]
        return {
            'username': f'user_{unique_id}',
            'email': f'user_{unique_id}@test.com',
            'password': 'pass123'
        }

    def test_full_user_flow(self):
        driver = self.driver
        user_data = self.get_unique_user_data()
        driver.get(f'{self.base_url}/auth/register')
        driver.find_element(By.NAME, "username").send_keys(user_data['username'])
        driver.find_element(By.NAME, "email").send_keys(user_data['email'])
        driver.find_element(By.NAME, "password").send_keys(user_data['password'])
        driver.find_element(By.NAME, "password2").send_keys(user_data['password'])
        driver.find_element(By.ID, "submit").click()
        self.assertIn("Sign In", driver.page_source)
        driver.find_element(By.NAME, "username").send_keys(user_data['username'])
        driver.find_element(By.NAME, "password").send_keys(user_data['password'])
        driver.find_element(By.ID, "submit").click()
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), f"Hi, {user_data['username']}!")
        )
        self.assertIn(f"Hi, {user_data['username']}!", driver.page_source)
        post_input = driver.find_element(By.NAME, "post")
        post_input.send_keys("Selenium post")
        driver.find_element(By.ID, "submit").click()
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Selenium post")
        )
        self.assertIn("Selenium post", driver.page_source)

    def test_edit_profile(self):
        driver = self.driver
        user_data = self.get_unique_user_data()
        u = User(username=user_data['username'], email=user_data['email'])
        u.set_password(user_data['password'])
        db.session.add(u)
        db.session.commit()
        driver.get(f'{self.base_url}/auth/login')
        driver.find_element(By.NAME, "username").send_keys(user_data['username'])
        driver.find_element(By.NAME, "password").send_keys(user_data['password'])
        driver.find_element(By.ID, "submit").click()
        WebDriverWait(driver, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), f"Hi, {user_data['username']}!")
        )
        driver.get(f'{self.base_url}/edit_profile')
        bio_field = driver.find_element(By.NAME, "about_me")
        bio_field.clear()
        bio_field.send_keys("Nowe bio")
        driver.find_element(By.ID, "submit").click()
        driver.get(f'{self.base_url}/user/{user_data["username"]}')
        self.assertIn("Nowe bio", driver.page_source)