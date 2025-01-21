# {py:mod}`pycityagent.utils.parsers.code_block_parser`

```{py:module} pycityagent.utils.parsers.code_block_parser
```

```{autodoc2-docstring} pycityagent.utils.parsers.code_block_parser
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CodeBlockParser <pycityagent.utils.parsers.code_block_parser.CodeBlockParser>`
  - ```{autodoc2-docstring} pycityagent.utils.parsers.code_block_parser.CodeBlockParser
    :summary:
    ```
````

### API

`````{py:class} CodeBlockParser(language_name: str)
:canonical: pycityagent.utils.parsers.code_block_parser.CodeBlockParser

Bases: {py:obj}`pycityagent.utils.parsers.parser_base.ParserBase`

```{autodoc2-docstring} pycityagent.utils.parsers.code_block_parser.CodeBlockParser
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.utils.parsers.code_block_parser.CodeBlockParser.__init__
```

````{py:attribute} tag_start
:canonical: pycityagent.utils.parsers.code_block_parser.CodeBlockParser.tag_start
:value: >
   '```{language_name}'

```{autodoc2-docstring} pycityagent.utils.parsers.code_block_parser.CodeBlockParser.tag_start
```

````

````{py:attribute} tag_end
:canonical: pycityagent.utils.parsers.code_block_parser.CodeBlockParser.tag_end
:value: >
   '```'

```{autodoc2-docstring} pycityagent.utils.parsers.code_block_parser.CodeBlockParser.tag_end
```

````

````{py:method} parse(response: str) -> str
:canonical: pycityagent.utils.parsers.code_block_parser.CodeBlockParser.parse

```{autodoc2-docstring} pycityagent.utils.parsers.code_block_parser.CodeBlockParser.parse
```

````

`````
