# {py:mod}`agentsociety.utils.parsers.parser_base`

```{py:module} agentsociety.utils.parsers.parser_base
```

```{autodoc2-docstring} agentsociety.utils.parsers.parser_base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ParserBase <agentsociety.utils.parsers.parser_base.ParserBase>`
  -
````

### API

`````{py:class} ParserBase()
:canonical: agentsociety.utils.parsers.parser_base.ParserBase

Bases: {py:obj}`abc.ABC`

````{py:method} parse(response: str) -> typing.Any
:canonical: agentsociety.utils.parsers.parser_base.ParserBase.parse
:abstractmethod:

```{autodoc2-docstring} agentsociety.utils.parsers.parser_base.ParserBase.parse
```

````

````{py:method} _extract_text_within_tags(response: str, tag_start: str, tag_end: str) -> str
:canonical: agentsociety.utils.parsers.parser_base.ParserBase._extract_text_within_tags

```{autodoc2-docstring} agentsociety.utils.parsers.parser_base.ParserBase._extract_text_within_tags
```

````

`````
