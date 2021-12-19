"""
after change sth, plz write down in terminal,
git add .
git commit -m "New title"
git push heroku master (or main)
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from data import countries_df, dropdown_options, make_global_confirmed_df, make_country_confirmed_df, top10_table, totals_df_bar, all_merged_df, new_melted_df, all_continents
import plotly.express as px
import pandas as pd
from builders import make_table

stylesheets = ["https://cdn.jsdelivr.net/npm/reset-css@5.0.1/reset.min.css",
               "https://fonts.googleapis.com/css2?family=Open+Sans&display=swap", ]

app = dash.Dash(__name__, external_stylesheets=stylesheets)
app.title = "Corona-Dashboard"

server = app.server

bubble_map = px.scatter_geo(countries_df,
                            size="7_Days_Incidence_Rate",
                            hover_name="Country_Region",
                            color="7_Days_Incidence_Rate",
                            locations="Country_Region",
                            locationmode="country names",
                            size_max=30,
                            template="plotly_dark",
                            color_continuous_scale=px.colors.sequential.dense,
                            projection="natural earth",
                            hover_data={
                                "Confirmed": ":,",
                                "Deaths": ":,",
                                "Population": ":,",
                                "Yesterday_Confirmed": ":,",
                                 "Country_Region": False
                            })
bubble_map.update_layout(
    margin=dict(l=0, r=0, t=50, b=50),
    title={
        'text': "7 Days Incidence Rate By Country",
        'y': 0.97,
        'x': 0.424,
        'xanchor': 'center',
        'yanchor': 'top'},
    title_font=dict(size=28))

bars_graph_vac = px.bar(totals_df_bar,
                        x="condition",
                        y="count",
                        template="plotly_dark",
                        hover_data={'count': ":,"},
                        labels={"condition": "Condition", "count": "Count", "color": "Condition"})
bars_graph_vac.update_traces(marker_color=["#ff5e57", "#0be881"])
bars_graph_vac.update_layout(
    margin=dict(l=0, r=0, t=50, b=50),
    title={
        'text': "Fully Vaccinated vs. World Population",
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    title_font=dict(size=14))


choro_vaccine_map = px.choropleth(countries_df, locations="Country_Region",
                                  locationmode="country names",
                                  color="Fully_vaccinated_percent",
                                  template="plotly_dark",
                                  projection="natural earth",
                                  hover_name="Country_Region",
                                  hover_data={
                                      "Population": ":,",
                                      "People_fully_vaccinated": ":,",
                                      "Country_Region": False
                                  },
                                  color_continuous_scale=px.colors.sequential.Oryel)

choro_vaccine_map.update_layout(
    margin=dict(l=0, r=0, t=50, b=50),
    title={
        'text': "% of the population fully vaccinated against COVID-19",
        'y': 0.97,
        'x': 0.424,
        'xanchor': 'center',
        'yanchor': 'top'},
    title_font=dict(size=28))

animation_graph = px.scatter(all_merged_df, x="Fully_vaccinated_percent", y="Incidence_Rate",
                             animation_frame="Date", animation_group="Country",
                             size="Population", color="region", hover_name="Country", facet_col="region",
                             # color_discrete_sequence=px.colors.sequential.Agsunset,
                             log_y=True,
                             template="plotly_dark",
                             size_max=40, range_x=[0, 100], range_y=[10, 1000])

animation_graph.update_layout(transition={'duration': 10})

app.layout = html.Div(
    style={"textAlign": "center", "minHeight": "100vh", "backgroundColor": "#111111",
           "color": "white", "fontFamily": "Open Sans, sans-serif", },
    children=[
        html.Header(
            style={"textAlign": "center",
                   "paddingTop": "50px", "marginBottom": 100},
            children=[html.H1("Corona Dashboard", style={
                              "fontSize": 70, "fontWeight": 700})],
        ), html.Div(
            style={"display": "grid",
                   "gap": 50,
                   "gridTemplateColumns": "repeat(2,1fr)",
                   },
            children=[
                html.Div(
                    style={"grid-column": "span 2"},
                    children=[
                        dcc.Dropdown(
                            style={
                                "width": 700,
                                "margin": "0 auto",
                                "color": "#111111",
                            },
                            placeholder="Select a Country",
                            id="country",
                            options=[
                                {'label': country, 'value': country}
                                for country in dropdown_options
                            ],
                        ),
                        dcc.Graph(id="country-graph"),
                    ])
            ]
        ),
        html.Div(
            style={"display": "grid",
                   "gap": 50,
                   "gridTemplateColumns": "repeat(2,1fr)",
                   },
            children=[
                html.Div(
                    style={"grid-column": "span 2"},
                    children=[
                        dcc.Checklist(
                            style={
                                "width": 1000,
                                "paidding": "10px",
                                "margin": "0 auto",
                                "color": "#ffffff",
                            },
                            id="checklist",
                            options=[
                                {'label': continent, 'value': continent}
                                for continent in all_continents
                            ],
                            value=all_continents[11:12],
                            labelStyle={'display': 'inline-block'}
                        ),
                        dcc.Graph(id="line-chart"),
                    ])
            ]
        ), html.Div(
            style={"display": "grid",
                   "gap": 50,
                   "gridTemplateColumns": "repeat(2,1fr)",
                   },
            children=[
                html.Div(
                    style={"grid-column": "span 2"},
                    children=[
                        dcc.Graph(figure=animation_graph),
                    ])
            ]
        )

    ],
)


@app.callback(Output("country-graph", "figure"), [Input("country", "value")])
def update_hello(value):
    if value:
        df = make_country_confirmed_df(value)
    else:
        df = make_global_confirmed_df()
    fig = px.line(
        df,
        x="date",
        y="Confirmed",
        template="plotly_dark",
        labels={"value": "Cases", "variable": "Confirmed", "date": "Date"}
    )
    fig.update_xaxes(rangeslider_visible=True)
    return fig


@app.callback(
    Output("line-chart", "figure"),
    [Input("checklist", "value")])
def update_line_chart(continents):
    mask = new_melted_df.subregion.isin(continents)
    df = new_melted_df[mask]
    y_max = df.Incidence_Rate.max()
    fig = px.line(df,
                  x="Date", y="Incidence_Rate", color='Country',
                  hover_name="Country",
                  template="plotly_dark",
                  range_y=[0, y_max])
    return fig


# if __name__ == '__main__':
   # app.run_server(debug=True)
