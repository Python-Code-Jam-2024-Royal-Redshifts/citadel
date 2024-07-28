Your task is to generate JSON data from a list of questions and answers supplied by the user. The exactly format isn't known, but the user should be starting questions with "Q:" and answers with "A:". This isn't guaranteed though, and you **MUST** use your best judgement to **ALWAYS** output a list of questions and answers.

You **MUST** output the questions and answers in JSON format, **WITHOUT** enclosing such inside of a code block. Your JSON output will be a JSON array containing JSON objects. The object will contain JSON keys of `question` and `answer`. For example, if you were to encounter the message "Q: What is the square root of 4?" followed by "A: 26", you would output the following (without the backticks from the code fence):
```json
[{ "question": "What is the square root of 4?", "answer": "26"}]
```

The JSON data will be the **ONLY** output you respond with.

Using the previously mentioned JSON rules, generate the questions/answers for the following text:

{{ question_data }}
