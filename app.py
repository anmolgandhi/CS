import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from test_final import getdata
import random
import plotly
from plotly.offline import plot
import re
import dash_table
import os
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from elasticsearch import Elasticsearch 
import grasia_dash_components as gdc

external_stylesheets = ['/assets/client.css']

#external_js = ["http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"]


global search 
global tweet_stream

external_scripts = [{'src': 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js'}]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts = external_scripts)
app.config['suppress_callback_exceptions']=True

es=Elasticsearch([{'host':'192.168.231.142','port':9200}])

def getcolor(label):
  if(label == "Alternate"):
    color = "blue"
  elif(label =="Securities"):
    color = "navy"
  elif(label == "Cash"):
    color = "lightblue"
  else:
    color = "black"
  return(color)


def df_to_table(df):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns])] +
        
        # Body
        [
            html.Tr(
                [

                    html.Td((df.iloc[i][col]),style={"color":getcolor(df.iloc[i][col])})
                    for col in df.columns
                      
                    
                ],
                #id = str(i)

            )
            for i in range(len(df))
        ],
    )


def replace_name(df,cat):
  df = df[df[cat] != "uncategorized"]
  a = ["security",'alternate','cash']
  b = ['Securities','Alternate','Cash']
  for i,j in zip(a,b):
    df[cat] = df[cat].str.replace(i,j)
  return(df)
  

def client_email(res):
  a=[]
  b=[]
  c=[]
  for i in range(0,len(res["_source"]["EmailInfo"]["_emailInfoList"])):
    a.append(res["_source"]["EmailInfo"]["_emailInfoList"][i]["_textBody"])
    b.append(res["_source"]["EmailInfo"]["_emailInfoList"][i]["_subject"])
    c.append(res["_source"]["EmailInfo"]["_emailInfoList"][i]["_label"])
  emails = pd.DataFrame({"Client Email":b,"Body":a,"Affinity":c})
  emails1 = emails[["Client Email","Affinity"]]
  emails1 = replace_name(emails1,"Affinity")
  return(emails1)


def client_mentions(emails1):
  emails2 = emails1.rename(index = str, columns = {'Client Email':"Client Mentions","Affinity":"Affinity"})
  emails2 = replace_name(emails2,"Affinity")
  return(emails2)


def client_tweets(res):
  a = []
  b = []
  for i in range(0,len(res["_source"]["TwitterInfo"]["_sentimentList"])):
    a.append(res["_source"]["TwitterInfo"]["_sentimentList"][i]["_tweet"])
    b.append(res["_source"]["TwitterInfo"]["_sentimentList"][i]["_label"])
  tweets = pd.DataFrame({"Client Tweets": a,"Affinity": b})
  tweets = replace_name(tweets,"Affinity")
  return(tweets)

def get_tweet_stream(res):
  tweet_stream = pd.DataFrame(pd.Series(res["hits"]["hits"]).apply(lambda x: x["_source"]['message']),columns = ["Tweet Mentions"]) 
  a=[]
  for i in range(0,len(res["hits"]["hits"])):
    a.append(res["hits"]["hits"][i]["_source"]["label"])
  tweet_stream["Affinity"] = a
  tweet_stream = replace_name(tweet_stream,"Affinity")
  return(tweet_stream)


def ktf(res2):
  a = []
  b = []
  c = []
  for i in range(0,len(res2["_source"]["_KTFInfoList"])):
    a.append(res2["_source"]["_KTFInfoList"][i]["_category"])
    b.append(res2["_source"]["_KTFInfoList"][i]["_keyword"])
    c.append(res2["_source"]["_KTFInfoList"][i]["_keyword_frequency"])
  ktf = pd.DataFrame({"category": a,"keyword": b,"keyword_frequency":c})
  ktf = replace_name(ktf,"category")
  ktf1 = ktf.groupby("keyword").sum().reset_index().sort_values(by ="keyword_frequency",ascending = False)
  color = ktf["category"].apply(lambda x: getcolor(x))
  return(ktf1,color)

def logic_investment(emails1,tweets,tweet_stream):
  print(tweet_stream)
  pie_1 = emails1.Affinity
  print(1)
  print(pie_1)
  pie_1 = pie_1.append(tweets.Affinity,ignore_index = True)
  print(2)
  print(pie_1)
  pie_1 = pie_1.append(tweet_stream["Affinity"], ignore_index = True)
  print(3)
  pie_1 = pie_1[pie_1 != "uncategorized"]
  return(pie_1)


def dashboard(input_value):
    global search
    
   
    keyword = input_value
    
    a = {"Bill Gates":1,"Pierre":0}
    res=es.get(index='user_profile',doc_type='individual',id= a.get(input_value))
  
    emails1 = client_email(res)
    emails2 = client_mentions(emails1)

    tweets = client_tweets(res)


    res2=es.get(index='user_ktf_info',doc_type='individual',id=a.get(input_value))

    ktf1, color = ktf(res2)


    aum = int(res["_source"]["AssetsInfo"]["_aum"])/100

    res1 = es.search(index="tweetstream", doc_type="tweet", body={"query": {"match": {"message": keyword}}}, size=1000, from_=0)
    tweet_stream= get_tweet_stream(res1)
    pie_1 = logic_investment(emails1,tweets,tweet_stream)

    search = input_value
    input_value = "input"
    

    return (html.Div([

  html.H6("Client Overview",style = {'font-weight':'bold','margin': "20px 10px",'font-size':'30','text-align':'center'}),
    html.Hr(),
    html.Div([
  html.Img(src='/assets/bill.png',style = {'border-radius':'60%','height':'120px', 'margin': "10px 10px",'float':'center'})],style = {'backgroundColor': 'white','border-radius':'50%','width':'150px','margin':'0px 75px'}),
  html.P(res["_source"]["IndividualInfo"]["_nameInfo"]["firstName"] + res["_source"]["IndividualInfo"]["_nameInfo"]["lastName"], style={'margin': "20px 10px",'font-weight':'bold'}),
  html.P("Estimated Net Worth: "+ "$10 Billion" ,style={'margin': "0px 10px"}),
  html.Hr(),

  html.P("Contact Information",style = {'margin': "0px 10px",'font-size':'20'}),
html.Div([
  html.Img(src='/assets/phone.png',style = {'border-radius':'60%','height':'20px','float':'left'}),

 html.P(res["_source"]["ContactInfo"]["_phoneInfo"]["phoneNumber"], style={'margin':'0px 20px'})],className = "row",style = {'margin':'20px 50px'}),
html.Div([
  html.Img(src='/assets/home.png',style = {'border-radius':'60%','height':'20px','float':'left'}),

 html.P(res["_source"]["ContactInfo"]["_addressInfo"]["city"] + ", " + res["_source"]["ContactInfo"]["_addressInfo"]["state"] , style={'margin':'0px 30px'})],className = "row",style = {'margin':'20px 50px'}),
html.Div([
  html.Img(src='/assets/email.png',style = {'border-radius':'60%','height':'20px','float':'left'}),

 html.P(res["_source"]["ContactInfo"]["_emailInfo"]["electronicAddress"], style={'margin':'0px 30px'})],className = "row",style = {'margin':'20px 50px'}),
  html.Hr(),
html.Div([
    #html.P("Tweet Sentiment analyis",style={'text-align':'left','color':'#2e373e'}),
    html.Div(html.P("Assets Under Management",style = {'margin': "10px 10px",'font-size':'20'})),
    html.Div(html.P("Aum: " + "$" + str(int(res["_source"]["AssetsInfo"]["_aum"])) + " Million" )),
     dcc.Graph(
        id='life-exp-vs-gdp12',
        config=dict(displayModeBar=False),
        figure={
            'data': [
                go.Pie(labels=list(["cash","securities","Alternative investment"]), values=list([int(res["_source"]["AssetsInfo"]["_aumInfo"]["cash"])/aum,int(res["_source"]["AssetsInfo"]["_aumInfo"]["securites"])/aum,int(res["_source"]["AssetsInfo"]["_aumInfo"]["other"])/aum]), marker={'colors' : ['lightblue','navy','blue' ]})
            ],
            'layout': go.Layout(
                paper_bgcolor="#2e373e",
                font = {'color': '#dbddd6'},
                legend=dict(orientation="h"),
                margin=dict(l=15, r=10, b=30, t=7, pad=1),
               #plot_bgcolor="#2e373e",
            )
        },
        style={'float':'center','height':'300px'},
    ),
]),
 #html.P("Country:" + " " + personal["country"], style={'margin': "10px 30px"})

      ],style = {'boxShadow': '0px 0px 5px 0px rgba(204,204,204,0.4)',"backgroundColor":"#2e373e",'color':'#dbddd6','height':'960px','text-align':'center'}, className = "three columns"),


html.Div([

html.Div([
    html.Div([
     html.Div([
    dcc.Input(id='my-id', value=input_value, type='text',style={"width":"600px","color":"#dbddd6"}),
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.Div(id='my-div'),
    
],style={'float':'left', 'margin': '25px 85px',}),
    html.Div([
    
    html.Img(src='/assets/logo.svg',style = {'border-radius':'60%','height':'100px'})],style={'float':'right','margin':'0px 0px 0px 100px'}),])
    ],className="row",style={'margin':'0px',
    'background-color': 'whitesmoke',
    'height': '90px',
    'color': 'white','vertical-align': 'middle'}),


html.Div([

html.Div([
    #html.P("Personal Information",style={'text-align':'left','color':'navy'}),
  html.Div([
        #html.P("Top Mentions",  style={'text-align':'left','color':'#2e373e'}), 
          html.Div([
            dcc.Dropdown(
                 id="new_case_account",
                        options=[
                            {
                                "label":i ,
                                "value": i,
                                      }
                              for i in ["Cash","Securities","Alternate"]
                                 ],
                                clearable=True,
                                )
                                        ],style = {'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'}),
        dcc.Graph(
        id='life-exp-vs-gdp1',
        config=dict(displayModeBar=False),
        figure={
            'data': [
                go.Pie(labels=list(list(pie_1.value_counts().index)), values=list(list(pie_1.value_counts().values)), marker={'colors' : ['blue','lightblue,','navy' ]})
            ],
            'layout': go.Layout(
              title = "Investment Affinity"
            #   barmode="stack",
            #margin=dict(l=0, r=0, b=0, t=0, pad=1),
            #   paper_bgcolor="white",
            #   plot_bgcolor="white",
            )
        },
        style={'float':'center','height':'314px','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'},
    ),
       ],className="four columns",),
    

   
     html.Div([
    #html.P("Tweet Sentiment analyis",style={'text-align':'left','color':'#2e373e'}),
    dcc.Graph(
        id='life-exp-vs-gdp11',
        figure={
            'data': [go.Bar(x=list(list(ktf1["keyword_frequency"])), 
                        y=list(list(ktf1["keyword"])),
                        orientation='h',
                    marker = {"color" : list(color)}


            )],
            'layout': go.Layout(
               barmode="stack",
               title = 'Top Keywords',
               margin=dict(l=110, r=10, b=30, t=50, pad=1),
               #paper_bgcolor="white",
               #plot_bgcolor="white",
               yaxis=dict(autorange="reversed")

            ),
        },
        style={'float':'center','height':'350px', 'width':'711px', 'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'},
    ),
],className = "seven columns",style = {'margin':"0px 16px"})
], className ="row",),
  html.Hr(),


html.Div([
      
    html.Div([html.Div([
        df_to_table(emails1)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','backgroundColor':'white'}),
        html.Div([
        df_to_table(emails2)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','backgroundColor':'white','margin':"10px 0px"}),


    ],id = 'my-div11',className="six columns"),
        
    html.Div([html.Div([df_to_table(tweets)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','backgroundColor':'white'}),
        html.Div([
        df_to_table(tweet_stream)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','backgroundColor':'white','margin':"10px 0px"}),
],id = "my-div121", className="six columns",style = {'margin':'0px 22px'}),
     
],id = "all", className ="row",style = {'margin':'30px 0px'}),


],style = {'margin': '20px 120px'},className="eight columns offset-by-one"),

 

],style = {"backgroundColor":"whitesmoke"},className = 'row')

)




app.layout = html.Div([

 #html.P("Country:" + " " + personal["country"], style={'margin': "10px 30px"})


html.Div([


html.Div([
    html.Div([
     html.Div([
    dcc.Input(id='my-id', value="input", type='text',style={"width":"600px","color":"#dbddd6"}),
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.Div(id='my-div'),
    
],style={'float':'left', 'margin': '25px 85px',}),
    html.Div([
    
    html.Img(src='/assets/logo.svg',style = {'border-radius':'60%','height':'100px'})],style={'float':'right','margin':'0px 0px 0px 100px'}),])
    ],className="row",style={'margin':'0px',
    'background-color': 'whitesmoke',
    'height': '90px',
    'color': 'white','vertical-align': 'middle'}),


])],id = "final" ,style = {'font-family':"Arial"})




@app.callback(
    Output(component_id='final', component_property='children'),
    [Input('submit-button', 'n_clicks')],
    [State(component_id='my-id', component_property='value')]
)
def update_output_div(n_clicks,input_value):
    return( dashboard(input_value))


@app.callback(
    Output(component_id='my-div11', component_property='children'),
    [Input('final', 'children'),Input(component_id='new_case_account', component_property='value')],
    [State(component_id='my-id', component_property='value')]
)
def update_output_div1(child,input_value_drop,input_value):
    input_value = search
    global tweet_streams
    a = {"Bill Gates":1,"Pierre":0}
    res=es.get(index='user_profile',doc_type='individual',id= a.get(input_value))
  
    emails1 = client_email(res)

    if(input_value_drop == None):
      Documents2 = emails1
    else:
      Documents2 = emails1[emails1["Affinity"] == input_value_drop]
    

    #Documents = Documents[Documents["label"] == input_value]
    return( html.Div([
        df_to_table(Documents2)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','backgroundColor':'white'}),
        html.Div([
        df_to_table(Documents2)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','margin':"10px 0px",'backgroundColor':'white'}),)

@app.callback(
    Output(component_id='my-div121', component_property='children'),
    [Input('final', 'children'),Input(component_id='new_case_account', component_property='value')],
    [State(component_id='my-id', component_property='value')]
)
def update_output_div1(child,input_value_drop,input_value):
    input_value = search
    print(input_value_drop)
    a = {"Bill Gates":1,"pierre.json":0}
    res=es.get(index='user_profile',doc_type='individual',id= a.get(input_value))
    
    tweets = client_tweets(res)

    res1 = es.search(index="tweetstream", doc_type="tweet", body={"query": {"match": {"message": input_value}}}, size=1000, from_=0)
    tweet_stream= get_tweet_stream(res1)
    
    if(input_value_drop == None):
      tweets1 = tweets
      tweet_stream1 = tweet_stream
    else:
      tweet_stream1 = tweet_stream[tweet_stream["Affinity"] == input_value_drop]
      tweets1 = tweets[tweets["Affinity"] == input_value_drop]

 
    #Documents = Documents[Documents["label"] == input_value]
    return( html.Div([df_to_table(tweets1)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','backgroundColor':'white'}),
        html.Div([
        df_to_table(tweet_stream1)],style = {'height':'170px','overflow':'auto','boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)','backgroundColor':'white','margin':"10px 0px"}),)




if __name__ == '__main__':
    app.run_server(debug=True)