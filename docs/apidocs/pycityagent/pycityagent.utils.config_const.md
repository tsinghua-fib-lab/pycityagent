# {py:mod}`pycityagent.utils.config_const`

```{py:module} pycityagent.utils.config_const
```

```{autodoc2-docstring} pycityagent.utils.config_const
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WorkflowType <pycityagent.utils.config_const.WorkflowType>`
  -
* - {py:obj}`LLMRequestType <pycityagent.utils.config_const.LLMRequestType>`
  -
````

### API

`````{py:class} WorkflowType()
:canonical: pycityagent.utils.config_const.WorkflowType

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

````{py:attribute} STEP
:canonical: pycityagent.utils.config_const.WorkflowType.STEP
:value: >
   'step'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.STEP
```

````

````{py:attribute} RUN
:canonical: pycityagent.utils.config_const.WorkflowType.RUN
:value: >
   'run'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.RUN
```

````

````{py:attribute} INTERVIEW
:canonical: pycityagent.utils.config_const.WorkflowType.INTERVIEW
:value: >
   'interview'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.INTERVIEW
```

````

````{py:attribute} SURVEY
:canonical: pycityagent.utils.config_const.WorkflowType.SURVEY
:value: >
   'survey'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.SURVEY
```

````

````{py:attribute} INTERVENE
:canonical: pycityagent.utils.config_const.WorkflowType.INTERVENE
:value: >
   'intervene'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.INTERVENE
```

````

````{py:attribute} PAUSE
:canonical: pycityagent.utils.config_const.WorkflowType.PAUSE
:value: >
   'pause'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.PAUSE
```

````

````{py:attribute} RESUME
:canonical: pycityagent.utils.config_const.WorkflowType.RESUME
:value: >
   'resume'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.RESUME
```

````

````{py:attribute} FUNCTION
:canonical: pycityagent.utils.config_const.WorkflowType.FUNCTION
:value: >
   'function'

```{autodoc2-docstring} pycityagent.utils.config_const.WorkflowType.FUNCTION
```

````

`````

`````{py:class} LLMRequestType()
:canonical: pycityagent.utils.config_const.LLMRequestType

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

````{py:attribute} OpenAI
:canonical: pycityagent.utils.config_const.LLMRequestType.OpenAI
:value: >
   'openai'

```{autodoc2-docstring} pycityagent.utils.config_const.LLMRequestType.OpenAI
```

````

````{py:attribute} DeepSeek
:canonical: pycityagent.utils.config_const.LLMRequestType.DeepSeek
:value: >
   'deepseek'

```{autodoc2-docstring} pycityagent.utils.config_const.LLMRequestType.DeepSeek
```

````

````{py:attribute} Qwen
:canonical: pycityagent.utils.config_const.LLMRequestType.Qwen
:value: >
   'qwen'

```{autodoc2-docstring} pycityagent.utils.config_const.LLMRequestType.Qwen
```

````

````{py:attribute} ZhipuAI
:canonical: pycityagent.utils.config_const.LLMRequestType.ZhipuAI
:value: >
   'zhipuai'

```{autodoc2-docstring} pycityagent.utils.config_const.LLMRequestType.ZhipuAI
```

````

````{py:attribute} SiliconFlow
:canonical: pycityagent.utils.config_const.LLMRequestType.SiliconFlow
:value: >
   'siliconflow'

```{autodoc2-docstring} pycityagent.utils.config_const.LLMRequestType.SiliconFlow
```

````

`````
