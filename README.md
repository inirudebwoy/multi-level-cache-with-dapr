# What is it?

This is a simple example of how to use Dapr to create 2 level cache.
Thread cache combined with shared cache (Redis based). With DAPR 
the cache can be in any store state supported by Dapr.

# Pre-requisites

- Dapr
- Python 3.12 (or any modern version of Python)

# How to use it

Run the application with Dapr
```bash
make dapr-run
```

Then make some requests to the application in other terminal window
```bash

curl http://localhost:8000/get?key=donuts
> "0245178074fd042e19b7c3885b360fc21064b30e73f5626c7e3b005d048069c5"

```
Observe in application logs that the first request is not served from cache.
Next requests will be served from cache. 
In order to make sure that shared cache is used, you can make change to code base  (the app will reload) and rerun the http call from above. 
