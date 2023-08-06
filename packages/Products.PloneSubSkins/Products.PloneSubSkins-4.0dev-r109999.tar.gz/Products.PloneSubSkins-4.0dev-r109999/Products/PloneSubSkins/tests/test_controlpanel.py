import unittest
import StringIO
from base import Browser
from base import IntegrationTestCase

class ControlPanelAnonymousTest(IntegrationTestCase):
    def test_anonymous_cannot_change_styles(self):
        browser = Browser()
        controlpanel_url = self.portal.absolute_url() + '/portal_subskinstool/subskins_control_panel'
        browser.open(controlpanel_url)
        self.failIfEqual(browser.url,controlpanel_url)

class ControlPanelTest(IntegrationTestCase):
    def setUp(self):
        super(ControlPanelTest, self).setUp()
        self.browser = Browser()
        self.browser.handleErrors = False
        self.browser.addAuthorizationHeader()
        self.controlpanel_url = self.portal.absolute_url() + '/portal_subskinstool'
        self.browser.open(self.controlpanel_url)
        self.browser.handleErrors = False
    def test_tool_admin_can_view(self):
        self.failUnlessEqual(self.browser.url,self.controlpanel_url)
    def test_choice(self):
        top_choice = self.browser.getControl(name="top_choice")
        top_options = top_choice.options
        self.assertTrue('top_test.css' in top_options)
        top_choice.value = ['top_test.css']
        self.browser.getControl("Save").click()
        self.failUnless(self.is_css_enabled('top_test.css'))
    def test_colorscheme(self):
        self.browser.open(self.css_url + "/top_test.css")
        self.failUnless('testcolor2.jpg' in self.browser.contents)
    def test_colorscheme_choice(self):
        colorscheme_choice = self.browser.getControl(name="colorschemes_choice")
        colorscheme_choice_options = colorscheme_choice.options
        self.assertTrue('colors2_test' in colorscheme_choice_options)
        colorscheme_choice.value = ['colors2_test']
        self.browser.getControl("Save").click()
        self.browser.open(self.css_url + "/top_test.css")
        self.failUnless('secondfile.jpg' in self.browser.contents)
    def test_colorscheme_on_the_fly_change(self):
        self.browser.open(self.css_url + "/top_test.css?colorscheme=colors2_test")
        self.failUnless('secondfile.jpg' in self.browser.contents)
    def test_change_logo(self):
        myPhoto = StringIO.StringIO('my logo')
        file_control = self.browser.getControl(name='newlogo').mech_control
        file_control.add_file(myPhoto, filename='myPhoto.gif')
        self.browser.getControl('Update').click()
        custom = self.portal.portal_skins.custom
        self.failUnless('logo.jpg' in custom.objectIds())
        image_url = custom['logo.jpg'].absolute_url()
        self.browser.open(image_url)
        self.failUnlessEqual('my logo', self.browser.contents)

def test_suite():
    return unittest.TestSuite([
            unittest.makeSuite(ControlPanelTest),
            unittest.makeSuite(ControlPanelAnonymousTest),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

