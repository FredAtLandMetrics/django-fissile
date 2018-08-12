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
I advocate moving toward a pattern like this:
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

![concrete](https://github.com/FredAtLandMetrics/django-fissile/blob/master/static/images/concrete.png?raw=true "Concrete Data Layer Architecture")

This is a database-as-center-of-the-universe architecture.  It works, but it's suboptimal because:

* All tests for view methods require a database.
* there end up being a lot of duplicate or very similar queries in the code making some types of changes very difficult
* cpu-intensive data processing tasks are competing for system resources against template rendering code

When you add a layer of abstraction around the database access code, the first thing that happens is that all the
duplicate, and often just similar, queries get transformed into calls to a single function or method.  The next thing
happens is that it becomes possible to change the behavior of the data layer at every place that query
had been made by simply updating the single new method.

So the after-pic of this change looks like this:
![abstract](https://github.com/FredAtLandMetrics/django-fissile/blob/master/static/images/abstract.png?raw=true "Abstracted Data Layer Architecture")

This is the point where it begins to make sense to use Fissile.

To use Fissile to split the codebase into frontend and backend servers, simply add the 
`@fissile.func decorator` to all those data layer functions.

Then, in your settings file, you’ll set FISSILE_EXEC_MODE to ‘frontend’ and set 
FISSILE_MODULES to a list of any modules that contain fissile-decorated functions.

To run the backend server, simply run ‘fissile-server’

That’s it.

At this point, the system architecture overview looks like this:

![separate](https://github.com/FredAtLandMetrics/django-fissile/blob/master/static/images/separate.png?raw=true "Separated Data Layer Architecture")

In the context of the example code above, it looks like this:

```python
@fissile.func
def serialized_lkp_thing(p1):
    return to_serializable(
        ThingModel.object.get(
            param1: p1
        )
    )

def my_view():
    return JsonResponse(serialized_lkp_thing('this'))
```

## Feedback
The goal of this project is to grease the righteous path.  It’s like the broom guys
 in olympic curling except it’s for software architecture.
 
I’m still planning out how I want it to work.  If you have anything interesting to 
say about all this, my email address is fred@frameworklabs.us and I’d love to hear 
it.
