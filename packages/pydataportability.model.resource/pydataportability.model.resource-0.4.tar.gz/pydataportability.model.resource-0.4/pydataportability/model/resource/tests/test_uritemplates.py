from pydataportability.model.resource.models import URITemplate

def test_uritemplates_basic():
    tmpl = URITemplate('http://foo/bar/?q={%id}')
    assert tmpl(id='mrtopf') == 'http://foo/bar/?q=mrtopf'
    
def test_uritemplates_missing_param():
    tmpl = URITemplate('http://foo/bar/?q={%id}&foo={%bar}')
    assert tmpl(id='mrtopf') == 'http://foo/bar/?q=mrtopf&foo={%bar}'
    
    
    