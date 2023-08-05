# -*- coding: ISO-8859-15 -*-
# Copyright (c) 2005
# Authors:
#   Godefroid Chapelle <gotcha@bubblenet.be>
#   Tarek Ziad� <tz@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

from kss.core import AzaxBaseView, force_unicode, KssExplicitError, kssaction
import datetime

class AzaxView(AzaxBaseView):

    def clearDivContent(self):
        """ clear div content """
        self.getCommandSet('core').clearChildNodes('div#demo')
        return self.render()

    def copyFromDivContent(self):
        """ copy div content """
        self.getCommandSet('core').copyChildNodesFrom('div#copy', 'demo')
        return self.render()

    def copyToDivContent(self):
        """ copy div content """
        self.getCommandSet('core').copyChildNodesTo('div#copy', 'demo')
        return self.render()

    def moveToDivContent(self):
        """ copy div content """
        self.getCommandSet('core').copyChildNodesTo('div#copy', 'demo')
        self.getCommandSet('core').clearChildNodes('div#copy')
        return self.render()

    def getDivContent(self):
        """ returns div content """
        self.getCommandSet('core').replaceInnerHTML('div#demo', '<h1>it worked</h1>')
        self.getCommandSet('core').replaceInnerHTML('div#demo', '<h1 id="workedagain">it worked&nbsp;again</h1>')
        return self.render()

    def getCorrespondingSelect(self, value):
        """ returns select content """
        mapping = {}
        mapping['']=[]
        mapping['animals']=['dog', 'cat', 'cow']
        mapping['machines']=['computer', 'car', 'airplane']
        # XXX Note that originally we just used replaceInnerHTML to just put
        # the options inside the select, however this is principally broken 
        # on IE due to an IE bug. Microsoft has confirmed the bug but is not
        # giving information on whether it has or it will ever be fixed.
        # For further info, see http://support.microsoft.com/default.aspx?scid=kb;en-us;276228
        # The current solution, replace the outer node, works solidly.
        result = ['<select id="second">']
        result.extend(['<option>%s</option>' % item for item in mapping[value]])
        result.append('</select>')
        self.getCommandSet('core').replaceHTML('select#second', ' '.join(result))
        return self.render()

    def getAutoupdateMarkup(self):
        """ returns the current time """
        self.getCommandSet('core').replaceInnerHTML('div#update-wrapper', '<div id="update-area"></div>')
        return self.render()

    def getCurrentTime(self):
        """ returns the current time """
        self.getCommandSet('core').replaceInnerHTML('div#update-area', "<p>%s</p>" % str(datetime.datetime.now()))
        return self.render()
        
    def getInputField(self, value):
        'Inserts the value as entered into an input field'
        # We need to make unicode. But on Z2 we receive utf-8, on Z3 unicode
        value = force_unicode(value, 'utf')
        self.getCommandSet('core').replaceInnerHTML('div#text', 
                            '<div><input type="text" name="value" value="'+value+'" /></div>' \
                            '<input type="button" value="save" id="save" />'
                           )
        return self.render()
        
    def saveText(self, value):
        'Inserts the value to display it on the page'
        # We need to make unicode. But on Z2 we receive utf-8, on Z3 unicode
        value = force_unicode(value, 'utf')
        self.getCommandSet('core').replaceInnerHTML('div#text', value+'<input type="hidden" name="value" value="'+value+'" />')
        return self.render()
    
    def expandSubTree(self, value, xvalue):
        'Expands given subtree'
        self.getCommandSet('core').replaceInnerHTML('#text', 'works, expand %s (xhtml attr: %s)' % (value, xvalue))
        return self.render()
        
    def collapseSubTree(self, value, xvalue):
        'Collapses given subtree'
        self.getCommandSet('core').replaceInnerHTML('#text', 'works, collapse %s (xhtml attr: %s)' % (value, xvalue))
        return self.render()

    def cancelSubmitSave(self, text_save):
        # We need to make unicode. But on Z2 we receive utf-8, on Z3 unicode
        text_save = force_unicode(text_save, 'utf')
        self.getCommandSet('core').replaceInnerHTML('div#async', 'Async saved %s' % text_save)
        return self.render()

    def removeNodeXpath(self):
        # XXX the xpath selector is now moved out of the core, see suppl, product "azaxslt"
        sel = self.getSelector('xpath', "//P[@id='xpath']/following-sibling::*[position()=1]")
        self.getCommandSet('core').deleteNode(sel)
        return self.render()
       
    def clickedButton(self, id):
        'Show status of the button clicked'
        self.getCommandSet('core').replaceInnerHTML('#update-status', "<p>Button <b>%s</b> clicked. <i>%s</i></p>" % (id, datetime.datetime.now()))
        return self.render()

    def updateSlaveSelector(self, masterid, value):
        """ returns select content """
        mapping = {}
        mapping['']=[]
        mapping['animals']=['dog', 'cat', 'cow']
        mapping['machines']=['computer', 'car', 'airplane']
        # calculate the slave id
        master, _dummy = masterid.split('-')
        slaveid = '%s-slave' % master
        # make the payload
        result = ['<select id="%s">' % slaveid]
        result.extend(['<option>%s</option>' % item for item in mapping[value]])
        result.append('</select>')
        # XXX See above remark why we need to replace the outer select.
        self.getCommandSet('core').replaceHTML('select#%s' % slaveid, ' '.join(result))
        return self.render()

    def formSubmitSave(self, data):
        result = ['<p>Async saved:</p><table><th>Name:</th><th>Value:</th>']
        for key, value in data.items():
            result.append('<tr><td>%s</td><td>%s</td></tr>' % (key, value))
        result.append('</table>')
        # We need to make unicode. But on Z2 we receive utf-8, on Z3 unicode
        retval = force_unicode(''.join(result), 'utf')
        self.getCommandSet('core').replaceInnerHTML('div#async', retval)
        return self.render()

    def reset(self):
        self.getCommandSet('effects').effect('.effects', 'appear')
        return self.render()

    @kssaction
    def errTest(self, id, act):
        if act == 'error':
            raise Exception, 'We have an error here.'
        elif act == 'explicit':
            raise KssExplicitError, 'Explicit error raised.'
        elif act == 'empty':
            # Just do nothing, we want to return a response with no commands.
            # This is valid behaviour, should raise no error, however 
            # gives a warning in the kukit log.
            pass
        ## XXX This is commented out by default, but you can try this on your own
        ## server, together with the timeout buttons in the page template timeout buttons in the page template.
        ## 
        #elif act == 'timeout':
        #    # Wait longer then timeout, this is currently 4 s
        #    time.sleep(6.0);
        #    # the next reply will never arrive.
        #    self.replaceInnerHTML('#update-status', u'Timeout response, button %s clicked. %s' % (id, datetime.datetime.now()))
        else:
            # act = noerror: standard response.
            self.getCommandSet('core').replaceInnerHTML('#update-status', u'Normal response, button %s clicked. %s' % (id, datetime.datetime.now()))
        return self.render()

    def htmlReplace(self):
        """html replace"""
        self.getCommandSet('core').replaceHTML('div#frame', '<div id="frame"><h1 id="core">KSS for a life.</h1></div>')
        return self.render()

    def htmlInsertBefore(self):
        """html insert"""
        self.getCommandSet('core').insertHTMLBefore('#core', '<div class="type1">KSS for a life. %s</div>' % (str(datetime.datetime.now()), ))
        return self.render()

    def htmlInsertAfter(self):
        """html insert"""
        self.getCommandSet('core').insertHTMLAfter('#core', '<div class="type1">KSS for a life. %s</div>' % (str(datetime.datetime.now()), ))
        return self.render()

    def htmlInsertAsFirstChild(self):
        """html insert"""
        self.getCommandSet('core').insertHTMLAsFirstChild('div#frame', '<div class="type2">KSS for a life. %s</div>' % (str(datetime.datetime.now()), ))
        return self.render()

    def htmlInsertAsLastChild(self):
        """html insert"""
        self.getCommandSet('core').insertHTMLAsLastChild('div#frame', '<div class="type2">KSS for a life. %s</div>' % (str(datetime.datetime.now()), ))
        return self.render()
