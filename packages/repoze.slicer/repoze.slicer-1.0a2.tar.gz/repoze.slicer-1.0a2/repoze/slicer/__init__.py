import logging
import wsgifilter
import lxml.html
from lxml import etree
from cgi import parse_qs
import sys

log = logging.getLogger("repoze.slicer")

class SlicerApp(wsgifilter.Filter):
    trigger = "_filter"
    query = etree.XPath("//*[@id=$target]")

    def should_filter(self, status, headers, exc_info):
        if not wsgifilter.Filter.should_filter(self, status, headers, exc_info):
            return False
        for frame in [3,2]:
            environ=sys._getframe(frame).f_locals.get("environ", None)
            if environ is not None:
                break
        else:
            log.critical("Unable to find the environ in the stack")
            return False
        query=parse_qs(environ.get("QUERY_STRING", ""))
        environ["slicer.target"]=target=query.get(self.trigger, [None])[0]
        return bool(target)


    def filter(self, environ, headers, data):
        target=environ["slicer.target"]
        try:
            parser = etree.XMLParser(remove_blank_text=True, strip_cdata=False, resolve_entities=False)
            dom=etree.fromstring(data, parser)
        except etree.XMLSyntaxError, e:
            log.info("Unable to parse response: %s", e)
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


