# For *salaried* perfectionists with deadlines
In other, less tongue-in-cheek words, Fissile lends developers a few decorators
and run-time config options that improve legibility, scalability, and testability
in complex Django sites.

It makes Django a more manageable place.

## The Problem
I’ve recently been working with a codebase that’s very mature and the data layer
is very concrete and difficult to change because there is no abstraction at all
and the ORM code is sprinkled throughout the view methods and anywhere else it’s
needed.  Running the entire test suite spans the better part of a lunch break
because nearly every test is an integration test involving the code and the 
database.

Fissile is a result of my brainstorming about a possible path forward for this 
codebase.

Its goal is to magnify the benefits of moving toward a better architecture 
pattern.  The hard work of separating out the data access code will still be a 
pain, but, with Fissile, the benefit of the split into frontend and backend comes 
at very little additional cost, so the gains in maintainability and testability 
will coincide with a drastic performance improvement.

## The Fix
So what I’m suggesting is that developers go through their code and replace any 
database-accessing code with a call to a function or method whose name pretty 
accurately describe what’s actually happening.  And that function can/should/will 
pretty much just wrap the original database-accessing code.  That’s step #1.  For 
my use-case, I suspect this will speed tests by at least 50%.

Splitting these functions off into modules that make  sense is fine, but the big 
idea is just hiding the implementation details about the data storage and query 
mechanism behind functions that don’t leak any details about how things work 
behind the scenes.

So, where a view method might look like this:
```python
def my_view():
    return JsonResponse(
        to_serializable(
            ThingModel.object.get(
                param1: 'this'
            )
        )
    )
```
I'd suggest moving toward a pattern like this:
```python
def lkp_thing(p1):
    return to_serializable((
        ThingModel.object.get(
            param1: p1
        )
    )

def my_view():
    return JsonResponse(lkp_thing('this'))
```

From a system-overview perspective, the before-pic looks like this:

![concrete](https://github.com/FredAtLandMetrics/django-fissile/blob/master/static/images/concrete.png?raw=true "Concrete Data Layer Architecture" | width=100%)

This is a database-as-center-of-the-universe architecture.  It works, but it's suboptimal because:

* All tests for view methods require a database.
* there end up being a lot of duplicate or very similar queries in the code making some types of changes very difficult
* cpu-intensive data processing tasks are competing for system resources against template rendering code

Next, to split the codebase into frontend and backend servers, simply add the 
`@fissile.func decorator` to all those data layer functions.

Then, in your settings file, you’ll set FISSILE_EXEC_MODE to ‘frontend’ and set 
FISSILE_MODULES to a list of any modules that contain fissile-decorated functions.

To run the backend server, simply run ‘fissile-server’

That’s it.

## Feedback
The goal of this project is to grease the righteous path.  It’s like the broom guys
 in olympic curling except it’s for software architecture.
 
I’m still planning out how I want it to work.  If you have anything interesting to 
say about all this, my email address is fred@frameworklabs.us and I’d love to hear 
it.
************ OLD **************
#### Brittle Way
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

#### Less Brittle Way
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

#### With Fissile
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

## Feedback
The goal of this project is to grease the righteous path.  It’s like olympic curling 
except for software architecture.

I’m still planning out how I want it to work.  If you have anything interesting to say
 about all this, my email address is fred@frameworklabs.us and I’d love to hear it.
