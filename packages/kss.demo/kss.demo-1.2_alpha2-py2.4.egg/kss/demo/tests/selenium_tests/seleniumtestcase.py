import os
import unittest

from selenium import selenium
try:
    browser = os.environ["SELENIUMBROWSER"]
except:
    browser = "*firefox"
try:
    target = os.environ["SELENIUMTARGET"]
except:
    target = "http://localhost:8080"

class SeleniumTestCase(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, browser, target)
        self.selenium.start()

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

