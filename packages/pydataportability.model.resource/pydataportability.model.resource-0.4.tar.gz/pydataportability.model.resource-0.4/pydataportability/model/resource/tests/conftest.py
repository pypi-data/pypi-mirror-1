from pydataportability.model.resource.models import *

class ResourceSetFixture:
    """a fixture for testing resource sets which are a group of resources"""
    
    def __init__(self):
        """instantiate some resource links and build resource sets from them"""
        
        # resource with rel `describedBy` and prio 1
        self.rl1 = ResourceLink(
            rels=['describedBy'],
            uris=['http://resource1'],
            priority = 1)
        # resource with rel `describedBy` and `webfingerable` and prio 1
        self.rl2 = ResourceLink(
            rels=['describedBy','webfingerable'],
            uris=['http://resource2'],
            priority = 1)
        # resource with rel `describedBy` and `webfingerable` and prio 2
        self.rl3 = ResourceLink(
            rels=['describedBy','webfingerable'],
            uris=['http://resource3'],
            priority = 2)
        self.rl4 = ResourceLink(
            rels=['describedBy','webfingerable'],
            uris=['http://resource4'],
            priority = 0)

        self.rs1 = ResourceSet([self.rl1, self.rl2, self.rl3, self.rl4])


def pytest_funcarg__rsf1(request):
    return ResourceSetFixture()
    