# {py:mod}`pycityagent.survey.models`

```{py:module} pycityagent.survey.models
```

```{autodoc2-docstring} pycityagent.survey.models
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`QuestionType <pycityagent.survey.models.QuestionType>`
  -
* - {py:obj}`Question <pycityagent.survey.models.Question>`
  - ```{autodoc2-docstring} pycityagent.survey.models.Question
    :summary:
    ```
* - {py:obj}`Page <pycityagent.survey.models.Page>`
  - ```{autodoc2-docstring} pycityagent.survey.models.Page
    :summary:
    ```
* - {py:obj}`Survey <pycityagent.survey.models.Survey>`
  - ```{autodoc2-docstring} pycityagent.survey.models.Survey
    :summary:
    ```
````

### API

`````{py:class} QuestionType
:canonical: pycityagent.survey.models.QuestionType

Bases: {py:obj}`enum.Enum`

````{py:attribute} TEXT
:canonical: pycityagent.survey.models.QuestionType.TEXT
:value: >
   'text'

```{autodoc2-docstring} pycityagent.survey.models.QuestionType.TEXT
```

````

````{py:attribute} RADIO
:canonical: pycityagent.survey.models.QuestionType.RADIO
:value: >
   'radiogroup'

```{autodoc2-docstring} pycityagent.survey.models.QuestionType.RADIO
```

````

````{py:attribute} CHECKBOX
:canonical: pycityagent.survey.models.QuestionType.CHECKBOX
:value: >
   'checkbox'

```{autodoc2-docstring} pycityagent.survey.models.QuestionType.CHECKBOX
```

````

````{py:attribute} BOOLEAN
:canonical: pycityagent.survey.models.QuestionType.BOOLEAN
:value: >
   'boolean'

```{autodoc2-docstring} pycityagent.survey.models.QuestionType.BOOLEAN
```

````

````{py:attribute} RATING
:canonical: pycityagent.survey.models.QuestionType.RATING
:value: >
   'rating'

```{autodoc2-docstring} pycityagent.survey.models.QuestionType.RATING
```

````

````{py:attribute} MATRIX
:canonical: pycityagent.survey.models.QuestionType.MATRIX
:value: >
   'matrix'

```{autodoc2-docstring} pycityagent.survey.models.QuestionType.MATRIX
```

````

`````

`````{py:class} Question
:canonical: pycityagent.survey.models.Question

```{autodoc2-docstring} pycityagent.survey.models.Question
```

````{py:attribute} name
:canonical: pycityagent.survey.models.Question.name
:type: str
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Question.name
```

````

````{py:attribute} title
:canonical: pycityagent.survey.models.Question.title
:type: str
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Question.title
```

````

````{py:attribute} type
:canonical: pycityagent.survey.models.Question.type
:type: pycityagent.survey.models.QuestionType
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Question.type
```

````

````{py:attribute} choices
:canonical: pycityagent.survey.models.Question.choices
:type: list[str]
:value: >
   'field(...)'

```{autodoc2-docstring} pycityagent.survey.models.Question.choices
```

````

````{py:attribute} columns
:canonical: pycityagent.survey.models.Question.columns
:type: list[str]
:value: >
   'field(...)'

```{autodoc2-docstring} pycityagent.survey.models.Question.columns
```

````

````{py:attribute} rows
:canonical: pycityagent.survey.models.Question.rows
:type: list[str]
:value: >
   'field(...)'

```{autodoc2-docstring} pycityagent.survey.models.Question.rows
```

````

````{py:attribute} required
:canonical: pycityagent.survey.models.Question.required
:type: bool
:value: >
   True

```{autodoc2-docstring} pycityagent.survey.models.Question.required
```

````

````{py:attribute} min_rating
:canonical: pycityagent.survey.models.Question.min_rating
:type: int
:value: >
   1

```{autodoc2-docstring} pycityagent.survey.models.Question.min_rating
```

````

````{py:attribute} max_rating
:canonical: pycityagent.survey.models.Question.max_rating
:type: int
:value: >
   5

```{autodoc2-docstring} pycityagent.survey.models.Question.max_rating
```

````

````{py:method} to_dict() -> dict
:canonical: pycityagent.survey.models.Question.to_dict

```{autodoc2-docstring} pycityagent.survey.models.Question.to_dict
```

````

`````

`````{py:class} Page
:canonical: pycityagent.survey.models.Page

```{autodoc2-docstring} pycityagent.survey.models.Page
```

````{py:attribute} name
:canonical: pycityagent.survey.models.Page.name
:type: str
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Page.name
```

````

````{py:attribute} elements
:canonical: pycityagent.survey.models.Page.elements
:type: list[pycityagent.survey.models.Question]
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Page.elements
```

````

````{py:method} to_dict() -> dict
:canonical: pycityagent.survey.models.Page.to_dict

```{autodoc2-docstring} pycityagent.survey.models.Page.to_dict
```

````

`````

`````{py:class} Survey
:canonical: pycityagent.survey.models.Survey

```{autodoc2-docstring} pycityagent.survey.models.Survey
```

````{py:attribute} id
:canonical: pycityagent.survey.models.Survey.id
:type: uuid.UUID
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Survey.id
```

````

````{py:attribute} title
:canonical: pycityagent.survey.models.Survey.title
:type: str
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Survey.title
```

````

````{py:attribute} description
:canonical: pycityagent.survey.models.Survey.description
:type: str
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Survey.description
```

````

````{py:attribute} pages
:canonical: pycityagent.survey.models.Survey.pages
:type: list[pycityagent.survey.models.Page]
:value: >
   None

```{autodoc2-docstring} pycityagent.survey.models.Survey.pages
```

````

````{py:attribute} responses
:canonical: pycityagent.survey.models.Survey.responses
:type: dict[str, dict]
:value: >
   'field(...)'

```{autodoc2-docstring} pycityagent.survey.models.Survey.responses
```

````

````{py:attribute} created_at
:canonical: pycityagent.survey.models.Survey.created_at
:type: datetime.datetime
:value: >
   'field(...)'

```{autodoc2-docstring} pycityagent.survey.models.Survey.created_at
```

````

````{py:method} to_dict() -> dict
:canonical: pycityagent.survey.models.Survey.to_dict

```{autodoc2-docstring} pycityagent.survey.models.Survey.to_dict
```

````

````{py:method} to_json() -> str
:canonical: pycityagent.survey.models.Survey.to_json

```{autodoc2-docstring} pycityagent.survey.models.Survey.to_json
```

````

````{py:method} from_json(json_str: str) -> pycityagent.survey.models.Survey
:canonical: pycityagent.survey.models.Survey.from_json
:classmethod:

```{autodoc2-docstring} pycityagent.survey.models.Survey.from_json
```

````

`````
