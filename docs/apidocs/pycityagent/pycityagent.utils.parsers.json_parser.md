# {py:mod}`pycityagent.utils.parsers.json_parser`

```{py:module} pycityagent.utils.parsers.json_parser
```

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`JsonObjectParser <pycityagent.utils.parsers.json_parser.JsonObjectParser>`
  - ```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonObjectParser
    :summary:
    ```
* - {py:obj}`JsonDictParser <pycityagent.utils.parsers.json_parser.JsonDictParser>`
  - ```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonDictParser
    :summary:
    ```
````

### API

`````{py:class} JsonObjectParser()
:canonical: pycityagent.utils.parsers.json_parser.JsonObjectParser

Bases: {py:obj}`pycityagent.utils.parsers.parser_base.ParserBase`

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonObjectParser
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonObjectParser.__init__
```

````{py:attribute} tag_start
:canonical: pycityagent.utils.parsers.json_parser.JsonObjectParser.tag_start
:value: >
   '```json'

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonObjectParser.tag_start
```

````

````{py:attribute} tag_end
:canonical: pycityagent.utils.parsers.json_parser.JsonObjectParser.tag_end
:value: >
   '```'

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonObjectParser.tag_end
```

````

````{py:method} parse(response: str) -> typing.Any
:canonical: pycityagent.utils.parsers.json_parser.JsonObjectParser.parse

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonObjectParser.parse
```

````

`````

`````{py:class} JsonDictParser()
:canonical: pycityagent.utils.parsers.json_parser.JsonDictParser

Bases: {py:obj}`pycityagent.utils.parsers.json_parser.JsonObjectParser`

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonDictParser
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonDictParser.__init__
```

````{py:attribute} tag_start
:canonical: pycityagent.utils.parsers.json_parser.JsonDictParser.tag_start
:value: >
   '```json'

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonDictParser.tag_start
```

````

````{py:attribute} tag_end
:canonical: pycityagent.utils.parsers.json_parser.JsonDictParser.tag_end
:value: >
   '```'

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonDictParser.tag_end
```

````

````{py:method} parse(response: str) -> dict
:canonical: pycityagent.utils.parsers.json_parser.JsonDictParser.parse

```{autodoc2-docstring} pycityagent.utils.parsers.json_parser.JsonDictParser.parse
```

````

`````
