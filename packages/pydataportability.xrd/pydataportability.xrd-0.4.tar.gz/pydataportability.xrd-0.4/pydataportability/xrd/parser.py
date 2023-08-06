from datetime import datetime
from elementtree.ElementTree import parse

from pydataportability.model.resource.models import *

NS = "http://docs.oasis-open.org/ns/xri/xrd-1.0"

def findall(elem, name, ns="http://docs.oasis-open.org/ns/xri/xrd-1.0"):
    return elem.findall("{%s}%s" %(ns,name))

def find(elem, name, ns="http://docs.oasis-open.org/ns/xri/xrd-1.0"):
    return elem.find("{%s}%s" %(ns,name))
    

def parse_xrd(fp):
    """an extensible XRD parser. The basic functionality is to take a file pointer and 
    parse the XRD. You can extend this by defining new utilities for parsing additional namespaces."""

    tree = parse(fp)
    elem = tree.getroot()
    expires = find(elem, 'Expires')
    if expires is not None:
        expires = datetime.strptime(expires.text,"%Y-%m-%dT%H:%M:%SZ")
    type_ = find(elem, 'Type')
    if type_ is not None:
        type_ = type_.text
    subject = find(elem, 'Subject')
    if subject is not None:
        subject = subject.text
    aliases = findall(elem, 'Alias')
    aliases = [alias.text for alias in aliases]

    resource = Resource(subject = subject,
                        aliases = aliases,
                        expires = expires,
                        type_ = type_)
                        
    # now add links
    links = findall(elem, 'Link')
    resource_set = ResourceSet()

    for link in links:
        rels = [rel.text for rel in findall(link, 'Rel')]
        media_types = [mt.text for mt in findall(link, 'MediaType')]
        uris = [uri.text for uri in findall(link, 'URI')]
        templates = [tmpl.text for tmpl in findall(link,"URITemplate")]
        priority = int(link.attrib.get("priority","0"))
        resource_link = ResourceLink(rels = rels,
                          media_types = media_types,
                          uris = uris,
                          templates = templates,
                          priority = priority)
        resource_set.append(resource_link)
    resource_set.commit()
    resource.links = resource_set
    return resource
