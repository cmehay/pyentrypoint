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
    {% for key in link.env %}
    {{key}}: {{link.env[key]}}
    {% endfor %}
{% endfor %}

All links 2 environ:
{% for link in links.test2 %}
    {% for key in link.env %}
    {{key}}: {{link.env[key]}}
    {% endfor %}
{% endfor %}

All names:
{% for container in containers %}
    {% for name in container.names %}
    - {{name}}
    {% endfor %}
{% endfor %}
