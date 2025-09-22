# PyReq

PyReq is a Python-based HTTP request automation tool that allows you to configure and execute HTTP requests using YAML configuration files. It supports environment variables, pre-request scripts, and dynamic header management.

## Features

- YAML-based request configuration
- Environment variable support
- Pre-request script execution
- Dynamic header management
- JSON response formatting
- Environment variable resolution in YAML files
- Support for multiple request configurations in a single YAML file

## Installation

The project uses Poetry for dependency management. To install the project:

```bash
poetry install
```

## Dependencies

- Python >= 3.9
- httpx >= 0.28.1
- pyyaml >= 6.0.2
- typer >= 0.19.1
- python-dotenv >= 1.1.1

## Configuration

### YAML Structure

The YAML configuration file should follow this structure:

```yaml
collection:
  environment:
    headers:
      # Global headers that will be applied to all requests
      Authorization: $_auth_token
    variables:
      # Environment variables
      $_base_url: "https://api.example.com"
      $_auth_token: "Bearer token"
    pre_script:
      # Pre-request scripts
      $_auth_token: "path/to/auth_script.py"
  
  # Request configurations
  get_users:
    method: GET
    url: $_base_url/users
    headers:
      # Request-specific headers (will be merged with environment headers)
      Content-Type: application/json
    query:
      # Query parameters
      page: 1
      limit: 10
    body:
      # Request body (for POST, PUT, etc.)
      key: value
```

### Environment Variables

Environment variables can be used in the YAML file using the `${VARIABLE_NAME}` syntax. These will be automatically resolved from your system's environment variables or a `.env` file.

Example `.env` file:
```
API_URL=https://api.example.com
AUTH_TOKEN=your_auth_token
```

## Usage

To make a request using a configuration from your YAML file:

```python
from pyreq.main import PyReq

# Initialize PyReq with your YAML config file
py_req = PyReq("path/to/your/config.yaml")

# Make a request using a named configuration from your YAML
py_req.request("get_users")
```

Or use the CLI:

```bash
pyreq path/to/your/config.yaml get_users
```

## Pre-request Scripts

Pre-request scripts are Python files that can modify the request configuration before the request is made. They must contain a `pre_request` function that takes a configuration dictionary as an argument and returns a value.

Example pre-request script:
```python
def pre_request(config):
    # Perform authentication or other setup
    # Return value will be assigned to the variable specified in YAML
    return "Bearer generated_token"
```

## Error Handling

The library handles various error cases:
- Invalid YAML configuration
- Missing environment variables
- HTTP request errors
- JSON decode errors

Errors are logged appropriately and can be handled in your application code.

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
