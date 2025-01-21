# {py:mod}`pycityagent.survey.manager`

```{py:module} pycityagent.survey.manager
```

```{autodoc2-docstring} pycityagent.survey.manager
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SurveyManager <pycityagent.survey.manager.SurveyManager>`
  - ```{autodoc2-docstring} pycityagent.survey.manager.SurveyManager
    :summary:
    ```
````

### API

`````{py:class} SurveyManager()
:canonical: pycityagent.survey.manager.SurveyManager

```{autodoc2-docstring} pycityagent.survey.manager.SurveyManager
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.survey.manager.SurveyManager.__init__
```

````{py:method} create_survey(title: str, description: str, pages: list[dict]) -> pycityagent.survey.models.Survey
:canonical: pycityagent.survey.manager.SurveyManager.create_survey

```{autodoc2-docstring} pycityagent.survey.manager.SurveyManager.create_survey
```

````

````{py:method} get_survey(survey_id: str) -> typing.Optional[pycityagent.survey.models.Survey]
:canonical: pycityagent.survey.manager.SurveyManager.get_survey

```{autodoc2-docstring} pycityagent.survey.manager.SurveyManager.get_survey
```

````

````{py:method} get_all_surveys() -> list[pycityagent.survey.models.Survey]
:canonical: pycityagent.survey.manager.SurveyManager.get_all_surveys

```{autodoc2-docstring} pycityagent.survey.manager.SurveyManager.get_all_surveys
```

````

`````
