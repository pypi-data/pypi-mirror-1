from seleniumtestcase import SeleniumTestCase
import unittest, time

def getTestClass():
   return seltest_basic_commands

class seltest_basic_commands(SeleniumTestCase):

    def test_seltest_basic_commands(self):
        sel = self.selenium
        sel.open("/demo/basic_commands.html")
        #test initial state
        self.assertEqual("KSS", sel.get_text("demo"))
        self.assertEqual("copy here", sel.get_text("copy"))
        sel.click("change")
        for i in range(60):
            try:
                if sel.is_element_present("workedagain"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.failUnless(sel.is_element_present("workedagain"))
        self.assertEqual("it worked again", sel.get_text("demo"))
        sel.click("clear")
        for i in range(60):
            try:
                if not sel.is_element_present("workedagain"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertNotEqual("it worked again", sel.get_text("demo"))
        sel.click("copyFrom")
        for i in range(60):
            try:
                if "copy here" != sel.get_text("copy"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertNotEqual("copy here", sel.get_text("copy"))
        self.failIf(sel.is_element_present("workedagain"))
        sel.click("change")
        for i in range(60):
            try:
                if sel.is_element_present("workedagain"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.failUnless(sel.is_element_present("workedagain"))
        self.assertNotEqual("it worked again", sel.get_text("copy"))
        sel.click("copyFrom")
        for i in range(60):
            try:
                if "it worked again" == sel.get_text("copy"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("it worked again", sel.get_text("copy"))
        sel.click("clear")
        for i in range(60):
            try:
                if "it worked again" != sel.get_text("demo"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertNotEqual("it worked again", sel.get_text("demo"))
        sel.click("copyTo")
        for i in range(60):
            try:
                if "it worked again" == sel.get_text("demo"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("it worked again", sel.get_text("demo"))
        sel.click("clear")
        for i in range(60):
            try:
                if "it worked again" != sel.get_text("demo"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertNotEqual("it worked again", sel.get_text("demo"))
        sel.click("moveTo")
        for i in range(60):
            try:
                if "it worked again" == sel.get_text("demo"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("it worked again", sel.get_text("demo"))
        self.assertNotEqual("it worked again", sel.get_text("copy"))

def test_suite():
    return unittest.makeSuite(getTestClass())

if __name__ == "__main__":
    unittest.main()
