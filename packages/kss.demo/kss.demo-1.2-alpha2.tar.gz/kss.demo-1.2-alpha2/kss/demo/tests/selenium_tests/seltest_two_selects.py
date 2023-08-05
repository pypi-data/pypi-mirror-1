from seleniumtestcase import SeleniumTestCase
import unittest, time

def getTestClass():
   return seltest_two_selects

class seltest_two_selects(SeleniumTestCase):

    def test_seltest_two_selects(self):
        sel = self.selenium
        sel.open("/demo/two_selects.html")
        self.assertEqual("animals machines", sel.get_text("first"))
        self.assertEqual("", sel.get_text("second"))
        sel.select("first", "label=animals")
        for i in range(60):
            try:
                if "dog cat cow" == sel.get_text("second"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("dog cat cow", sel.get_text("second"))
        sel.select("first", "label=machines")
        for i in range(60):
            try:
                if "computer car airplane" == sel.get_text("second"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("computer car airplane", sel.get_text("second"))

def test_suite():
    return unittest.makeSuite(getTestClass())

if __name__ == "__main__":
    unittest.main()
