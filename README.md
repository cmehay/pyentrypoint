# py_docker_links

py_docker_links is a kiss python module which helps to list
linked containers inner containers.

You can use it with `ENTRYPOINT` script to generate configuration.


## Usages

We have some containers described in `docker-compose.yml`

```yaml
# Here some dummies containers
test1:
    image: busybox
    command: sleep 30
    expose:
        - 800
        - 8001/udp
    environment:
        FOO: bar

test2:
    image: busybox
    command: sleep 30
    expose:
        - 800/udp
        - 8001

test3:
    image: busybox
    command: sleep 30
    environment:
        FOO: bar


# Here our container that embed docker_links.py linked
# with dummies containers
dockerlinks:
    build: .
    dockerfile: Dockerfile.py3
    command: python docker_links.py
    links:
        - test1
        - test2
        - test3
```

Start them

```shell
$ docker-compose build && docker-compose up dockerlinks
```

We should get formated json with informations about linked containers.

```json
{
    "172.17.0.2": {
        "environment": {
            "FOO": "bar",
            "affinity:container": "=a5601d5d225a3e57ea295c7646468067dd1859d4b2ee4574b5bf5542ed372e59"
        },
        "names": [
            "d778f6ef9371",
            "pythondockertools_test3_1",
            "test3",
            "test3_1"
        ],
        "ports": {}
    },
    "172.17.0.3": {
        "environment": {
            "affinity:container": "=78393f27c629fc426af5837a11d30720c8af7a5e029eb173b394f207e7e4701c"
        },
        "names": [
            "5fc12cf7b49e",
            "pythondockertools_test2_1",
            "test2",
            "test2_1"
        ],
        "ports": {
            "800": {
                "protocol": "tcp"
            },
            "8001": {
                "protocol": "tcp"
            }
        }
    },
    "172.17.0.4": {
        "environment": {
            "FOO": "bar",
            "affinity:container": "=6a31a66a1aafcd607763dcd916b81b4385a3baf4354c044345255c3eb0bce925"
        },
        "names": [
            "d32fc2303721",
            "pythondockertools_test1_1",
            "test1",
            "test1_1"
        ],
        "ports": {
            "800": {
                "protocol": "tcp"
            },
            "8001": {
                "protocol": "udp"
            }
        }
    }
}
```

#### Using as module

```python
from docker_links import DockerLinks

links = DockerLinks()

print(links.links())
```
You'll get a dictionary with all linked containers
```python
{'172.17.0.2': {'environment': {'affinity:container': '=6a31a66a1aafcd607763dcd916b81b4385a3baf4354c044345255c3eb0bce925', 'FOO': 'bar'}, 'ports': {'800': {'protocol': 'tcp'}, '8001': {'protocol': 'udp'}}, 'names': ['d32fc2303721', 'pythondockertools_test1_1', 'test1', 'test1_1']}, '172.17.0.3': {'environment': {'affinity:container': '=78393f27c629fc426af5837a11d30720c8af7a5e029eb173b394f207e7e4701c'}, 'ports': {'800': {'protocol': 'tcp'}, '8001': {'protocol': 'tcp'}}, 'names': ['5fc12cf7b49e', 'pythondockertools_test2_1', 'test2', 'test2_1']}, '172.17.0.5': {'environment': {'affinity:container': '=a5601d5d225a3e57ea295c7646468067dd1859d4b2ee4574b5bf5542ed372e59', 'FOO': 'bar'}, 'ports': {}, 'names': ['d778f6ef9371', 'pythondockertools_test3_1', 'test3', 'test3_1']}}

```

---
You call also get a pretty print json formating

```python
from docker_links import DockerLinks

links = DockerLinks()

print(links.to_json())
```

or filter links

```python
from docker_links import DockerLinks

links = DockerLinks()

print(links.links('test1', 'test2')) # It also works with container uid
```


### Running Tests

To run tests, ensure that docker-compose is installed and run

```shell
docker-compose build && docker-compose up testpython2 testpython3
