import re
import pandas as pd

# Initialize an empty list to store the extracted data
extracted_data = []

# Define the pattern to extract 'g' and 'd' numbers
pattern = r"g(\d+)-d(\d+)"

# Read the CSV file containing 'query' and 'url' columns
df_urls = pd.read_csv('urls1.csv')  # Adjust the file name as needed

# Iterate over each row in the DataFrame
for index, row in df_urls.iterrows():
    url = row['url']  # Assuming the column with URLs is named 'url'
    query = row['query']  # If you want to store the query alongside
    
    match = re.search(pattern, url)  # Search for the pattern in the URL
    if match:
        location_id = match.group(1)
        hotel_id = match.group(2)
        extracted_data.append({
            'query': query,  # Include the query if needed
            'hotel_review_urls': url, 
            'location_id': location_id, 
            'hotel_id': hotel_id
        })

# Create a DataFrame from the extracted data
df_extracted = pd.DataFrame(extracted_data)

# Write the extracted data to a new CSV file
df_extracted.to_csv('extracted_urls2.csv', index=False)

print("Extraction complete! Data saved to 'extracted_urls.csv'")

