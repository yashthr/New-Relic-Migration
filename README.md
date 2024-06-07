# New Relic Dashboard Migration Script

This Python script is designed to migrate dashboards from one New Relic account to another. It queries dashboards from a source account, fetches their detailed configurations, and replicates them in a destination account. The script uses concurrent processing to speed up the migration process.

## Features

- **Fetch Dashboards**: Retrieves all dashboards from the source New Relic account.
- **Fetch Dashboard Details**: Gets detailed configuration of each dashboard.
- **Create Dashboards**: Recreates the dashboards in the destination New Relic account.
- **Concurrent Processing**: Uses `concurrent.futures.ThreadPoolExecutor` to migrate multiple dashboards concurrently for faster execution.

## Prerequisites

- Python 3.x
- `requests` library
- New Relic API keys with appropriate permissions for both source and destination accounts

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yashthr/New-Relic-Migration.git
    ```

2. **Install the required Python libraries**:
    ```sh
    pip install requests
    ```

## Usage

1. **Run the script**:
    ```sh
    python dashboard-migrate.py
    ```

2. **Provide the necessary inputs when prompted**:
    - Source New Relic API key
    - Source New Relic account ID
    - Destination New Relic API key
    - Destination New Relic account ID

## Script Details

### `execute_graphql_query(api_key, query, variables=None)`

Executes a GraphQL query against the New Relic API.

- **Parameters**:
  - `api_key`: API key for authentication.
  - `query`: GraphQL query string.
  - `variables`: Optional variables for the query.

- **Returns**: JSON response data or `None` if there's an error.

### `get_dashboards(api_key, account_id)`

Fetches a list of all dashboards in the specified New Relic account.

- **Parameters**:
  - `api_key`: API key for the source New Relic account.
  - `account_id`: Account ID of the source New Relic account.

- **Returns**: List of dashboard entities.

### `get_dashboard_details(api_key, guid)`

Fetches detailed configuration for a specific dashboard.

- **Parameters**:
  - `api_key`: API key for the source New Relic account.
  - `guid`: GUID of the dashboard.

- **Returns**: Detailed dashboard configuration or `None` if there's an error.

### `create_dashboard(api_key, account_id, dashboard)`

Creates a new dashboard in the specified New Relic account.

- **Parameters**:
  - `api_key`: API key for the destination New Relic account.
  - `account_id`: Account ID of the destination New Relic account.
  - `dashboard`: Dashboard configuration to be created.

- **Returns**: `None`. Logs success or error messages.

### `migrate_dashboard(api_key, destination_api_key, destination_account_id, dashboard)`

Migrates a single dashboard from the source to the destination account.

- **Parameters**:
  - `api_key`: API key for the source New Relic account.
  - `destination_api_key`: API key for the destination New Relic account.
  - `destination_account_id`: Account ID of the destination New Relic account.
  - `dashboard`: Dashboard entity to be migrated.

- **Returns**: `None`. Logs success or error messages.

### `main()`

Main function to handle the entire migration process.

- **Prompts for user inputs**: API keys and account IDs.
- **Fetches dashboards** from the source account.
- **Migrates dashboards** to the destination account using concurrent processing.

## Logging

The script uses the `logging` module to provide detailed information about the migration process, including:
- Info messages for the start and completion of fetching and migration tasks.
- Error messages for any issues encountered during API requests or dashboard creation.

## Example Output

```
Enter source New Relic API key:
Enter source account ID: 123456
Enter destination New Relic API key:
Enter destination account ID: 987654
2024-06-04 17:10:14,992 - INFO - Fetching dashboards from source account...
2024-06-04 17:10:15,378 - INFO - Migrating dashboard: Alerts (GUID: XyzD1bbwex)
2024-06-04 17:10:16,123 - INFO - Dashboard created: Alerts
...
```
