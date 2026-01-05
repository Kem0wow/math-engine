import plotly.express as px 

df = px.data.iris() 

# plotting the bar chart
fig = px.bar(df, x="sepal_width", y="sepal_length") 

fig.show()