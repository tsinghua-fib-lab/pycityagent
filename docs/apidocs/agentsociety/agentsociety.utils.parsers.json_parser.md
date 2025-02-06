# {py:mod}`agentsociety.utils.parsers.json_parser`

```{py:module} agentsociety.utils.parsers.json_parser
```

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`JsonObjectParser <agentsociety.utils.parsers.json_parser.JsonObjectParser>`
  - ```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonObjectParser
    :summary:
    ```
* - {py:obj}`JsonDictParser <agentsociety.utils.parsers.json_parser.JsonDictParser>`
  - ```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonDictParser
    :summary:
    ```
````

### API

`````{py:class} JsonObjectParser()
:canonical: agentsociety.utils.parsers.json_parser.JsonObjectParser

Bases: {py:obj}`agentsociety.utils.parsers.parser_base.ParserBase`

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonObjectParser
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonObjectParser.__init__
```

````{py:attribute} tag_start
:canonical: agentsociety.utils.parsers.json_parser.JsonObjectParser.tag_start
:value: >
   '```json'

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonObjectParser.tag_start
```

````

````{py:attribute} tag_end
:canonical: agentsociety.utils.parsers.json_parser.JsonObjectParser.tag_end
:value: >
   '```'

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonObjectParser.tag_end
```

````

````{py:method} parse(response: str) -> typing.Any
:canonical: agentsociety.utils.parsers.json_parser.JsonObjectParser.parse

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonObjectParser.parse
```

````

`````

`````{py:class} JsonDictParser()
:canonical: agentsociety.utils.parsers.json_parser.JsonDictParser

Bases: {py:obj}`agentsociety.utils.parsers.json_parser.JsonObjectParser`

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonDictParser
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonDictParser.__init__
```

````{py:attribute} tag_start
:canonical: agentsociety.utils.parsers.json_parser.JsonDictParser.tag_start
:value: >
   '```json'

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonDictParser.tag_start
```

````

````{py:attribute} tag_end
:canonical: agentsociety.utils.parsers.json_parser.JsonDictParser.tag_end
:value: >
   '```'

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonDictParser.tag_end
```

````

````{py:method} parse(response: str) -> dict
:canonical: agentsociety.utils.parsers.json_parser.JsonDictParser.parse

```{autodoc2-docstring} agentsociety.utils.parsers.json_parser.JsonDictParser.parse
```

````

`````
