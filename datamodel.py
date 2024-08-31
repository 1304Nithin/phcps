import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
product_df = pd.read_csv('productdataset.csv')

# Copy first 101 rows to a new file
product_df.head(100).to_csv('data.csv', index=False)

# Load the new dataset
data = pd.read_csv('data.csv')

# Check for null values
print("Initial Null Values:")
print(data.isnull().sum())

# Drop the specified columns
data = data.drop(columns=['Offers.Listings.0.SavingBasis.Percentage'])
data = data.drop(columns=['ASIN'])

# Fill missing values in the specified column with 'naan'
data['BrowseNodeInfo.BrowseNodes.0.SalesRank'] = data['BrowseNodeInfo.BrowseNodes.0.SalesRank'].fillna('naan')

# Save the cleaned data to a new file
data.to_csv('products_cleaned.csv', index=False)

# Print the first few rows to verify changes
print("\nData After Initial Cleaning:")
print(data.head())
print(data.isnull().sum())

# Reload cleaned data
data = pd.read_csv('products_cleaned.csv')

# Convert column to numeric, setting errors='coerce' will convert 'naan' to NaN
data['BrowseNodeInfo.BrowseNodes.0.SalesRank'] = pd.to_numeric(data['BrowseNodeInfo.BrowseNodes.0.SalesRank'], errors='coerce')

# Fill missing values with the mean of the column
mean_value = data['BrowseNodeInfo.BrowseNodes.0.SalesRank'].mean()
data['BrowseNodeInfo.BrowseNodes.0.SalesRank'].fillna(mean_value, inplace=True)

# Save the updated data
data.to_csv('products_filled.csv', index=False)

# Print the first few rows to verify changes
print("\nData After Filling Missing Values:")
print(data.head())
print(data.isnull().sum())

# Define a score for the best product
# Assuming lower sales rank and price are better
data['Offers.Listings.0.Price.Amount'] = pd.to_numeric(data['Offers.Listings.0.Price.Amount'], errors='coerce')

# Drop rows where price is NaN
data = data.dropna(subset=['Offers.Listings.0.Price.Amount'])

# Sort by SalesRank (ascending for better rank) and Price (ascending for lower price)
data_sorted = data.sort_values(by=['BrowseNodeInfo.BrowseNodes.0.SalesRank', 'Offers.Listings.0.Price.Amount'])

# Save the sorted results to a new file
data_sorted.to_csv('products.csv', index=False)

# Print the first few rows of the sorted data
print("\nBest Products Based on Sales Rank and Price:")
print(data_sorted.head())

# Plot graph for Sales Rank and Price Comparisons
plt.figure(figsize=(20, 12))
plt.scatter(data_sorted['BrowseNodeInfo.BrowseNodes.0.SalesRank'], data_sorted['Offers.Listings.0.Price.Amount'], alpha=0.5)
plt.title('Sales Rank vs. Price')
plt.xlabel('Sales Rank')
plt.ylabel('Price Amount')
plt.grid(True)
plt.show()

# Highlight top N products
N = 10  # Define how many top products to highlight
top_products = data_sorted.head(N)

plt.figure(figsize=(10, 6))
plt.scatter(data_sorted['BrowseNodeInfo.BrowseNodes.0.SalesRank'], data_sorted['Offers.Listings.0.Price.Amount'], alpha=0.5, label='All Products')
plt.scatter(top_products['BrowseNodeInfo.BrowseNodes.0.SalesRank'], top_products['Offers.Listings.0.Price.Amount'], color='red', alpha=0.7, label='Top Products')
plt.title('Sales Rank vs. Price with Top Products Highlighted')
plt.xlabel('Sales Rank')
plt.ylabel('Price Amount')
plt.legend()
plt.grid(True)
plt.show()
