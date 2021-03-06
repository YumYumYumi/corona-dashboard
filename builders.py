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
                            "fontWeight": "700",
                            "fontSize": 13,
                        },
                    )
                ]
            ),
            html.Tbody(
                style={"maxHeight": "370px", "display": "block"},
                children=[
                    html.Tr(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(2, 1fr)",
                            "border-top": "1px solid white",
                            "padding": "10px 5px",
                            "fontSize": 13,
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
