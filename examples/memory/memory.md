# `Memory` Documentation

The `Memory` class is designed to manage different types of memory within the system, specifically state memory, profile memory, and dynamically configured memory. The `Memory` class provides snapshot functionality, allowing snapshots to be recorded when updating memory. Timestamps of changes can also be optionally recorded with `activate_timestamp=True` when initializing. See `examples/memory/read_and_write.py` for using examples.

## Table of Contents

- [`Memory` Documentation](#memory-documentation)
  - [Table of Contents](#table-of-contents)
  - [Attributes](#attributes)
  - [Initialization](#initialization)
    - [`__init__`](#__init__)
  - [Methods](#methods)
    - [`get`](#get)
    - [`get_top_k`](#get_top_k)
    - [`update`](#update)
    - [`update_batch`](#update_batch)
    - [`add_watcher`](#add_watcher)
    - [`export`](#export)
    - [`load`](#load)

## Attributes

- **_state**: An instance of `StateMemory` used to store state-related data.
- **_profile**: An instance of `ProfileMemory` used to store profile-related data.
- **_dynamic**: An instance of `DynamicMemory` used to store dynamically configured data.

## Initialization

### `__init__`

Initializes the `Memory` object with optional configurations for dynamic memory, base attributes, and motion attributes.

**Parameters:**

- **config**: `Optional[Dict[Any, Any]]` - A configuration dictionary for dynamic memory. Each key-value pair represents a field name and its type or a callable to generate a default value. If a key overlaps with predefined attributes, a warning is logged, and the key is ignored.
- **profile**: `Optional[Dict[Any, Any]]` - A dictionary of base attributes. Keys not in `PROFILE_ATTRIBUTES` will log a warning.
- **base**: `Optional[Dict[Any, Any]]` - A dictionary of base attributes from the City Simulator. Keys not in `STATE_ATTRIBUTES` will log a warning.
- **motion**: `Optional[Dict[Any, Any]]` - A dictionary of motion attributes from the City Simulator. Keys not in `STATE_ATTRIBUTES` will log a warning.
- **activate_timestamp**: `bool` - Whether to activate timestamp storage in memory units.

## Methods

### `get`

Retrieves a value from memory based on the given key and access mode.

**Parameters:**

- **key**: `Any` - The key of the item to retrieve.
- **mode**: `Union[Literal["read only"], Literal["read and write"]]` - Access mode for the item. Defaults to `"read only"`.

**Returns:**

- **Any**: The value associated with the key.

**Raises:**

- **ValueError**: If an invalid mode is provided.
- **KeyError**: If the key is not found in any of the memory sections.

### `get_top_k`

Retrieves the top-k items from the memory based on the given key and metric.

**Parameters:**

- **key**: `Any` - The key of the item to retrieve.
- **metric**: `Callable[[Any], Any]` - A callable function that defines the metric for ranking the items.
- **top_k**: `Optional[int]` - The number of top items to retrieve. Defaults to `None` (all items).
- **mode**: `Union[Literal["read only"], Literal["read and write"]]` - Access mode for the item. Defaults to `"read only"`.
- **preserve_order**: `bool` - Whether preserve original order in output values.

**Returns:**

- **Any**: The top-k items based on the specified metric.

**Raises:**

- **ValueError**: If an invalid mode is provided.
- **KeyError**: If the key is not found in any of the memory sections.

### `update`

Updates an existing value in the memory with a new value based on the given key and update mode.

**Parameters:**

- **key**: `Any` - The key of the item to update.
- **value**: `Any` - The new value to set.
- **mode**: `Union[Literal["replace"], Literal["merge"]]` - Update mode. Defaults to `"replace"`.
- **store_snapshot**: `bool` - Whether to store a snapshot of the memory after the update.
- **protect_llm_read_only_fields**: `bool` - Whether to protect LLM read-only fields from being updated.

**Raises:**

- **ValueError**: If an invalid update mode is provided.
- **KeyError**: If the key is not found in any of the memory sections.

### `update_batch`

Updates multiple values in the memory at once.

**Parameters:**

- **content**: `Union[Dict, Sequence[Tuple[Any, Any]]]` - A dictionary or sequence of tuples containing the keys and values to update.
- **mode**: `Union[Literal["replace"], Literal["merge"]]` - Update mode. Defaults to `"replace"`.
- **store_snapshot**: `bool` - Whether to store a snapshot of the memory after the update.
- **protect_llm_read_only_fields**: `bool` - Whether to protect non-self-defined fields from being updated.

**Raises:**

- **TypeError**: If the content type is neither a dictionary nor a sequence of tuples.

### `add_watcher`

Adds a callback function to be invoked when the value associated with the specified key in memory is updated.

**Parameters:**

- **key**: `str` - The key for which the watcher is being registered.
- **callback**: `Callable` - A callable function that will be executed whenever the value associated with the specified key is updated.

### `export`

Exports the current state of all memory sections.

**Returns:**

- **Tuple[Sequence[Dict], Sequence[Dict], Sequence[Dict]]**: A tuple containing the exported data of profile, state, and dynamic memory sections.

### `load`

Imports the snapshot memories of all sections.

**Parameters:**

- **snapshots**: `Tuple[Sequence[Dict], Sequence[Dict], Sequence[Dict]]` - The exported snapshots.
- **reset_memory**: `bool` - Whether to reset previous memory.
