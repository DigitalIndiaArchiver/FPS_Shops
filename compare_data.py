import pandas as pd
import os

# Load previous and current data
if os.path.exists('previous_ConsolidatedShops.csv'):
    previous_data = pd.read_csv('previous_ConsolidatedShops.csv')
else:
    previous_data = pd.DataFrame()

current_data = pd.read_csv('ConsolidatedShops.csv')

# Merge dataframes to find differences
merged_data = previous_data.merge(current_data, on='fpsCode', how='outer', indicator=True, suffixes=('_old', '_new'))

# Added shops
added_shops = merged_data[merged_data['_merge'] == 'right_only']

# Removed shops
removed_shops = merged_data[merged_data['_merge'] == 'left_only']

# Updated shops
updated_shops = merged_data[merged_data['_merge'] == 'both']
updated_shops = updated_shops.loc[~(updated_shops.filter(like='_old').values == updated_shops.filter(like='_new').values).all(axis=1)]

# Output changes
changes = f"""
Added Shops: {len(added_shops)}
Removed Shops: {len(removed_shops)}
Updated Shops: {len(updated_shops)}
"""

print(changes)

# Save changes to GitHub environment variable
with open(os.environ['GITHUB_ENV'], 'a') as env_file:
    env_file.write(f"changes<<EOF\n{changes}\nEOF\n")

# Save the new data as ConsolidatedShops.csv
current_data.to_csv('ConsolidatedShops.csv', index=False)