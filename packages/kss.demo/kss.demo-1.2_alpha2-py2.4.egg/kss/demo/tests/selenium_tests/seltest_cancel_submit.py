from seleniumtestcase import SeleniumTestCase
import unittest, time

def getTestClass():
   return seltest_cancel_submit

class seltest_cancel_submit(SeleniumTestCase):

    def test_seltest_cancel_submit(self):
        sel = self.selenium
        sel.open("/demo/cancel_submit.html")
        self.assertEqual("", sel.get_value("text_save"))
        sel.type("text_save", "abc")
        sel.click("submit")
        for i in range(60):
            try:
                if "Async saved abc" == sel.get_text("async"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("Async saved abc", sel.get_text("async"))

def test_suite():
    return unittest.makeSuite(getTestClass())

if __name__ == "__main__":
    unittest.main()
