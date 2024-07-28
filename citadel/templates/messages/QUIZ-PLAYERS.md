**Current Players:**
{% if players|length == 0 -%}
*No one is in the quiz. Deleting...*
{% else -%}
{% for player in players -%}
- {{ player }}
{% endfor -%}
{% endif -%}
