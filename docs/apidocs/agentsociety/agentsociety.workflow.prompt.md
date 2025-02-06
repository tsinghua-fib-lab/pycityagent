# {py:mod}`agentsociety.workflow.prompt`

```{py:module} agentsociety.workflow.prompt
```

```{autodoc2-docstring} agentsociety.workflow.prompt
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FormatPrompt <agentsociety.workflow.prompt.FormatPrompt>`
  - ```{autodoc2-docstring} agentsociety.workflow.prompt.FormatPrompt
    :summary:
    ```
````

### API

`````{py:class} FormatPrompt(template: str, system_prompt: typing.Optional[str] = None)
:canonical: agentsociety.workflow.prompt.FormatPrompt

```{autodoc2-docstring} agentsociety.workflow.prompt.FormatPrompt
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.workflow.prompt.FormatPrompt.__init__
```

````{py:method} _extract_variables() -> list[str]
:canonical: agentsociety.workflow.prompt.FormatPrompt._extract_variables

```{autodoc2-docstring} agentsociety.workflow.prompt.FormatPrompt._extract_variables
```

````

````{py:method} format(**kwargs) -> str
:canonical: agentsociety.workflow.prompt.FormatPrompt.format

```{autodoc2-docstring} agentsociety.workflow.prompt.FormatPrompt.format
```

````

````{py:method} to_dialog() -> list[dict[str, str]]
:canonical: agentsociety.workflow.prompt.FormatPrompt.to_dialog

```{autodoc2-docstring} agentsociety.workflow.prompt.FormatPrompt.to_dialog
```

````

````{py:method} log() -> None
:canonical: agentsociety.workflow.prompt.FormatPrompt.log

```{autodoc2-docstring} agentsociety.workflow.prompt.FormatPrompt.log
```

````

`````
