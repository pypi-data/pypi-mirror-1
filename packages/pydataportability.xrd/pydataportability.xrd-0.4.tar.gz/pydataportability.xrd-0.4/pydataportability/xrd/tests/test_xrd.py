from pydataportability.xrd.parser import parse_xrd
from datetime import datetime

def test_xrd_basic_info(xrd1fp):
    resource = parse_xrd(xrd1fp)
    assert resource.subject == 'http://subject/'
    assert resource.type_ == "I don't know what this means yet"
    assert resource.expires == datetime(2010, 1, 1, 23, 42, 42)
    assert len(resource.aliases) == 3
    
def test_xrd_aliases(xrd1fp):
    resource = parse_xrd(xrd1fp)
    aliases = resource.aliases
    assert aliases[0] == "http://alias1/"
    assert aliases[1] == "http://alias2/"
    assert aliases[2] == "http://alias3/"

def test_xrd_links(xrd1fp):
    resource = parse_xrd(xrd1fp)
    assert len(resource.links) == 3
    
def test_correct_amount_of_rels(xrd1fp):
    resource = parse_xrd(xrd1fp)
    assert len(resource.links.get_by_rel("http://rel1/"))==2
    assert len(resource.links.get_by_rel("http://rel2/"))==2
    assert len(resource.links.get_by_rel("http://rel3/"))==1
    
def test_link_basic_data(xrd1fp):
    resource = parse_xrd(xrd1fp)
    link = resource.links.get_by_rel("http://link2_rel/")[0]
    assert len(link.uris) == 2
    assert link.uris[0] == "http://uri1_for_link2/"
    assert link.uris[1] == "http://uri2_for_link2/"
    assert link.media_types == []
    assert link.subject is None
    assert link.priority == 2
    assert link.templates == []
    
def test_link_filter_with_rel(xrd1fp):
    """test filtering of link types"""
    resource = parse_xrd(xrd1fp)
    assert len(resource.links.filter(rels=["http://link2_rel/"]))==1
    
def test_link_filter_without_parameters(xrd1fp):
    resource = parse_xrd(xrd1fp)
    assert len(resource.links.filter())==3

def test_link_filter_with_media_type(xrd1fp):
    resource = parse_xrd(xrd1fp)
    assert len(resource.links.filter(media_types=['application/pdf']))==1
    
def test_link_filter_with_media_type_and_rel_no_result(xrd1fp):
    resource = parse_xrd(xrd1fp)
    assert len(resource.links.filter(rels=["http://link2_rel/"], media_types=['application/pdf']))==0

def test_link_filter_with_media_type_and_rel(xrd1fp):
    resource = parse_xrd(xrd1fp)
    assert len(resource.links.filter(rels=["http://rel3/"], media_types=['application/pdf']))==1
    
def test_link_filter_priorities(xrd1fp):
    resource = parse_xrd(xrd1fp)    
    links = resource.links.filter()
    prios = [link.priority for link in links]
    
    assert prios == [2,0,0]
    
    
    
    
    