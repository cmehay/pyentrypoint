All links:
{% for link in links.all %}
    - {{link.uri}}
{% endfor %}

All links 1:
{% for link in links.test1 %}
    - {{link.uri}}
{% endfor %}


Links 2 800:
    - {{links.test2_800.uri}}

All links 2:
{% for link in links.test2 %}
    - {{link.uri}}
{% endfor %}

All environ:
{% for link in links.all %}
    {% for key in link.environ %}
    {{key}}:
        {{link.environ[key] | indent(8)}}
    {% endfor %}
{% endfor %}

All links 2 environ:
{% for link in links.test2 %}
    {% for key in link.environ %}
    {{key}}:
        {{link.environ[key] | indent(8)}}
    {% endfor %}
{% endfor %}

All names:
{% for container in containers %}
    {% for name in container.names %}
    - {{name}}
    {% endfor %}
{% endfor %}

ID:
{% for container in containers %}
    - {{container.id}}
{% endfor %}

ENV:
{% for e in env %}
    '{{e}}': |
        {{ env[e] | indent(8) }}
{% endfor %}

ENVIRON:
{% for e in environ %}
    '{{e}}': |
        {{ env[e] | indent(8) }}
{% endfor %}

JSON:
{% for key, val in json.loads(env['JSON']).items() %}
    '{{key}}': '{{val}}'
{% endfor %}

YAML:
{% for key, val in yaml.load(env['YAML']).items() %}
    '{{key}}': '{{val}}'
{% endfor %}

ENVTOBOOL:
    ok: {{ envtobool('OK', False) }}
    ko: {{ envtobool('KO', True) }}

TOML: |
    {{ toml.dumps(toml.loads(env['TOML'])) | indent }}

CONFIGPARSER: |
    {{ ConfigParser().read_string(env['CONFIGPARSER']).to_string() | indent }}
