

def test_link_amount_for_describedby(rsf1):
    """rsf1 is the ResourceSetFixture, rs1 a resource set"""
    rs = rsf1.rs1
    assert len(rs.get_by_rel('describedBy'))==4
    

def test_link_amount_for_webfingerable(rsf1):
    """rsf1 is the ResourceSetFixture, rs1 a resource set"""
    rs = rsf1.rs1
    assert len(rs.get_by_rel('webfingerable'))==3
    
def test_link_priority_sorting(rsf1):
    """test if the priority sort order is correct"""
    rs = rsf1.rs1
    uris = [l.uris[0] for l in rs.get_by_rel('webfingerable')]
    assert uris == ['http://resource3', 'http://resource2', 'http://resource4']
    
def test_link_priority_with_minprio(rsf1):
    rs = rsf1.rs1
    uris = [l.uris[0] for l in rs.get_by_rel('webfingerable', min_priority=2)]
    assert uris == ['http://resource3']
    


    
    