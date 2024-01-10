#!/usr/bin/env python
# coding: utf-8

# Import libraries

# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


# Importing Data

# In[3]:


df=pd.read_csv(r"C:\Users\Mohit\Downloads\rfm_data.csv")
df.head(50)


# Info of Dataframe

# In[4]:


df.info()


# As we can see DataType of PurchaseDate object now we need to update the datatype

# In[5]:


from datetime import datetime
df['PurchaseDate']=pd.to_datetime(df['PurchaseDate'])


# Check Unique values

# In[6]:


df.nunique()


# Now lets get the insights

# Getting Customer counts according to location

# In[7]:


location_counts = df.groupby('Location')['CustomerID'].count().reset_index()
location_counts = location_counts.rename(columns={"CustomerID": "Customer_Counts"})

fig = px.bar(location_counts, x='Location', y='Customer_Counts', color='Customer_Counts')

# Show the plot
fig.show()


# Revenue by Products

# In[8]:


Product_revenue=df.groupby('ProductInformation')['TransactionAmount'].sum().reset_index()
Product_revenue=Product_revenue.rename(columns={'ProductInformation':'Products','TransactionAmount':'Revenue'})
fig1=px.pie(Product_revenue,names=Product_revenue['Products'],values=Product_revenue['Revenue'])
fig1


# We can analyse the data on the basis of Months Also, we can get the trend

# In[9]:


df['months']=df['PurchaseDate'].dt.month


# In[10]:


revenue_month=df.groupby('months')['TransactionAmount'].sum().reset_index()
revenue_month=revenue_month.rename(columns={'TransactionAmount':'Revenue'})

#plot the trend of revenue by Month
fig2=px.line(revenue_month,x=revenue_month['months'],y=revenue_month['Revenue'])
fig2.update_xaxes(tickmode='linear', dtick=1)


# Insight:- Significant increase from month 4 to month 5, nearly doubling and Substantial decrease in revenue from month 5 to month 6.

# Now we are doing RFM analysis

# In[11]:


#calculating Recency
df['Recency']=(datetime.now().date()-df['PurchaseDate'].dt.date).dt.days


# In[14]:


#Frequency
frequency=df.groupby('CustomerID')['OrderID'].count().reset_index()
frequency.rename(columns={'OrderID': 'Frequency'},inplace=True)
frequency


# Now we are joining both the tables and map the frquency of  customer against the customer id

# In[15]:


df=df.merge(frequency,on='CustomerID',how="left")
df


# In[16]:


# Calculate Monetary Value
monetary = df.groupby('CustomerID')['TransactionAmount'].sum().reset_index()
monetary.rename(columns={'TransactionAmount': 'MonetaryValue'}, inplace=True)
df= df.merge(monetary, on='CustomerID', how='left')


# Assigning Scores

# In[18]:


recency_scores = [5, 4, 3, 2, 1]  # Higher score for lower recency (more recent)
frequency_scores = [1, 2, 3, 4, 5]  # Higher score for higher frequency
monetary_scores = [1, 2, 3, 4, 5]  # Higher score for higher monetary value

# Calculate RFM scores
df['RecencyScore'] = pd.cut(df['Recency'], bins=5, labels=recency_scores)
df['FrequencyScore'] = pd.cut(df['Frequency'], bins=5, labels=frequency_scores)
df['MonetaryScore'] = pd.cut(df['MonetaryValue'], bins=5, labels=monetary_scores)


# In[19]:


#checking the info
df.info()


# As we can see the new added columns are has the datatype- Object we need to change it

# In[21]:


df['RecencyScore'] =df['RecencyScore'].astype(int)
df['FrequencyScore'] =df['FrequencyScore'].astype(int)
df['MonetaryScore'] =df['MonetaryScore'].astype(int)


# Now let’s calculate the final RFM score

# In[22]:


df['RFM']=df['RecencyScore']+df['FrequencyScore']+df['MonetaryScore']


# In[23]:


df


# let's the value segment according to the scores:

# In[24]:


segment_labels = ['Low-Value', 'Mid-Value', 'High-Value']
df['Value Segment'] = pd.qcut(df['RFM'], q=3, labels=segment_labels)


# In[25]:


#insights of it
px.histogram(df,x='Value Segment',color='Value Segment')


# Now let’s create and analyze RFM Customer Segments that are broader classifications based on the RFM scores. These segments, such as “Champions”, “Potential Loyalists”, and “Can’t Lose” provide a more strategic perspective on customer behaviour and characteristics in terms of recency, frequency, and monetary aspects. Here’s how to create the RFM customer segments:

# In[26]:


df['RFM_Customer_Segments']=""

#assigning the tags
df.loc[df['RFM'] >= 9, 'RFM_Customer_Segments'] = 'Champions'
df.loc[(df['RFM'] >= 6) & (df['RFM'] < 9), 'RFM_Customer_Segments'] = 'Potential Loyalists'
df.loc[(df['RFM'] >= 5) & (df['RFM'] < 6), 'RFM_Customer_Segments'] = 'At Risk Customers'
df.loc[(df['RFM'] >= 4) & (df['RFM'] < 5), 'RFM_Customer_Segments'] = "Can't Lose"
df.loc[(df['RFM'] >= 3) & (df['RFM'] < 4), 'RFM_Customer_Segments'] = "Lost"


# In[27]:


#Insights according to tags
px.histogram(df,x='RFM_Customer_Segments',color='RFM_Customer_Segments')


# Now let’s analyze the distribution of customers across different RFM customer segments within each value segment:

# In[28]:


segment_product_counts = df.groupby(['Value Segment', 'RFM_Customer_Segments']).size().reset_index(name='Count')
segment_product_counts=segment_product_counts.sort_values('Count', ascending=False)

#Treemap

treemap_segment_product = px.treemap(segment_product_counts, 
                                         path=['Value Segment', 'RFM_Customer_Segments'], 
                                         values='Count',
                                         color='Value Segment', color_discrete_sequence=px.colors.qualitative.Pastel,
                                         title='RFM Customer Segments by Value')
treemap_segment_product.show()


# Now let’s have a look at the recency, frequency, and monetary scores of all the segments:

# In[30]:


# Calculate the average Recency, Frequency, and Monetary scores for each segment
segment_scores = df.groupby('RFM_Customer_Segments')['RecencyScore', 'FrequencyScore', 'MonetaryScore'].mean().reset_index()
segment_scores


# In[31]:


import plotly.graph_objects as go
# Create a grouped bar chart to compare segment scores
fig = go.Figure()

# Add bars for Recency score
fig.add_trace(go.Bar(
    x=segment_scores['RFM_Customer_Segments'],
    y=segment_scores['RecencyScore'],
    name='Recency Score',
    marker_color='rgb(158,202,225)'
))

# Add bars for Frequency score
fig.add_trace(go.Bar(
    x=segment_scores['RFM_Customer_Segments'],
    y=segment_scores['FrequencyScore'],
    name='Frequency Score',
    marker_color='rgb(94,158,217)'
))

# Add bars for Monetary score
fig.add_trace(go.Bar(
    x=segment_scores['RFM_Customer_Segments'],
    y=segment_scores['MonetaryScore'],
    name='Monetary Score',
    marker_color='rgb(32,102,148)'
))

# Update the layout
fig.update_layout(
    title='Comparison of RFM Segments based on Recency, Frequency, and Monetary Scores',
    xaxis_title='RFM Segments',
    yaxis_title='Score',
    barmode='group',
    showlegend=True
)

fig.show()


# Conclusion:
# 1.The "Can't Lose" segment stands out with consistently high engagement, making them prime candidates for loyalty programs and personalized offers.
# 
# 2."Champions" represent valuable customers, but their low recency warrants attention. Targeted strategies to re-engage this segment may yield significant returns.
# 
# 3."At Risk Customers" show recent activity but lack frequency. Implementing retention campaigns to increase engagement could prove beneficial.
# 
# 4."Potential Loyalists" exhibit potential for increased engagement. Targeted marketing efforts may convert them into more frequent and higher-value customers.
# 
# 5.The "Lost" segment requires careful consideration. Assessing the possibility of reactivation or understanding the reasons behind their inactivity is essential.
# 
# This analysis guides strategic decision-making, helping to tailor marketing and retention efforts for each customer segment.
