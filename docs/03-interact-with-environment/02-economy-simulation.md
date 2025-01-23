# Economy Simulation

The Economy Simulation serves as a financial settlement system in the city simulation environment.

## Constructor
```python

class EconomyClient:
    def __init__(self, server_address: str, secure: bool = False):
    """
    Parameters:
        server_address: The address of the Economy server to connect to.
        secure: Whether to use a secure connection. Defaults to `False`.
    """
```

## Key Methods

### Agent and Organization Management Methods
```python

    async def add_agents(self, configs: Union[list[dict], dict]):
        """
        Add one or more agents to the economy system.
        """

    async def add_orgs(self, configs: Union[list[dict], dict]):
        """
        Add one or more organizations to the economy system.
        """

    async def get_org_entity_ids(self, org_type: economyv2.OrgType) -> list[int]:
        """
        Get the IDs of all organizations of a specific type.
        """

    async def remove_agents(self, agent_ids: Union[int, list[int]]):
        """
        Remove one or more agents from the system.
        """

    async def remove_orgs(self, org_ids: Union[int, list[int]]):
        """
        Remove one or more organizations from the system.
        """
```

### Attribute Management Methods
```python

    async def get(
            self,
            id: int,
            key: str,
        ) -> Any:
        """
        Get specific value
        """

    async def update(
            self,
            id: int,
            key: str,
            value: Any,
            mode: Union[Literal["replace"], Literal["merge"]] = "replace",
        ) -> Any:
        """
        Update key-value pair
        """
```

### Calculation Methods
```python
    async def calculate_taxes_due(
            self,
            org_id: int,
            agent_ids: list[int],
            incomes: list[float],
            enable_redistribution: bool,
        ):
        """
        Calculate the taxes due for agents based on their incomes.
        """
    
    async def calculate_consumption(
            self, org_id: int, agent_ids: list[int], demands: list[int]
        ):
        """
        Calculate consumption for agents based on their demands.
        """

    async def calculate_interest(self, org_id: int, agent_ids: list[int]):
        """
        Calculate interest for agents based on their accounts.
        """
```

### System Status Management
```python

    async def save(self, file_path: str) -> tuple[list[int], list[int]]:
        """
        Save the current state of all economy entities to a specified file.
        """

    async def load(self, file_path: str):
        """
        Load the state of economy entities from a specified file.
        """
```
