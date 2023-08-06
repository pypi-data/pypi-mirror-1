import math

from zope.interface import implements

from interfaces import IBatch


class Batch(object):
    implements(IBatch)
    def __init__(self, results, currentPage, itemsPerPage=3):
        self.itemsPerPage = itemsPerPage
        if results:
            self.results = results
        else:
            self.results = []
        self.currentPage = currentPage
        self.numberOfPages = len(self.results)/self.itemsPerPage
        if math.fmod(len(self.results), self.itemsPerPage) > 0:
            self.numberOfPages += 1
        
    
    def create(self):
        """
        batch = {
            'total': 5,
            'content': ['item3', 'item4', 'item5'],
            'pages': [
                {'number': 1, 'isCurrent': True},
                {'number': 2, 'isCurrent': False}
            ],
            'prev': {},
            'first': {},
            'next': 2,
            'last': 2
        }
        
        """
        batch = {}
        
        # 'total'
        batch['total'] = len(self.results)
        
        # 'content'
        if self.currentPage == 1:
            start = 0
        else:
            start = (self.currentPage-1)*self.itemsPerPage        
        batch['content'] = self.results[start:start+self.itemsPerPage]
        
        # 'pages'
        pages = []
        for number in range(1, self.numberOfPages+1):
            page = {}
            page['number'] = number
            
            page['isCurrent'] = False
            if number == self.currentPage:
                page['isCurrent'] = True
            
            pages.append(page)
        batch['pages'] = pages
        batch['page'] = self.currentPage
        
        # 'prev', 'first', 'next', 'last'
        if self.currentPage == 1:
            batch['prev'] = {}
            batch['first'] = {}
        else:
            batch['prev'] = {'page': self.currentPage - 1}
            batch['first'] = {'page': 1}
        if (not self.numberOfPages) or (self.currentPage == self.numberOfPages):
            batch['next'] = {}
            batch['last'] = {}
        else:
            batch['next'] = {'page': self.currentPage + 1}
            batch['last'] = {'page': self.numberOfPages}
        
        import logging
        logging.info(batch)
        
        return batch
    

