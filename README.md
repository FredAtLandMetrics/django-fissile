# For *salaried* perfectionists with deadlines
In other, less tongue-in-cheek words, Fissile lends developers a few decorators and run-time 
config options that improve legibility, scalability, and testability in complex Django sites.

Proper use of Fissile makes Django a more manageable place.

## Why? Django is so perfect already...
### Old habits
A long time ago (think pre-Rails), I got in the habit of sequestering any code I wrote that 
interacted with a database behind a domain-based set of modules.  I’d figured out that there 
was a lot of redundant code strewn about and wrangling it to well-defined data layer kept 
things tidy.

Later, when I adopted some TDD practices, I found that testing these data-layer methods 
required a database connection, which was unfortunate, but when I figured out how to use 
mock (or whatever terrible substitute I’d come up with before I found mock), I found that 
testing calls to these methods was easy and fast.

It was handy too when I needed to make a fairly significant change like a switch from one 
database to another or when I needed to split a database across multiple servers.  The 
surface area of the data layer was literally as small as possible (ideally) so such 
changes were a lot more tractable than they would otherwise have been.

If I needed to do some caching to ease the pressure on the database, it was a relatively 
straightforward thing to do.  If I needed to separate frontend template-rendering code from 
backend processor- and/or network-hungry backend services, the data layer methods made a 
conveniently small set of changes necessary to achieve the goal.

It worked well enough that, once,  when I was contracted to work on a Rails project that was 
particularly riddled with comments like “Beware all those who pass by this comment!” and 
“Here be dragons!”, my precondition for accepting the contract was that we first be allowed 
to move all database interactions out of the top-level controller methods and into 
domain-based modules that could be tested and instrumented.

### New Challenges
So, more recently, I’m involved with a codebase that’s very mature and reasonably 
well-behaved.  But it’s hard to work with because it just interacts with the database 
wherever and however it needs to.  Tests take __for-ev-er__ because most of them interact 
with the database.  Don’t get me wrong, there’s high-quality code in there, but sometimes 
it is very difficult and/or time-consuming to work with.

In a very real way, it just burns money and that bugs me.  So I conceived of this construct 
to speed along its beautification.  Ideally, it will achieve my selfish goal of wanting to 
constrain the wild ORM rumpus and, at the same time, it will make some very provable gains 
in testability and scalability.

## The Quantified Problem and The Fix
### the Quantified Problem

### The Fix
The first part of the fix for the slippage of the understandable and lawful world into 
wildly prolific database-active code is to wrestle any and all code that interacts with 
the database into a limited set of domain-specific methods.  There should be no leakage 
of information about the storage mechanism into the rest of the codebase.  Is my business 
logic stored in the database?  On a disk?  On a blockchain?  You won’t know by looking at 
the data layer methods.

That part has nothing to do with Fissile.  But it’s a Good Idea.  You can limit your 
integration tests to only those methods that need to interact with the database and 
everything else is a very fast unit test.  If you stop here, you will have done great 
things for the maintainability of your codebase.

Fissile simply makes it easy to split the codebase into front-end and back-end services.  
It adds a @fissile.func decorator that allows the frontend server and to interact with a 
function as it would without the decorator but, unbeknownst to the caller, cause an HTTP 
query to a backend service that will perform the data layer actions.

Since the front-end servers end up depending only on the availability of the backend 
servers, it is often possible to leverage the performance improvements of asynchronous 
HTTP servers.  In any case, the delineation ensures that processor-intensive data 
operations aren’t competing with template rendering code for resources.

## Usage
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
    
### Example
To illustrate how Fissile works, a simple simple follows.

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
