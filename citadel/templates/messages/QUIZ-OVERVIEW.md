### Question {{ question_number }}/{{ question_total }}
{% for person in leaderboard[0] -%}
**1st Place:** {{ person[0].display_name }} ({{ person[1].points }} points)
{% endfor -%}
{% for person in leaderboard[1] -%}
**2nd Place:** {{ person[0].display_name }} ({{ person[1].points }} points)
{% endfor -%}
{% for person in leaderboard[2] -%}
**3rd Place:** {{ person[0].display_name }} ({{ person[1].points }} points)
{% endfor -%}
{% for person in leaderboard[3] -%}
**4rd Place:** {{ person[0].display_name }} ({{ person[1].points }} points)
{% endfor -%}
{% for person in leaderboard[4] -%}
**5rd Place:** {{ person[0].display_name }} ({{ person[1].points }} points)
{% endfor -%}

*Continuing in {{ seconds }} {{ "seconds" if seconds != 1 else "second" }}*
