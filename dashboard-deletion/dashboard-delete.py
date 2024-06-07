import requests
import json
import getpass
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to make a GraphQL request
def make_graphql_request(api_key, query):
    headers = {
        'Content-Type': 'application/json',
        'API-Key': api_key
    }
    response = requests.post('https://api.newrelic.com/graphql', headers=headers, data=json.dumps({'query': query}))
    response.raise_for_status()
    return response.json()

# Function to fetch dashboards
def fetch_dashboards(api_key, account_id):
    query = '''
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
    }
    ''' % account_id
    
    dashboards = []
    next_cursor = None

    while True:
        if next_cursor:
            query = '''
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
            }
            ''' % (account_id, next_cursor)

        result = make_graphql_request(api_key, query)
        dashboards.extend(result['data']['actor']['entitySearch']['results']['entities'])
        next_cursor = result['data']['actor']['entitySearch']['results']['nextCursor']

        if not next_cursor:
            break

    return dashboards

# Function to delete a dashboard
def delete_dashboard(api_key, guid):
    mutation = '''
    mutation {
      dashboardDelete(guid: "%s") {
        status
      }
    }
    ''' % guid
    
    result = make_graphql_request(api_key, mutation)
    return result['data']['dashboardDelete']['status']

# Function to delete multiple dashboards in parallel
def delete_dashboards_in_parallel(api_key, dashboards):
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_dashboard = {executor.submit(delete_dashboard, api_key, dashboard['guid']): dashboard for dashboard in dashboards}
        for future in as_completed(future_to_dashboard):
            dashboard = future_to_dashboard[future]
            try:
                status = future.result()
                print(f"Deleted dashboard '{dashboard['name']}' with GUID '{dashboard['guid']}' - Status: {status}")
            except Exception as exc:
                print(f"Dashboard '{dashboard['name']}' generated an exception: {exc}")

def main():
    account_id = input("Enter New Relic account ID: ")
    api_key = getpass.getpass("Enter New Relic API key: ")
    delete_all = input("Do you want to delete all dashboards? (yes/no): ").strip().lower()

    dashboards = fetch_dashboards(api_key, account_id)
    
    if delete_all == 'yes':
        delete_dashboards_in_parallel(api_key, dashboards)
    else:
        dashboard_name = input("Enter the name of the dashboard to delete: ").strip()
        encoded_dashboard_name = urllib.parse.quote(dashboard_name)
        dashboard = next((d for d in dashboards if urllib.parse.quote(d['name']) == encoded_dashboard_name), None)
        if dashboard:
            status = delete_dashboard(api_key, dashboard['guid'])
            print(f"Deleted dashboard '{dashboard_name}' with GUID '{dashboard['guid']}' - Status: {status}")
        else:
            print(f"Dashboard '{dashboard_name}' not found.")

if __name__ == "__main__":
    main()
