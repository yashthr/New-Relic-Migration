import requests
import json
import getpass
import logging
import concurrent.futures

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_URL = 'https://api.newrelic.com/graphql'

def execute_graphql_query(api_key, query, variables=None):
    headers = {
        'API-Key': api_key,
        'Content-Type': 'application/json',
    }
    payload = {'query': query}
    if variables:
        payload['variables'] = variables

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'errors' in data:
            logging.error(f"GraphQL errors: {data['errors']}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request failed: {e}")
        return None

def get_dashboards(api_key, account_id):
    initial_query = '''
    {
      actor {
        entitySearch(
          queryBuilder: {type: DASHBOARD, tags: {key: "accountId", value: "%s"}}
        ) {
          results {
            entities {
              ... on DashboardEntityOutline {
                guid
                name
                accountId
              }
            }
            nextCursor
          }
        }
      }
    }''' % account_id

    paginated_query = '''
    {
      actor {
        entitySearch(
          queryBuilder: {type: DASHBOARD, tags: {key: "accountId", value: "%s"}}
        ) {
          results(cursor: "%s") {
            entities {
              ... on DashboardEntityOutline {
                guid
                name
                accountId
              }
            }
            nextCursor
          }
        }
      }
    }'''

    dashboards = []
    next_cursor = None
    while True:
        if next_cursor:
            query = paginated_query % (account_id, next_cursor)
        else:
            query = initial_query

        data = execute_graphql_query(api_key, query)
        if not data:
            break
        
        results = data['data']['actor']['entitySearch']['results']
        dashboards.extend(results['entities'])
        next_cursor = results.get('nextCursor')
        if not next_cursor:
            break
    
    return dashboards

def get_dashboard_details(api_key, guid):
    query = '''
    {
      actor {
        entity(guid: "%s") {
          ... on DashboardEntity {
            name
            permissions
            pages {
              name
              widgets {
                visualization { id }
                title
                layout { row width height column }
                rawConfiguration
              }
            }
          }
        }
      }
    }''' % guid

    data = execute_graphql_query(api_key, query)
    if data:
        return data['data']['actor']['entity']
    return None

def create_dashboard(api_key, account_id, dashboard):
    mutation = '''
    mutation create($dashboard: DashboardInput!) {
      dashboardCreate(accountId: %s, dashboard: $dashboard) {
        entityResult {
          guid
          name
        }
        errors {
          description
        }
      }
    }''' % account_id

    variables = {
        "dashboard": {
            "name": dashboard['name'],
            "pages": dashboard['pages'],
            "permissions": dashboard['permissions']
        }
    }

    data = execute_graphql_query(api_key, mutation, variables)
    if data:
        if data['data']['dashboardCreate']['errors']:
            logging.error(f"Errors: {data['data']['dashboardCreate']['errors']}")
        else:
            logging.info(f"Dashboard created: {data['data']['dashboardCreate']['entityResult']['name']}")

def migrate_dashboard(api_key, destination_api_key, destination_account_id, dashboard):
    logging.info(f"Migrating dashboard: {dashboard['name']} (GUID: {dashboard['guid']})")
    details = get_dashboard_details(api_key, dashboard['guid'])
    
    if not details:
        logging.error(f"Skipping dashboard {dashboard['name']} due to error in fetching details.")
        return
    
    create_dashboard(destination_api_key, destination_account_id, details)

def main():
    source_api_key = getpass.getpass(prompt='Enter source New Relic API key: ')
    source_account_id = input('Enter source account ID: ')
    destination_api_key = getpass.getpass(prompt='Enter destination New Relic API key: ')
    destination_account_id = input('Enter destination account ID: ')

    logging.info("Fetching dashboards from source account...")
    dashboards = get_dashboards(source_api_key, source_account_id)
    
    if not dashboards:
        logging.error("No dashboards found or error occurred while fetching dashboards.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(migrate_dashboard, source_api_key, destination_api_key, destination_account_id, dashboard)
            for dashboard in dashboards
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error during migration: {e}")

if __name__ == "__main__":
    main()
