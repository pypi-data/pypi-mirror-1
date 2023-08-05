from seleniumtestcase import SeleniumTestCase
import unittest, time

def getTestClass():
   return seltest_three_autopupdate

class seltest_three_autopupdate(SeleniumTestCase):

    def test_seltest_three_autopupdate(self):
        sel = self.selenium
        sel.open("/demo/three_autoupdate.html")
        self.assertEqual("", sel.get_text("update-wrapper"))
        sel.click("start-update")
        for i in range(60):
            try:
                if sel.is_element_present("update-area"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        self.failUnless(sel.is_element_present("update-area"))
        self.assertEqual("", sel.get_text("update-area"))
        updateText = sel.get_text("update-area")
        self.assertEqual(updateText, sel.get_text("update-area"))
        time.sleep(3)
        self.assertNotEqual(updateText, sel.get_text("update-area"))
        # sel.()

def test_suite():
    return unittest.makeSuite(getTestClass())

if __name__ == "__main__":
    unittest.main()
