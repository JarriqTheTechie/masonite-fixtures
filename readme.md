# Masonite Fixtures

The `masonite-fixtures` package provides utilities for managing fixture data python applications. It offers a convenient way to populate database tables with predefined data.

## Installation

You can install `masonite-fixtures` via pip:

```bash
pip install masonite-fixtures
```

## Features

- Initialize fixture data for database tables effortlessly.
- Automatically create database tables based on the schema of the fixture model.
- Populate database tables with data defined in the fixture model using either `get_rows` method or `rows` property.
- Enable query logging for debugging and monitoring database interactions.

## Usage

To use the `masonite-fixtures` package, follow these steps:

1. Import your model class that implements the `FixtureMixin`.
2. Mix the `FixtureMixin` into your model class.
####
That's it. 
3. Optionally, set the `__log_queries__` attribute to `True` to enable query logging.

Example:

```python
from typing import Any
from masoniteorm.models import Model
from masonite_fixtures import FixtureMixin


# Example using get_rows method:
class User(Model, FixtureMixin):
    def get_rows(self) -> list[dict[str, Any]]:
        return [
            {"name": "John", "age": 30},
            {"name": "Alice", "age": 25},
            # Add more rows as needed
        ]
    
# Example using rows attribute:
class User(Model, FixtureMixin):
    rows: list[dict[str, Any]] = [
            {"name": "John", "age": 30},
            {"name": "Alice", "age": 25},
            # Add more rows as needed
        ]    

```
#### Thats it. You can now use the model as you would any other masoniteorm model. 

## Important
Fixture data is semi-permanent. Every time you modify the fixture model file the data in its database is deleted. If you never modify the model file then the data remains in place. Which means you can even store additional data in fixtures. Personally I would avoid doing this. 


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

This README now provides a more thorough description of the features offered by the `masonite-fixtures` package and includes examples demonstrating the usage of both `get_rows` and `rows`.