
from unittest import TestCase, TestSuite, makeSuite

from oofill.parser import OOFill

def getAbsPathOfTestFile(name):
    from os.path import dirname, join
    return join(dirname(__file__), name)

class OOFillTests(TestCase):
    """
    Test suite for udp.
    """
    def test_OOFill_identity(self):
        class Test1View:
            pass
        a = file(getAbsPathOfTestFile("test1.odt"))
        ofilinst = OOFill(a)
        b = ofilinst.render(Test1View())
 
    def test_OOFill_insertblock(self):
        class Test1View:
            def titreOrdreDuJour(self):
                import time
                text='<text:p  text:outline-level="2" text:style-name="P2">'
                text+="Séance du %s" % time.ctime()
                text+='</text:p>'
                return text.decode('utf-8')
        a = file(getAbsPathOfTestFile("test1.odt"))
        ofilinst = OOFill(a)
        #b = file(getAbsPathOfTestFile("test1_out.odt"), 'w')
        #b = file("tests/test1_out.odt", 'w')
        #for block in ofilinst.render(Test1View(),
        #                             getAbsPathOfTestFile("test1_out.odt")):
        #    
        #    b.write(block)
        ofilinst.render(Test1View(), getAbsPathOfTestFile("test1_out.odt"))

    def test_OOFill_replaceblock(self):
        class Test2View:
            def replaceTitreOrdreDuJour(self):
                import time
                text='<text:p  text:outline-level="2" text:style-name="P2">'
                text+="Séance du %s" % time.ctime()
                text+='</text:p>'
                return text.decode('utf-8')
        a = file(getAbsPathOfTestFile("test2.odt"))
        ofilinst = OOFill(a)
        #b = file(getAbsPathOfTestFile("test1_out.odt"), 'w')
        #b = file("tests/test1_out.odt", 'w')
        #for block in ofilinst.render(Test1View(),
        #                             getAbsPathOfTestFile("test1_out.odt")):
        #    
        #    b.write(block)
        ofilinst.render(Test2View(), getAbsPathOfTestFile("test2_out.odt"))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(OOFillTests))
    return suite

if __name__ == '__main__':
    framework()
