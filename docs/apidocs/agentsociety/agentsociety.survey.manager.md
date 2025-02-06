# {py:mod}`agentsociety.survey.manager`

```{py:module} agentsociety.survey.manager
```

```{autodoc2-docstring} agentsociety.survey.manager
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SurveyManager <agentsociety.survey.manager.SurveyManager>`
  - ```{autodoc2-docstring} agentsociety.survey.manager.SurveyManager
    :summary:
    ```
````

### API

`````{py:class} SurveyManager()
:canonical: agentsociety.survey.manager.SurveyManager

```{autodoc2-docstring} agentsociety.survey.manager.SurveyManager
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.survey.manager.SurveyManager.__init__
```

````{py:method} create_survey(title: str, description: str, pages: list[dict]) -> agentsociety.survey.models.Survey
:canonical: agentsociety.survey.manager.SurveyManager.create_survey

```{autodoc2-docstring} agentsociety.survey.manager.SurveyManager.create_survey
```

````

````{py:method} get_survey(survey_id: str) -> typing.Optional[agentsociety.survey.models.Survey]
:canonical: agentsociety.survey.manager.SurveyManager.get_survey

```{autodoc2-docstring} agentsociety.survey.manager.SurveyManager.get_survey
```

````

````{py:method} get_all_surveys() -> list[agentsociety.survey.models.Survey]
:canonical: agentsociety.survey.manager.SurveyManager.get_all_surveys

```{autodoc2-docstring} agentsociety.survey.manager.SurveyManager.get_all_surveys
```

````

`````
