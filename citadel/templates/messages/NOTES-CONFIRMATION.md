The following questions were detected from your filter:

{% for note in notes -%}
> **{{ note.question }}**
> {{ note.answer }}

{% endfor -%}
Would you like to create the test for **{{ test_name }}**, or edit its questions?
