from seleniumtestcase import SeleniumTestCase
import unittest, time

def getTestClass():
   return seltest_two_select_revisited

class seltest_two_select_revisited(SeleniumTestCase):

    def test_seltest_two_select_revisited(self):
        sel = self.selenium
        sel.open("/demo/two_select_revisited.html")
        self.assertEqual("animals machines", sel.get_text("first-master"))
        self.assertEqual("", sel.get_text("first-slave"))
        sel.select("first-master", "label=animals")
        for i in range(60):
            try:
                if "dog cat cow" == sel.get_text("first-slave"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("dog cat cow", sel.get_text("first-slave"))
        sel.select("first-master", "label=machines")
        for i in range(60):
            try:
                if "computer car airplane" == sel.get_text("first-slave"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("computer car airplane", sel.get_text("first-slave"))
        self.assertEqual("animals machines", sel.get_text("second-master"))
        self.assertEqual("", sel.get_text("second-slave"))
        sel.select("second-master", "label=animals")
        for i in range(60):
            try:
                if "dog cat cow" == sel.get_text("second-slave"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("dog cat cow", sel.get_text("second-slave"))
        sel.select("second-master", "label=machines")
        for i in range(60):
            try:
                if "computer car airplane" == sel.get_text("second-slave"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("computer car airplane", sel.get_text("second-slave"))
        self.assertEqual("animals machines", sel.get_text("third-master"))
        self.assertEqual("", sel.get_text("third-slave"))
        sel.select("third-master", "label=animals")
        for i in range(60):
            try:
                if "dog cat cow" == sel.get_text("third-slave"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("dog cat cow", sel.get_text("third-slave"))
        sel.select("third-master", "label=machines")
        for i in range(60):
            try:
                if "computer car airplane" == sel.get_text("third-slave"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("computer car airplane", sel.get_text("third-slave"))

def test_suite():
    return unittest.makeSuite(getTestClass())

if __name__ == "__main__":
    unittest.main()
