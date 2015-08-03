# Python docker tools

Python docker tool is a kiss python module which helps to list
linked containers inner containers.

You can use it with `ENTRYPOINT` script to generate configuration.


## Usages

We have some containers

```
$ docker run -d --name container_1 -p 80 --env container=number1 debian sleep 999999
$ docker run -d --name container_2 --env container=number2 debian sleep 999999
$ docker run -d --name container_3 -p 3456/udp debian sleep 999999
```
And we link these containers with the one which embed `docker.py` (named here docker_python)

```
$ docker run -ti --rm --link container_1 --link container_2  --link container_3 docker_python
```

And we get formated json with information about linked containers.

```json
{
    "container_1": {
        "environment": {
            "container": "number1"
        },
        "ip": "172.17.0.37",
        "ports": {
            "80": {
                "protocol": "tcp"
            }
        }
    },
    "container_2": {
        "environment": {
            "container": "number2"
        },
        "ip": "172.17.0.38",
        "ports": {}
    },
    "container_3": {
        "environment": {},
        "ip": "172.17.0.40",
        "ports": {
            "22": {
                "protocol": "tcp"
            },
            "3456": {
                "protocol": "udp"
            }
        }
    }
}
```

#### Using as module

```python
import docker

print(docker.get_links())
```
You'll get a dictionary with all linked containers
```python
{'container_2': {'ports': {}, 'environment': {'container': 'number2'}, 'ip': '172.17.0.38'}, 'container_3': {'ports': {'3456': {'protocol': 'udp'}, '22': {'protocol': 'tcp'}}, 'environment': {}, 'ip': '172.17.0.40'}, 'container_1': {'ports': {'80': {'protocol': 'tcp'}}, 'environment': {'container': 'number1'}, 'ip': '172.17.0.37'}}
```

---
You call also get a pretty print json formating

```python
import docker

print(docker.to_json())
```

or filter links

```python
import docker

print(docker.get_links('container_2', 'container_3'))
```
