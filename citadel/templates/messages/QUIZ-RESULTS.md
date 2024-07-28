### Results
{% for person in leaderboard[0] -%}
**1st Place:** {{ person[0].display_name }} ({{ person[1].points }} points, {{ person[1].correct }}/{{ question_total }} correct)
{% endfor -%}
{% for person in leaderboard[1] -%}
**2nd Place:** {{ person[0].display_name }} ({{ person[1].points }} points, {{ person[1].correct }}/{{ question_total }} correct)
{% endfor -%}
{% for person in leaderboard[2] -%}
**3rd Place:** {{ person[0].display_name }} ({{ person[1].points }} points, {{ person[1].correct }}/{{ question_total }} correct)
{% endfor -%}
