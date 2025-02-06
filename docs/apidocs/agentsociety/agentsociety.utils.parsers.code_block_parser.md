# {py:mod}`agentsociety.utils.parsers.code_block_parser`

```{py:module} agentsociety.utils.parsers.code_block_parser
```

```{autodoc2-docstring} agentsociety.utils.parsers.code_block_parser
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CodeBlockParser <agentsociety.utils.parsers.code_block_parser.CodeBlockParser>`
  - ```{autodoc2-docstring} agentsociety.utils.parsers.code_block_parser.CodeBlockParser
    :summary:
    ```
````

### API

`````{py:class} CodeBlockParser(language_name: str)
:canonical: agentsociety.utils.parsers.code_block_parser.CodeBlockParser

Bases: {py:obj}`agentsociety.utils.parsers.parser_base.ParserBase`

```{autodoc2-docstring} agentsociety.utils.parsers.code_block_parser.CodeBlockParser
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.utils.parsers.code_block_parser.CodeBlockParser.__init__
```

````{py:attribute} tag_start
:canonical: agentsociety.utils.parsers.code_block_parser.CodeBlockParser.tag_start
:value: >
   '```{language_name}'

```{autodoc2-docstring} agentsociety.utils.parsers.code_block_parser.CodeBlockParser.tag_start
```

````

````{py:attribute} tag_end
:canonical: agentsociety.utils.parsers.code_block_parser.CodeBlockParser.tag_end
:value: >
   '```'

```{autodoc2-docstring} agentsociety.utils.parsers.code_block_parser.CodeBlockParser.tag_end
```

````

````{py:method} parse(response: str) -> str
:canonical: agentsociety.utils.parsers.code_block_parser.CodeBlockParser.parse

```{autodoc2-docstring} agentsociety.utils.parsers.code_block_parser.CodeBlockParser.parse
```

````

`````
