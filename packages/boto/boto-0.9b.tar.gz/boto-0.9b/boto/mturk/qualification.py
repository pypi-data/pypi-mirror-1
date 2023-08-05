# Copyright (c) 2006,2007 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

class Qualification:

    def __init__(self, id=None, subject_id=None, grant_time=None,
                 integer_value=None, locale_value=None, status=None):
        self.id = id
        self.subject_id = subject_id
        self.grant_time = grant_time
        self.integer_value = integer_value
        self.locale_value = locale_value
        self.status = status

    def __repr__(self):
        return 'Qualification: %s' % self.id

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'QualificationTypeId':
            self.id = value
        elif name == 'SubjectId':
            self.subject_id = value
        elif name == 'GrantTime':
            self.grant_time = value
        elif name == 'IntegerValue':
            self.integer_value = int(value)
        elif name == 'Country':
            # Since the Locale data structure currently consists of
            # only the Country element, I'm just handling that here
            # rather than creating a separate Locale object
            self.locale_value = value
        elif name == 'Status':
            self.status = value
        else:
            setattr(self, name, value)

            
