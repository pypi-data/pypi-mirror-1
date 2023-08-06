import unittest

class ShouldFilterTests(unittest.TestCase):
    def makeCall(self, qs=None, status="200 Ok", ct="text/html"):
        from repoze.slicer import SlicerApp
        slicer=SlicerApp(None)
        environ={}
        if qs is not None:
            environ["QUERY_STRING"]=qs
        # Use a trampoline to deal with the usage of sys._getframe()
        def trampoline():
            return slicer.should_filter(status, [("content-type", ct)], None)
        return trampoline()

    def testProperRequest(self):
        self.assertEqual(self.makeCall(qs="_filter=id"), True)

    def testNoTrigger(self):
        self.assertEqual(self.makeCall(), False)

    def testInvalidStatusCode(self):
        self.assertEqual(self.makeCall(qs="_filter=id", status="404"), False)

    def testNonHtmlResponse(self):
        self.assertEqual(self.makeCall(qs="_filter=id", ct="text/plain"), False)


class FilterTests(unittest.TestCase):
    def makeCall(self, data, headers=None):
        from repoze.slicer import SlicerApp
        slicer=SlicerApp(None)
        environ={"slicer.target": "id"}
        if headers is None:
            headers=[("content-length"), str(len(data))]
        return slicer.filter(environ, headers, data)

    def testIdPresent(self):
        self.assertEqual(self.makeCall("<html><p id='id'>test</p></html>"),
                        '<p id="id">test</p>')

    def testIdNotPresent(self):
        self.assertEqual(self.makeCall("<html></html>"), "<div/>")

    def testContentLengthUpdated(self):
        input="<html><p id='id'>test</p></html>"
        headers=[("Content-Length", str(len(input)))]
        self.makeCall(input, headers)
        self.assertEqual(headers, [("Content-Length", "19")])

    def testContentLengthUpdateNotCaseSensitive(self):
        input="<html><p id='id'>test</p></html>"
        headers=[("coNtEnt-LeNGtH", str(len(input)))]
        self.makeCall(input, headers)
        self.assertEqual(headers, [("Content-Length", "19")])

    def testInvalidHtmlReturnedUntouched(self):
        input="<html><p id='id'>test</html>"
        self.failUnless(self.makeCall(input) is input)

    def testPreserveCDATA(self):
        self.assertEqual(self.makeCall("<html><p id='id'><![CDATA[test]]></p></html>"),
                        '<p id="id"><![CDATA[test]]></p>')

    def XtestHtmlEntity(self):
        # Disabled for now - lxml refuses to ignore HTML entities, and there
        # is no API to tell it about valid entities.
        self.assertEqual(self.makeCall("<html><p id='id'>&copy;</p></html>"),
                        '<p id="id">&copy;</p>')



def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")

