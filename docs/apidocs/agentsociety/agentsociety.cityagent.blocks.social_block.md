# {py:mod}`agentsociety.cityagent.blocks.social_block`

```{py:module} agentsociety.cityagent.blocks.social_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MessagePromptManager <agentsociety.cityagent.blocks.social_block.MessagePromptManager>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessagePromptManager
    :summary:
    ```
* - {py:obj}`SocialNoneBlock <agentsociety.cityagent.blocks.social_block.SocialNoneBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialNoneBlock
    :summary:
    ```
* - {py:obj}`FindPersonBlock <agentsociety.cityagent.blocks.social_block.FindPersonBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.FindPersonBlock
    :summary:
    ```
* - {py:obj}`MessageBlock <agentsociety.cityagent.blocks.social_block.MessageBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessageBlock
    :summary:
    ```
* - {py:obj}`SocialBlock <agentsociety.cityagent.blocks.social_block.SocialBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialBlock
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.social_block.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.social_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.logger
```

````

`````{py:class} MessagePromptManager()
:canonical: agentsociety.cityagent.blocks.social_block.MessagePromptManager

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessagePromptManager
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessagePromptManager.__init__
```

````{py:method} get_prompt(memory, step: typing.Dict[str, typing.Any], target: str, template: str) -> str
:canonical: agentsociety.cityagent.blocks.social_block.MessagePromptManager.get_prompt
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessagePromptManager.get_prompt
```

````

`````

`````{py:class} SocialNoneBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.social_block.SocialNoneBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialNoneBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialNoneBlock.__init__
```

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.social_block.SocialNoneBlock.forward
:async:

````

`````

`````{py:class} FindPersonBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.social_block.FindPersonBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.FindPersonBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.FindPersonBlock.__init__
```

````{py:method} forward(step: typing.Dict[str, typing.Any], context: typing.Optional[typing.Dict] = None) -> typing.Dict[str, typing.Any]
:canonical: agentsociety.cityagent.blocks.social_block.FindPersonBlock.forward
:async:

````

`````

`````{py:class} MessageBlock(agent, llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.social_block.MessageBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessageBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessageBlock.__init__
```

````{py:method} _serialize_message(message: str, propagation_count: int) -> str
:canonical: agentsociety.cityagent.blocks.social_block.MessageBlock._serialize_message

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.MessageBlock._serialize_message
```

````

````{py:method} forward(step: typing.Dict[str, typing.Any], context: typing.Optional[typing.Dict] = None) -> typing.Dict[str, typing.Any]
:canonical: agentsociety.cityagent.blocks.social_block.MessageBlock.forward
:async:

````

`````

`````{py:class} SocialBlock(agent, llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.social_block.SocialBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialBlock.__init__
```

````{py:attribute} find_person_block
:canonical: agentsociety.cityagent.blocks.social_block.SocialBlock.find_person_block
:type: agentsociety.cityagent.blocks.social_block.FindPersonBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialBlock.find_person_block
```

````

````{py:attribute} message_block
:canonical: agentsociety.cityagent.blocks.social_block.SocialBlock.message_block
:type: agentsociety.cityagent.blocks.social_block.MessageBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialBlock.message_block
```

````

````{py:attribute} noneblock
:canonical: agentsociety.cityagent.blocks.social_block.SocialBlock.noneblock
:type: agentsociety.cityagent.blocks.social_block.SocialNoneBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.social_block.SocialBlock.noneblock
```

````

````{py:method} forward(step: typing.Dict[str, typing.Any], context: typing.Optional[typing.Dict] = None) -> typing.Dict[str, typing.Any]
:canonical: agentsociety.cityagent.blocks.social_block.SocialBlock.forward
:async:

````

`````
