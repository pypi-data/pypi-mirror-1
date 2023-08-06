import logging
import wsgifilter
from lxml import etree
from cgi import parse_qs
import sys

class SlicerApp(wsgifilter.Filter):
    trigger = "_filter"
    query = etree.XPath("//*[@id=$target]")

    def should_filter(self, status, headers, exc_info):
        if not wsgifilter.Filter.should_filter(self, status, headers, exc_info):
            return False
        environ=sys._getframe(2).f_locals["environ"]
        query=parse_qs(environ.get("QUERY_STRING", ""))
        environ["slicer.target"]=target=query.get(self.trigger, [None])[0]
        return bool(target)


    def filter(self, environ, headers, data):
        target=environ["slicer.target"]
        try:
            dom=etree.fromstring(data)
        except etree.XMLSyntaxError, e:
            return data

        nodes=self.query(dom, target=target)
        if nodes:
            tree=nodes[0]
        else:
            tree=etree.Element("div")

        doc=etree.tostring(tree)
        for i in range(len(headers)):
            if headers[i][0].lower()=="content-length":
                headers[i]=("Content-Length", str(len(doc)))
        return doc


