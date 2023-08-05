"""
Demonstrate sibling grouping, a common PITA problem.
Specifically inspired by:
http://mail.python.org/pipermail/xml-sig/2005-March/011028.html
"""
import amara
from amara import bindery

XML="""\
<questions>
  <question>
    <content>Why?</content>
    <answer id="1"/>
  </question>
  <question>
    <content>Why?</content>
    <answer id="2"/>
  </question>
</questions>
"""

ANSWER1 = """\
<content>just because</content>
"""

#Subclass from the default binding class
#We're adding a specialized method for accessing content
class answer_proxy(bindery.element_base):
    def __init__(self):
        #Flag to avoid problematic recursion
        #Use leading "xml" convention to avoid any clashes with XML constructs
        self.xml_mutex = False 
        bindery.element_base.__init__(self)
    
    def __getattr__(self, name):
        #Warning: __getattr__ is one of the trickest aspects of Python to
        #get right, and to debug.
        #BTW, you rarely want to use __getattribute__ in this case
        #Overall, always good to be familiar with
        #http://www.python.org/download/releases/2.2.3/descrintro/
        if name == 'content' and not self.xml_mutex:
            #Use Amara API as you wish, in this case grabbing the id attribute
            answer_ob_name = 'ANSWER' + self.id
            try:
                self.xml_mutex = True #Set flag to avoid unwanted recursion
                self.xml_append_fragment(globals()[answer_ob_name])
                self.xml_mutex = False
            except KeyError:
                msg = u'Answer document fragment string %s not found'%answer_ob_name
                elem = self.xml_create_element(u'content', content=msg)
                self.xml_append(elem)
            return self.__dict__[name]
        raise AttributeError('%r has no attribute "%s"'%(self, name))


doc = amara.parse(XML, binding_classes={(None, 'answer'): answer_proxy})

print doc.xml()
print "Accessing answer 1: ", doc.questions.question.answer.content
print "Accessing answer 2: ", doc.questions.question[1].answer.content
print doc.xml()

