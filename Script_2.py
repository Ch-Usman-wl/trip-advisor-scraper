import requests
import pandas as pd
import time


def get_request(query, url_query):
    cookies = {
    }

    headers = {
    }

    json_data = [
    ]


    retries = 5
    response = None
    print(query)
    print(url_query)
    print('--------------------')
    for attempt in range(retries):
        try:
            response = requests.post('https://www.tripadvisor.com/data/graphql/ids', cookies=cookies, headers=headers, json=json_data)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Attempt {attempt + 1} failed: {e}")
            print('Waiting 8 seconds to retry...')
            time.sleep(8)
    
    if response:
        resp = response.json()
        for item in resp:
            data = item.get('data')
            if data and "SERP_getResultSections" in data:
                serp_data=data['SERP_getResultSections']    
                clusters= serp_data['clusters']
                #print(f'LENGTH OF CLUSTERS: {len(clusters)}')
                #for cluster in clusters:
                cluster = clusters[0]
                sections = cluster.get('sections', [])  # Get 'sections' from each cluster
                results = get_results_from_sections(sections)
                #print(f'Length of RESULTS: {len(results)}')
                if results:
                    if isinstance(results, dict):
                        details = results['details']
                        default_url = details['defaultUrl']
                        print(default_url)
                        url_list.append({
                            'query': query,
                            'url': default_url
                        })
                    elif isinstance(results, list):
                        if 'details' in results[0]:
                            details = results[0]['details']
                            default_url = details.get('defaultUrl')
                            print(default_url)
                            url_list.append({
                                'query': query,
                                'url': default_url
                            })
                        else:
                            print("Key 'details' not found in the list.")
                    else:
                        print("Unexpected data type for 'results'.")
                else:
                    print("No results found.")

 
 
def get_results_from_sections(sections):
    # Recursively search for 'results' within the 'sections'
    for section in sections:
        # Check if 'results' exist directly in the section
        if 'results' in section:
            return section['results']

        # If 'results' is not in this level, check for nested objects
        for key, value in section.items():
            if isinstance(value, list):  # If the value is a list, call recursively
                found = get_results_from_sections(value)
                if found:
                    return found

    return None 
 
 
df = pd.read_csv('output.csv')
csv_file = 'urls1.csv'
url_list = []


for index, row in df.iterrows():
    query = row['query']
    url_query = row['urlquery']

    print(f'Retrieving URLs for query: {query}')
    get_request(query,url_query)
    time.sleep(10)

df2 = pd.DataFrame(url_list)
df2.to_csv(csv_file, index=False)
print(f'Stored URLs in {csv_file}')

