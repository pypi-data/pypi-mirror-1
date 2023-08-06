# Clearwind Consulting Ltd, 2010
# BSD License
# based on work by mmalone
import sys
from django.core.paginator import Paginator, Page, InvalidPage

class LazyPaginator(Paginator):
    max_safe_pages = 0

    def __init__(self, object_list, per_page, orphans=0, 
            allow_empty_first_page=True, max_safe_pages=1000):
        self.max_safe_pages = max_safe_pages
        super(LazyPaginator, self).__init__(object_list, per_page, 
            orphans=orphans, allow_empty_first_page=allow_empty_first_page)

    def validate_number(self, number):
        try:
            number = int(number)
        except:
            raise InvalidPage
        if number <= self.max_safe_pages:
            return number
        return super(LazyPaginator, self).validate_number(number)
    
    def _get_num_pages(self):
        return self.max_safe_pages
    num_pages = property(_get_num_pages)

    def page(self, number):
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page

        # get one extra object to see if there is a next page
        page = list(self.object_list[bottom:top + 1])
        if len(page) > self.per_page:
            # if we got an extra object, update max_safe_pages
            if number + 1 > self.max_safe_pages:
                self.max_safe_pages = number + 1
            page = page[:self.per_page]
        if number > 0 and len(page) == 0:
            raise InvalidPage
            
        return Page(self.object_list[bottom:top], number, self)

    def has_next(self, number):
        if number < self.max_safe_pages:
            return True
        return super(LazyPaginator, self).has_next(number)

    def last_on_page(self, number):
        """
        Returns the 1-based index of the last object on the given page,
        relative to total objects found (hits).
        """
        number = self.validate_number(number)
        if number >= self.max_safe_pages:
            return super(LazyPaginator, self).last_on_page(number)
        number += 1 # 1-base
        return number * self.per_page
