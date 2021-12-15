from dash import html


def make_table(df):
    return html.Table(
        children=[
            html.Thead(
                children=[
                    html.Tr(
                        children=[
                            html.Th(
                                column_name.replace("_", " "))
                            for column_name in df.columns
                        ],
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(2, 1fr)",
                            "fontWeight": "600",
                            "fontSize": 12,
                        },
                    )
                ]
            ),
            html.Tbody(
                style={"maxHeight": "30vh", "display": "block",
                       "overflow": "scroll", },
                children=[
                    html.Tr(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(2, 1fr)",
                            "border-top": "1px solid white",
                            "padding": "30px 5px",
                        },
                        children=[
                            html.Td(
                                value_column, style={"textAlign": "center"}
                            ) for value_column in value
                        ],
                    )
                    for value in df.values
                ]
            )
        ]
    )
