This is a paginator that does not do a count. 

** Warning this needs work :)

It started with this:

http://www.agmweb.ca/blog/andy/2226/

Then there was excellent idea from mmalone and an excellent gist:

http://gist.github.com/213702

So then this got updated for the latest Django and became this.

Example:

>>> from django.db import connection
>>> from listener.models.error import Error
>>> queryset = Error.objects.filter(account=1, archived=1)

The old way:

>>> from django.core.paginator import Paginator 
>>> p = Paginator(queryset, 10)
>>> p.page(1)
<Page 1 of 859>

Causes:

>>> connection.queries
[ {'time': '21.953', 'sql': 'SELECT COUNT(*) FROM "listener_error" WHERE ("listener_error"."account_id" = 1  AND "listener_error"."archived" = true )'}]

That's one query. To get the object list it does another.

>>> p.page(1).object_list
[{'time': '0.000', 'sql': 'SELECT "listener_error"."id", ... FROM "listener_error" WHERE ("listener_error"."account_id" = 1  AND "listener_error"."archived" = true ) LIMIT 10'}]

The problem is that count can be hideously expensive.

The new way:

>>> from lazy_paginator.paginator import LazyPaginator 
>>> p = LazyPaginator(queryset, 10)
>>> p.page(1)
<Page 1 of 1000>

>>> connection.queries     
[{'time': '0.000', 'sql': 'SELECT "listener_error"."id",... FROM "listener_error" WHERE ("listener_error"."account_id" = 1  AND "listener_error"."archived" = true ) LIMIT 11'}]

>>> p.page(1).object_list
[{'time': '0.000', 'sql': 'SELECT "listener_error"."id",... FROM "listener_error" WHERE ("listener_error"."account_id" = 1  AND "listener_error"."archived" = true ) LIMIT 10'}]

By doing a query for one more than you need, it figures out if there's a next. The difference is the select vs the count.

What do you lose? You don't know how many records there are, you just know if there is a next and previous (and you can figure out how many came before). But if you are using postgresql, beware of how expensive those counts can be.

The default assumes there's going to be 1000 pages, but we don't really know how many there. There's a max_safe_pages variable that gets updated as information is provided. For example if you set it to 3 pages... when try and access 4, it fail, thinking that there was no data.

>>> p = LazyPaginator(queryset, 10, max_safe_pages=3)
>>> p.has_next(1)
True
>>> p.has_next(2)
True
>>> p.has_next(3)
False
>>> p.has_next(4)
False
>>> p.page(4)    
Traceback (most recent call last):
  File "<console>", line 1, in <module>
  File "/var/arecibo/lazy_paginator/paginator.py", line 27, in page
    number = self.validate_number(number)
  File "/var/arecibo/lazy_paginator/paginator.py", line 20, in validate_number
    return super(LazyPaginator, self).validate_number(number)
  File "/usr/lib/python2.5/site-packages/django/core/paginator.py", line 32, in validate_number
    raise EmptyPage('That page contains no results')
EmptyPage: That page contains no results

Now if you start at the beginning:

>>> p.page(2)
<Page 2 of 3>
>>> p.page(3)
<Page 3 of 4>
>>> p.page(4)
<Page 4 of 5>

That can be a bit confusing, perhaps in the future it should check and if not then try to get it... improvements welcome.