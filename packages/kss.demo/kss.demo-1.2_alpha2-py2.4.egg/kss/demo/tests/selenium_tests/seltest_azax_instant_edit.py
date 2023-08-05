from seleniumtestcase import SeleniumTestCase
import unittest, time

def getTestClass():
   return seltest_azax_instant_edit

class seltest_azax_instant_edit(SeleniumTestCase):

    def test_seltest_azax_instant_edit(self):
        sel = self.selenium
        sel.open("/demo/azax_instant_edit.html")
        self.failUnless(sel.is_text_present("click me!"))
        self.assertEqual("click me!", sel.get_text("text"))
        sel.click("text")
        for i in range(60):
            try:
                if "click me!" == sel.get_value("value"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.assertEqual("click me!", sel.get_value("value"))
        sel.type("value", "change")
        sel.click("save")
        for i in range(60):
            try:
                if sel.is_text_present("change"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.failUnless(sel.is_text_present("change"))
        self.failIf(sel.is_text_present("click me!"))

def test_suite():
    return unittest.makeSuite(getTestClass())

if __name__ == "__main__":
    unittest.main()
