# Fissile
Fissile makes good system design with Django a little easier.

## Intro
A frequent pattern in the evolution of a Django application is that:
1) the app starts with changing requirements, lots of ORM code in the views,
   and few tests
2) then, as requirements solidify and the code matures, the ORM code moves
   to domain-specific functions and the data layer is abstracted to hide
   ORM-based implementation details
3) once the data layer is abstracted, the web servers can be broken up into
   front-end and back-end servers along the data layer abstraction divide such
   that the data-specific functions are made available to the views on the
   front-end servers via data-specific API endpoints which map to each
   function
   
The main reason for transitioning from step 1 to step 2 is to make the
codebase easier to test and easier to read.

But the move to step 3 comes with some fairly significant scaling 
opportunities.

First off, the frontend servers no longer communicate with anything but
backend servers and the backend servers are HTTPS.  So the frontend servers
can easily be made asynchronous using Tornado or several other async
frameworks.  Without database connections, the frontend servers scale to
handle many more client connections.

Step 3 also removes the burden of template rendering from the backend servers
so there's no unnecessary CPU load on the server slowing backend data
processing.

Fissile combines step 2 and 3.

## Quickstart
Using Fissile is as simple as:

* all queries to the database (or other external services) should be in
  Fissile functions
* Fissile functions accept only JSON-serializable input and return only
  JSON-serializable output
* use fissile decorator on functions that abstract data access
* use Django settings file to
    * set the execution mode to one of:
        * frontend
        * backend
        * combined
    * set the backend execution selector (only matters if the execution mode is 'backend')
    
## Example
To illustrate how Fissile works, a simple simple follows.

### Brittle Way
In this example, there's no abstraction and the view method is interacting directly with the database.

Any tests we might write would necessarily be dependent on an external component.
```
def my_view():
    return JsonResponse(
        to_serializable(
            ThingModel.object.get(
                param1: 'this'
            )
        )
    )
    
urlpatterns = [
    path('', my_view, name='my_view')
]
```

### Less Brittle Way
This example shows an abstracted data layer.  The view calls the lkp_thing() method which,
in turn, interacts with the database.

To add a test for the view method, we could mock the lkp_thing() method, which would be
very performant, having no external dependencies.

Of course, the test for the lkp_thing() method would still require a database, but if this
were a larger, fairly typical Django codebase, it would be reasonable to expect that this
sort of abstraction pattern would place significantly less demand on a database than a Django
installation which was structured like the code in the previous example.

```
def lkp_thing(p1):
    return to_serializable((
        ThingModel.object.get(
            param1: p1
        )
    )

def my_view():
    return JsonResponse(lkp_thing('this'))
    
urlpatterns = [
    path('myview', my_view, name='my_view')
]
```

### With Fissile
This example uses the fissile decorator on the data layer abstraction method.

With Fissile, the return value of the abstraction layer must be serialized, so there's
a bit more code related to that, but it's pretty much the same except for the decorator,
which defines, among other things, a url route by which the function may be reached via an
HTTP endpoint.

The big difference is that, once a function has been decorated with the @fissile.func
decorator, the app can be configured to translate all calls to the decorated function,
in this case serialized_lkp_thing() to an HTTP request to a backend server, such that the
web service is split into a frontend HTTP server that queries one or more backend HTTP
servers for data.
```
@fissile.func(url='thing/<param1>/', selector='thing', name='thing_search')
def serialized_lkp_thing(p1):
    return to_serializable(
        ThingModel.object.get(
            param1: p1
        )
    )

def my_view():
    return JsonResponse(serialized_lkp_thing('this'))
    
urlpatterns = [
    path('myview', my_view, name='my_view')
]
fissile.append_urls(urlpatterns, [serialized_lkp_thing.to_path()])
```