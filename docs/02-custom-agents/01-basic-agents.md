# Basic Agent Classes

## InstitutionAgent Class

Represents an institutional entity in the city simulation environment.
Inherits from the base Agent class.

### Properties
```python
class InstitutionAgent:
    agent_id: str          # Unique identifier
    type: AgentType       # Always AgentType.Institution
    simulator: Simulator   # Reference to simulation environment
    economy_client: EconomyClient  # Economy system interface
    memory: Memory        # State storage
    llm_client: LLM      # LLM interface
    mlflow_client: MlflowClient  # Metrics tracking
```

### Constructor
```python
def __init__(
    self,
    name: str,
    llm_client: Optional[LLM] = None,
    simulator: Optional[Simulator] = None,
    memory: Optional[Memory] = None,
    economy_client: Optional[EconomyClient] = None,
    messager: Optional[Messager] = None,
    message_interceptor: Optional[MessageInterceptor] = None,
    avro_file: Optional[dict] = None
) -> None:
    """
    Parameters:
        name: Institution name
        llm_client: Language model client
        simulator: Simulation environment
        memory: State storage
        economy_client: Economy system interface
        messager: Communication service with MQTT
        message_interceptor: Message interceptor, forbids the message transforming if needed.
        avro_file: Avro storage config
    """
```

### Key Methods

#### Binding Methods
```python
async def bind_to_simulator(self):
    """Connects institution to simulation environment"""

async def _bind_to_economy(self):
    """Registers institution in economic system"""
```

#### Message Handling
```python
async def handle_gather_message(self, payload: dict):
    """
    Processes incoming gather requests
    payload: {
        "target": str,  # Requested attribute
        "from": str    # Sender ID
    }
    """
```

## CitizenAgent Class

Represents individual citizens with daily activities and behaviors.

### Properties
```python

class CitizenAgent(Agent):
    agent_id: str          # Unique identifier
    type: AgentType       # Always AgentType.Institution
    simulator: Simulator   # Reference to simulation environment
    economy_client: EconomyClient  # Economy system interface
    memory: Memory        # State storage
    llm_client: LLM      # LLM interface
    mlflow_client: MlflowClient  # Metrics tracking
```

### Constructor

```python
def __init__(
    name: str,                                    # Agent name
    llm_client: Optional[LLM] = None,            # Language model client
    simulator: Optional[Simulator] = None,        # City simulator instance
    memory: Optional[Memory] = None,             # Agent memory system
    economy_client: Optional[EconomyClient] = None, # Economic system client
    messager: Optional[Messager] = None,         # Communication system
    message_interceptor: Optional[MessageInterceptor] = None,  # Message handler
    avro_file: Optional[dict] = None,            # Data logging config
)
```

### Key Methods

#### Binding Methods
```python
async def bind_to_simulator(self):
    """
    Binds agent to both traffic and economy simulators
    Raises:
        RuntimeError: If simulator is not configured
    """

async def _bind_to_simulator(self):
    """
    Binds to traffic simulator
    - Creates person entity
    - Sets agent ID
    - Updates status
    """

async def _bind_to_economy(self):
    """
    Binds to economy simulator
    - Registers agent in economy system
    - Sets initial currency
    """
```

#### Message Handling
```python
async def handle_gather_message(self, payload: dict):
    """
    Processes information gathering requests
    Args:
        payload: {
            "target": str,  # Requested attribute
            "from": str     # Requester ID
        }
    """
```
