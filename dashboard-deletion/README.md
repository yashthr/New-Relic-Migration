# New Relic Dashboard Deletion Script

This Python script is designed to delete dashboards from a New Relic account. It can delete all dashboards in an account or a specific dashboard by name. The script uses concurrent processing to speed up the deletion process.

## Features

- **Fetch Dashboards**: Retrieves all dashboards from the specified New Relic account.
- **Delete Dashboards**: Deletes dashboards from the specified New Relic account.
- **Concurrent Processing**: Uses `concurrent.futures.ThreadPoolExecutor` to delete multiple dashboards concurrently for faster execution.

## Prerequisites

- Python 3.x
- `requests` library
- New Relic API key with appropriate permissions

## Installation

Clone the repository:

```sh
git clone https://github.com/yourusername/newrelic-dashboard-deletion.git
cd dashboard-deletion
```

Install the required Python libraries:

```sh
pip install requests
```

## Usage

Run the script:

```sh
python dashboard-delete.py
```

Provide the necessary inputs when prompted:

- New Relic API key
- New Relic account ID
- Option to delete all dashboards or specify a dashboard name

## Script Details

### `make_graphql_request(api_key, query)`

Executes a GraphQL query against the New Relic API.

- **Parameters**:
  - `api_key`: API key for authentication.
  - `query`: GraphQL query string.
- **Returns**: JSON response data or raises an error if the request fails.

### `fetch_dashboards(api_key, account_id)`

Fetches a list of all dashboards in the specified New Relic account.

- **Parameters**:
  - `api_key`: API key for the New Relic account.
  - `account_id`: Account ID of the New Relic account.
- **Returns**: List of dashboard entities.

### `delete_dashboard(api_key, guid)`

Deletes a specific dashboard.

- **Parameters**:
  - `api_key`: API key for the New Relic account.
  - `guid`: GUID of the dashboard.
- **Returns**: Status of the deletion.

### `delete_dashboards_in_parallel(api_key, dashboards)`

Deletes multiple dashboards in parallel.

- **Parameters**:
  - `api_key`: API key for the New Relic account.
  - `dashboards`: List of dashboard entities to be deleted.
- **Returns**: None. Logs success or error messages.

### `main()`

Main function to handle the entire deletion process.

- Prompts for user inputs: API key and account ID.
- Fetches dashboards from the account.
- Deletes dashboards based on user input (all or specific dashboard) using concurrent processing.

## Example Output

```sh
Enter New Relic account ID: 123456
Enter New Relic API key:
Do you want to delete all dashboards? (yes/no): yes
Deleted dashboard 'Alerts' with GUID 'MxaseFwddi' - Status: SUCCESS
...
```
