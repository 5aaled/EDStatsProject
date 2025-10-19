

import numpy as np
import pandas as pd  ,pycountry as pc , matplotlib.pyplot as plt,seaborn as sns
from future.backports.datetime import datetime

EDStatsData=pd.read_csv('Source/EdStatsData.csv')
EDStatsFootNote =  pd.read_csv('Source/EdStatsFootNote.csv')
EDStatsCountrySeries = pd.read_csv('Source/EdStatsCountry-Series.csv')
EDStatsCountry = pd.read_csv('Source/EdStatsCountry.csv')
EDStatsSeries= pd.read_csv('Source/EdStatsSeries.csv')
# Explore the data
############ 1 : EDStats Country##########
Country_shapes = EDStatsCountry.shape
N_of_null_values =EDStatsCountry.isnull().sum()
Country_info =EDStatsCountry.info
Country_heads = EDStatsCountry.head()
Country_descriptions = EDStatsCountry.describe()
Country_N_of_unique = EDStatsCountry.nunique().sort_values(ascending=False).reset_index(name='nunique')
Country_keys= Country_N_of_unique[Country_N_of_unique['nunique'] == Country_shapes[0]]

percentage_of_null_values = (N_of_null_values.sort_values(ascending=False) / Country_shapes[0]) *100
# if null values Precnetage is bigger than 75 %  then the column is useless
# WB-2 code  is the same as  2-alpha code  so i will delete one of them
EDStatsCountry.drop(['Unnamed: 31','National accounts reference year','Alternative conversion factor','Other groups','2-alpha code','Table Name'],axis=1,inplace=True)

valid_iso = {c.alpha_2 for c in pc.countries}
valid_iso = list(valid_iso)
fake_country = EDStatsCountry[~EDStatsCountry["WB-2 code"].isin(valid_iso)]
N_Fake_Countries = fake_country.shape[0]
fake_country_null_values=fake_country.isnull().sum()
fake_country_Names = fake_country['Short Name'].tolist()
RealCountry_EDStatsCountry = EDStatsCountry[EDStatsCountry["WB-2 code"].isin(valid_iso)].drop_duplicates()

### fill missing values in Region

Regions = RealCountry_EDStatsCountry['Region'].value_counts().index.tolist()

missing_region = RealCountry_EDStatsCountry[RealCountry_EDStatsCountry["Region"].isna()]

region_mapping = {"Gibraltar": "Europe & Central Asia","Nauru": "East Asia & Pacific"}
RealCountry_EDStatsCountry["Region"] = RealCountry_EDStatsCountry.apply(lambda row: region_mapping.get(row["Short Name"], row["Region"]), axis=1)




# 2 : EDStatsSeries : This is the dictionary of indicators — it describes what each “indicator” means and its category.
EDStatsSeries.drop(["Development relevance","Related source links","Other web links","Related indicators","License Type"],axis=1,inplace=True)
EDStatsSeries_shapes = EDStatsSeries.shape
EDStatsSeries_N_of_null_values =EDStatsSeries.isnull().sum()
EDStatsSeries_info = EDStatsSeries.info
EDStatsSeries_heads = EDStatsSeries.head()
EDStatsSeries_descriptions = EDStatsSeries.describe()
EDStatsSeries_N_of_unique = EDStatsSeries.nunique().sort_values(ascending=False).reset_index(name='nunique')
EDStatsSeries_keys=EDStatsSeries_N_of_unique[EDStatsSeries_N_of_unique['nunique'] == EDStatsSeries_shapes[0]]

EDStatsSeries_percentage_of_null_values =  (EDStatsSeries_N_of_null_values.sort_values(ascending=False) / EDStatsSeries_shapes[0]) *100
topics_to_keep = [ "Learning Outcomes", "Attainment","Education Equality","Primary", "Secondary","Tertiary","Pre-Primary","Teachers", "Expenditures", "Literacy", "Early Childhood Education", "Post-Secondary/Non-Tertiary","Population", "Education Management Information Systems (SABER)"]
EDStatsSeries = EDStatsSeries[EDStatsSeries['Topic'].isin(topics_to_keep)].drop_duplicates()


##### EDStatsData ###########

EDStatsData= pd.merge(EDStatsData,RealCountry_EDStatsCountry['Country Code'],"inner",on='Country Code').merge(EDStatsSeries[["Series Code","Topic"]],how='inner',left_on='Indicator Code',right_on="Series Code")
EDStatsData_columns = EDStatsData.columns.tolist()
EDStatsData_shapes = EDStatsData.shape
EData_N_of_null_values =EDStatsData.isnull().sum()
EDStatsData_info=EDStatsData.info
EDStatsData_heads = EDStatsData.head()
EDStatsData_descriptions = EDStatsData.describe()
EDStatsData_N_of_unique = EDStatsData.nunique().sort_values(ascending=False).reset_index(name='nunique')
EDStatsData_keys=EDStatsData_N_of_unique[EDStatsData_N_of_unique['nunique'] == EDStatsData_shapes[0]]
EDStatsData_percentage_of_null_values =  (EData_N_of_null_values.sort_values(ascending=False) / EDStatsData_shapes[0]) *100
# drop useless columns
EDStatsData.drop(['Unnamed: 69',"Series Code"],inplace=True,axis=1) # here i deleted also Series Code that comes from the join

# 3 : EDStatsFootNote
EDStatsFootNote= pd.merge(EDStatsFootNote,RealCountry_EDStatsCountry,'inner',left_on='CountryCode',right_on='Country Code').merge(EDStatsSeries["Series Code"],how='inner',left_on="SeriesCode",right_on="Series Code").drop_duplicates()

# 4 StatsCountry
EDStatsCountrySeries= pd.merge(EDStatsCountrySeries,RealCountry_EDStatsCountry,'inner',left_on='CountryCode',right_on='Country Code').merge(EDStatsSeries["Series Code"],how='inner',left_on="SeriesCode",right_on="Series Code").drop_duplicates()

# extract all years values to put them in a pivot table :
year_cols = [c for c in EDStatsData.columns if c.isdigit()]
EDStatsData['mean_value'] = EDStatsData[year_cols].mean(axis=1)

# the average of all indicators per country :
EDStatsData_grouped_by_country = EDStatsData.groupby("Country Name")["mean_value"].mean()

# # the average of all indicators per country and topic :
EDStatsData_groupedby_topic =EDStatsData.groupby(['Country Name','Topic'])['mean_value'].mean().reset_index(name= 'Indic_avg')
EDStatsData_pivot_data_by_topic = EDStatsData_groupedby_topic.pivot(index= 'Country Name',columns='Topic',values='Indic_avg')

# # the average of all indicators per country and indicators  :
EDStatsData_pivot_data_by_indicator =EDStatsData.pivot(index="Country Name" ,columns ='Indicator Code',values='mean_value')

for topic in topics_to_keep :
  df = EDStatsData[EDStatsData["Topic"] == topic]
  data_grouped = (df.groupby("Country Name")["mean_value"].mean().sort_values(ascending=False))

# Show the top 10 countries by each Topic
# there is a country that  I consider it as outliers so I  removed the first country (Tuvalu)
  top10 = data_grouped.iloc[1 :11]
  plt.figure(figsize=(10,5))
  sns.barplot(x=top10.values, y=top10.index)
  plt.title(f"Top 10 Countries by {topic} (Mean Value)")
  plt.xlabel("Average Expenditure Indicator Value")
  plt.ylabel("Country")
  #plt.show()


plt.figure(figsize=(10, 8))
sns.heatmap(EDStatsData_pivot_data_by_indicator.iloc[ : , 0 : 11].corr(), annot=True, cmap='coolwarm', center=0)
plt.title("Correlation between indicators")
#plt.show()

plt.figure(figsize=(10, 8))
sns.heatmap(EDStatsData_pivot_data_by_indicator.corr(method="spearman"), cmap="coolwarm", center=0)
plt.title("Spearman Correlation Between Indicators")
#plt.show()













