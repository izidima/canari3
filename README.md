# Canari 3 ![Build Status](https://circleci.com/gh/redcanari/canari3.svg?style=shield&circle-token=da787a222c75b0a739152d0aa92a9465f702bae6) ![Doc Status](https://readthedocs.org/projects/canari3/badge/?version=latest)

Welcome to the Canari 3 repository - the next generation Maltego rapid transform development framework which allows you
to rapidly prototype, package, and distribute Maltego local and remote transforms. Please visit the 
[documentation](http://canari3.readthedocs.io/en/latest/) site for a quick how-to and more in-depth information on the
framework itself.

## Sneak Peek

The following is an example of how easy it is to write a quick Maltego transform in Canari 3:

```python

from canari.maltego.entities import Phrase, Person

class HelloWorld(Transform):
    """This transform says hello to a person entity."""

    # The transform input entity type.
    input_type = Person

    def do_transform(self, request, response, config):
        return response + Phrase("Hello " + request.entity.value)
```

## Canari Docker

You can now dockerize your remote transform packages using `canari dockerize-package`. This will create a Docker 
container that runs Canari Plume fully configured with your remote transforms. You can easily distribute this container
to your Docker swarm. Check out the documentation on Docker [website](http://docker.com) for more information on how
containers work.

## Bug Reports & Questions
Please use the issues page to log any bugs or questions regarding the Canari Framework. 
 
## Kudos

Kudos to our user community for making this release happen. A special thanks to those of you who have supported the
development of Canari 3 by donating money at our crowd-funding pages. If you like this project, please consider donating
money to help accelerate development. 
 
<a href='https://pledgie.com/campaigns/30181'><img alt='Click here to lend your support to: Help the Canari Framework get to Version 3.0 and make a donation at pledgie.com !' src='https://pledgie.com/campaigns/30181.png?skin_name=chrome' border='0' ></a>