SECRET:
{% for key, secret in secrets,items() %}
    '{{key}}': '{{secret}}'
{% endfor %}
