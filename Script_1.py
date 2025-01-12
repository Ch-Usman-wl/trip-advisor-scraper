import pandas as pd

# Read the CSV file
df = pd.read_csv('hotels_info.csv')

# Create a new DataFrame to store the results
result = pd.DataFrame()

# Generate 'query' and 'urlquery'
result['query'] = df['name'].str.replace(',', '').str.cat(df['city'].str.replace(',', ''), sep=' ')
result['urlquery'] = result['query'].str.replace(' ', '+').str.replace(',', '%2C')

# Save the result to a new CSV file
result.to_csv('output.csv', index=False)
