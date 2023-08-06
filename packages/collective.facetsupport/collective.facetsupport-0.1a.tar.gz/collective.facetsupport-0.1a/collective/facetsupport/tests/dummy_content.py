from Products.CMFPlone.utils import _createObjectByType


TEST_CONTENT = [
    {'id':'doc1',
     'type':'Document',
     'Subject':['Apple','Banana','Orange','Lemon'],
    },
    {'id':'doc2',
     'type':'Document',
     'Subject':['Apple','Banana','Orange'],
    },
    {'id':'doc3',
     'type':'Document',
     'Subject':['Apple','Banana','Lemon'],
    },
    {'id':'doc4',
     'type':'Document',
     'Subject':['Apple','Banana','Lemon'],
    },
    {'id':'doc5',
     'type':'Document',
     'Subject':['Apple'],
    },
    {'id':'news1',
     'type':'News Item',
     'Subject':['Apple','Banana','Lemon'],
    },
    {'id':'news2',
     'type':'News Item',
     'Subject':['Apple','Banana','Orange','Lemon'],
    },
    {'id':'news3',
     'type':'News Item',
     'Subject':['Apple','Lemon'],
    },
    {'id':'news4',
     'type':'News Item',
     'Subject':['Apple','Banana','Orange','Lemon'],
    },
    {'id':'news5',
     'type':'News Item',
     'Subject':['Apple'],
    },
]


def construct_dummy_content(portal):
    #Create a container to keep it away from portal root
    _createObjectByType(type_name='Folder',
                        id='dummy_container',
                        container=portal)
    container = portal.dummy_container

    for item in TEST_CONTENT:
        _createObjectByType(type_name=item['type'],
                            id=item['id'],
                            container=container,
                            title=item['id'])
        obj = container.get(item['id'])
        obj.setSubject(item['Subject'])
        obj.reindexObject()

    _createObjectByType(type_name='Topic',
                        container=portal,
                        id='collection')

    collection = portal.collection
    type_crit = collection.addCriterion('Type','ATPortalTypeCriterion')
    type_crit.setValue(['News Item','Page'])
    sort_crit = collection.addCriterion('created','ATSortCriterion')
    collection.setSortCriterion('created', True)