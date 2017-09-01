TODO: project name
==================

TODO: project description
-------------------------

TODO: build status icon


### Offline Data Synchronization

This package provides support of data synchronization by offline clients, such as mobile applications. This is accomplished by the following approach:
* Aggregate list endpoints per object type are exposed. This allows all objects of a given type to be retrieved in a single request, even if they are nested into different objects. For example, in the hierarchy notebook/note, there is a note list endpoint that returns all notes from all notebooks.
  - The choice to expose one endpoint per object type, as opposed to a single endpoint for all synchronized types, was made because the latter approach produces a response that is an object (as opposed to a list). This does not allow paginating responses and forces the use of a single request. Avoiding multiple round-trip times is still possible by pipelining requests for different object types.
* List endpoints allow the client to specify the minimum modification time of the returned objects. The returned data contains the request execution timestamp. To synchronize incrementally, the client must store this timestamp and send it as the minimum modification time during their next synchronization.
  - Since the synchronization is performed across multiple requests, their results may be inconsistent if objects are modified between the requests. To counter this, the endpoints also accept the maximum modification timestamp of the returned objects as a parameter. All requests after the first one in a single synchronization session should set this parameter to the request execution timestamp from the first response.
* Deletion of objects is performed softly. Upon deletion, a hidden flag is toggled, but the data itself is not removed. This allows offline clients to detect which locally-existing objects have been deleted on the server.
  - However, to preserve system resources, objects that are deleted a specified time ago are periodically removed. Also, the number of deleted objects is limited. When an object is being deleted and this limit is reached, the object with the oldest deletion timestamp is removed.
* Deleted objects are listed in separate (aggregate) endpoints, which also accept a minimum deletion timestamp parameter.
  - The server is able to detect if the generated listing is complete for the requested minimum modification timestamp. If objects may have removed due to expiry or an exceeded limit, a different response status code is returned. In this case, the client must retrieve the full list of non-deleted objects and determine the deleted ones by comparing to their local database.

#### Conflict Detection

The package also supports conflict detection when a write request is made from a client for an object, whose contents on the client are older than the contents on the server. This is beneficial for offline as well as online clients. The approach is the following:
* Endpoints that modify the state of an object accept a last modification timestamp. Clients shall set it to the object's modification timestamp in their database. If it does not match the object's modification timestamp on the server, the request is rejected.
* When a conflict occurs, it is up to the client to decide how to handle it. Some possibilities are:
  - Synchronize the newer object state on both sides.
  - Create a copy of the object.
  - Duplicate the two versions on both sides.


### Requirements

* Python 3 (tested with 3.6)
* Django (tested with 1.11)
* Django REST Framework (tested with 3.6)


### Usage

1. Install the package:
```
pip install django-rest-offline
```

2. Add the package to Django's list of installed apps in your project's *settings.py*:
```
INSTALLED_APPS = [
    ...
    'rest_offline',
    ...
]
```

3. Inherit your models from *rest_offline.models.TrackedModel*:
```
from rest_offline.models import TrackedModel
class Document(TrackedModel):
    ...
```

4. Inherit your viewsets from *rest_offline.sync.SyncedModelMixin*:
```
from rest_framework import viewsets
from rest_offline import sync
class DocumentViewSet(sync.SyncedModelMixin,
                      ...
                      viewsets.ModelViewSet):
    ...
```

5. Declare your viewsets' querysets:
```
    queryset = Document.objects.all()
```
**NOTE:** This is required because the set of viewset mixins in this package override *get_queryset()* to chain-manipulate the queryset of each mixin, and the "base" queryset is defined with this attribute. If you override *get_queryset()* to perform per-request queryset manipulation, you **must** call the superclass's method and start from its result.

6. Configure the expiry delay of deleted objects in *settings.py*:
```
REST_OFFLINE = {
    'DELETED_EXPIRY_DAYS': 30,
    ...
}
```
You can use `None` or `0` for unlimited.

Your viewsets will now:
* accept minimum and maximum modification timestamp arguments (*since* and *until*) for their list endpoints
  - these endpoints return both timestamps in the response body
  - if the maximum modification timestamp is not specified, the execution time is returned
* accept a current modification timestamp argument (*at*) for their write endpoints, and concurrency-safely enforce it
  - if the specified modification timestamp does not match the current one, the operation is not performed and http status 409 is returned
  - write operations are guaranteed to increment the object modification timestamp for reliable conflict detection
* perform soft deletion
* not show deleted objects in list results
* return http status 404 for requests to deleted objects
* expose endpoints that list deleted objects (*./deleted/*)
  - these endpoints indicate possibly incomplete results by returning http status 206

#### Clearing Expired Deleted Objects

A management command is provided to clear expired deleted objects. To invoke it:
```
python manage.py cleardeleted
```
The output is the number of cleared objects per tracked model.


### Synchronization and Model Relationships

Relationships between synchronized models are supported by the *NestedModelMixin* viewset mixin.

#### Resource Nesting and Aggregation


### Resource Quotas

Quotas (limits) of synchronized models are supported by the *LimitedNestedSynced* viewset mixin.


### Example Project

For a working example project that integrates this package, see the */example* directory. To run it:
```
cd example
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
