#!/usr/bin/env python
# coding: utf-8

# ### Intro

# In[ ]:


# python modules
import base64
from dash import dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import io
from jupyter_dash import JupyterDash
import numpy as np
import pandas as pd


# ### App Layout
# #### Dash components

# In[ ]:


# dbc button: upload appointments csv
bt_up = dcc.Upload(
    dbc.Button(
        html.P(
            ["Click to Upload ", html.Code("csv"), " File"],
            style={"margin-top": "12px", "fontWeight": "bold",},
        ),
        id="btn",
        class_name="me-1",
        outline=True,
        color="success",
    ),
    id="upload-data",
)

# dbc button: missing data
bt_miss = dbc.Button(
    html.P(
        ["Click to Validate ", html.Code("csv"), " File"],
        style={"margin-top": "12px", "fontWeight": "bold",},
    ),
    id="btn-val",
    class_name="me-1",
    outline=True,
    color="primary",
)

# dash date picker
date_picker = dcc.DatePickerRange(
    id="my-date-picker-range",
    min_date_allowed=date(2016, 1, 1),
    max_date_allowed=date(2030, 12, 31),
    # initial_visible_month=date(2022, 1, 1),
    start_date=date(2022, 1, 1),
    end_date=date(2022, 12, 31),
    display_format="Do MMM YYYY",
    style={"fontSize": 20},
)

# button: execute KPIs
# bt_kpi = html.Button("Refresh KPIs", id="btn-kpi")

# dbc appointments row
appoint_row = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.P(
                            "Load Appointments",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "18px",
                                "marginBottom": "10px",
                                "textAlign": "center",
                            },
                        ),
                        bt_up,
                        html.Div(
                            id="uploading-state",
                            className="output-uploading-state",
                            style={"color": "DarkGreen", "textAlign": "center",},
                        ),
                    ]
                ),
                width="auto",
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P(
                            "Check Missing Data",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "18px",
                                "marginBottom": "10px",
                                "textAlign": "center",
                            },
                        ),
                        bt_miss,
                    ]
                ),
                width="auto",
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P(
                            "Click to Select Dates",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "18px",
                                "marginBottom": "20px",
                                "textAlign": "center",
                            },
                        ),
                        date_picker,
                    ]
                ),
                width="auto",
            ),
        ],
        justify="evenly",
        align="start",
    ),
    fluid=True,
)


# In[ ]:


# function to return cards layout
# dbc kpi card: https://www.nelsontang.com/blog/2020-07-02-dash-bootstrap-kpi-card/
def create_card(card_title, card_num):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(card_title, className="card-title"),
                    html.P("N/A", className="card-value", id=f"card-val-{card_num}"),
                    # note there's card-text bootstrap class ...
                    # html.P(
                    #     "Target: $10.0 M",
                    #     className="card-target",
                    # ),
                    # html.Span([
                    #     html.I(className="fas fa-arrow-circle-up up"),
                    #     html.Span(" 5.5% vs Last Year",
                    #     className="up")
                    # ])
                ]
            )
        ],
        color="danger",
        outline=True,
    )
    return card


# dbc 3 cards deck
cards_row = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                create_card("KPI1: Quantitat de passejades fetes", 1), width="auto"
            ),
            dbc.Col(
                create_card("KPI2: Quantitat de passejades anul·lades", 2), width="auto"
            ),
            dbc.Col(
                create_card("KPI3: Total d’hores passejades fetes", 3), width="auto"
            ),
        ],
        justify="evenly",
    ),
    fluid=True,
)

# dbc 3 cards deck: user
cards_row_user = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                create_card("KPI1: Quantitat de persones usuàries", 4), width="auto"
            ),
            dbc.Col(
                create_card("KPI2: Percentatge de dones usuàries", 5), width="auto"
            ),
            dbc.Col(
                create_card("KPI3: Usuàries més grans i més petites", 6), width="auto"
            ),
        ],
        justify="evenly",
    ),
    fluid=True,
)

# # dbc 2 cards deck
# cards_row_2 = dbc.Container(
#     dbc.Row([
#         dbc.Col(
#             create_card("KPI4: Quantitat de passejades fetes", 4),
#             width="auto"
#         ),
#         dbc.Col(
#             create_card("KPI5: Quantitat de passejades fetes", 5),
#             width="auto"
#         ),
#     ], justify="evenly"),
#     fluid=True
# )


# In[ ]:


# dbc dropdown: user type (not used --> dbc select instead)
# dd_user = dbc.DropdownMenu(
#     label="Tipología d'usuàries",
#     children=[
#         "Usuària Gran",
#         "Usuària amb diversitat funcional",
#         "Usuària amb malaltía (mental, degenerativa...)",
#     ],
#     color="success",
#     class_name="m-1",
#     direction="end",
#     id='my-user-dd'
# )

# dbc select: user type
dd_user = dbc.Select(id="my-user-dd", options=[], value="",)

# dbc dropdown and 4 cards deck: user type
cards_row_type = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                "Select User Type",
                                style={
                                    "fontWeight": "bold",
                                    "fontSize": "18px",
                                    "marginBottom": "10px",
                                    "textAlign": "center",
                                },
                            ),
                            dd_user,
                        ]
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="start",
            style={"paddingLeft": "25px", "marginBottom": "30px",},
        ),
        dbc.Row(
            [
                dbc.Col(create_card("KPI1: Quantitat de persones", 7), width="auto"),
                dbc.Col(create_card("KPI2: Percentatge de dones", 8), width="auto"),
                dbc.Col(create_card("KPI3: Extrems d’edat", 9), width="auto"),
                dbc.Col(create_card("KPI4: Mitjana d’edat", 10), width="auto"),
            ],
            justify="evenly",
        ),
    ],
    fluid=True,
)


# In[ ]:


# dbc select: amenities
dd_amenity = dbc.Select(id="my-amenity-dd", options=[], value="",)

# dbc dropdown and 3-cards two rows deck: amenities
amenity_row_type = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                "Select Amenity",
                                style={
                                    "fontWeight": "bold",
                                    "fontSize": "18px",
                                    "marginBottom": "10px",
                                    "textAlign": "center",
                                },
                            ),
                            dd_amenity,
                        ]
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="start",
            style={"paddingLeft": "25px", "marginBottom": "30px",},
        ),
        dbc.Row(
            [
                dbc.Col(
                    create_card("KPI1: Quantitat de passejades fetes", 11), width="auto"
                ),
                dbc.Col(
                    create_card("KPI2: Quantitat de passejades anul·lades", 12),
                    width="auto",
                ),
                dbc.Col(
                    create_card("KPI3: Total d’hores passejades fetes", 13),
                    width="auto",
                ),
            ],
            justify="evenly",
            style={"marginBottom": "30px"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    create_card("KPI4: Quantitat de persones usuàries", 14),
                    width="auto",
                ),
                dbc.Col(
                    create_card("KPI5: Percentatge de dones usuàries", 15), width="auto"
                ),
                dbc.Col(
                    create_card("KPI6: Mitjana d’edat d’usuàries", 16), width="auto"
                ),
            ],
            justify="evenly",
        ),
    ],
    fluid=True,
)


# #### Dash HTML

# In[ ]:


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
fontawesome_stylesheet = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
# Build App
# app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app = JupyterDash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, fontawesome_stylesheet]
)

# app tittle for web browser
app.title = "EBSE KPIs"

# App Layout
app.layout = html.Div(
    [
        # title Div
        html.Div(
            [
                html.H6(
                    "EBSE KPIs",
                    style={
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "paddingTop": "25px",
                        "color": "white",
                        "fontSize": "32px",
                    },
                ),
            ],
            style={
                "height": "100px",
                "width": "100%",
                "backgroundColor": "DarkRed",
                "margin-left": "auto",
                "margin-right": "auto",
                "margin-top": "15px",
            },
        ),
        # div appointments row
        html.Div([appoint_row], style={"paddingTop": "20px",},),
        html.Hr(
            style={
                "color": "DarkRed",
                "height": "4px",
                "margin-top": "30px",
                "margin-bottom": "0",
            }
        ),
        # div 3-cards row
        dcc.Loading(
            children=html.Div([cards_row], style={"paddingTop": "40px",},),
            id="loading-kpis",
            type="circle",
            fullscreen=True,
        ),
        html.Hr(
            style={
                "color": "DarkRed",
                "height": "2px",
                "margin-top": "30px",
                "margin-bottom": "0",
            }
        ),
        # div 3-cards row: user
        html.Div(
            [cards_row_user], style={"paddingTop": "30px", "margin-bottom": "0",},
        ),
        html.Hr(
            style={
                "color": "DarkRed",
                "height": "2px",
                "margin-top": "30px",
                "margin-bottom": "15px",
            }
        ),
        # div 4-cards row: user type
        dcc.Loading(
            children=html.Div(
                [cards_row_type], style={"paddingTop": "0", "margin-bottom": "0",},
            ),
            id="loading-kpis-user-type",
            type="circle",
            fullscreen=True,
        ),
        html.Hr(
            style={
                "color": "DarkRed",
                "height": "2px",
                "margin-top": "30px",
                "margin-bottom": "15px",
            }
        ),
        # div 3-cards 2-row: amenities
        dcc.Loading(
            children=html.Div(
                [amenity_row_type], style={"paddingTop": "0", "margin-bottom": "40px",},
            ),
            id="loading-kpis-amenity",
            type="circle",
            fullscreen=True,
        ),
        # dbc Modal: output msg from load button - wraped by Spinner?
        dcc.Loading(
            children=dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Upload Message"), close_button=False
                    ),
                    dbc.ModalBody(id="my-modal-body"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="btn-close", class_name="ms-auto")
                    ),
                ],
                id="my-modal",
                is_open=False,
                keyboard=False,
                backdrop="static",
                scrollable=True,
                centered=True,
            ),
            id="loading-modal",
            type="circle",
            fullscreen=True,
        ),
        # hidden div: ouput msg from load button
        html.Div(id="output-data-upload", style={"display": "none"}),
        # hidden div: share csv-df in Dash
        html.Div(id="csv-df", style={"display": "none"}),
        # hidden div: share df-aprov-dates in Dash
        html.Div(id="df-aprov-dates", style={"display": "none"}),
        # hidden div: share df-cancel-dates in Dash
        html.Div(id="df-cancel-dates", style={"display": "none"}),
    ]
)


# ### App Callbacks
# #### Trigger Uploading Printing state

# In[ ]:


# showing Loading trick for dcc Upload? - Also displays loaded filename
@app.callback(
    Output("uploading-state", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def upload_triggers_spinner(_, filename):
    return filename


# #### Upload `csv` File

# In[ ]:


def read_csv_file(contents, filename, date):
    # decoded as proposed in Dash Doc
    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename:
            # Assume user uploaded a csv file
            # read csv into dataframe: appointments
            app_df = pd.read_csv(io.BytesIO(decoded))
        else:
            # Warn user hasn't uploaded a csv file
            return (
                ["Appointments must be a ", html.Code("csv"), " File",],
                {},
            )
    except Exception as e:
        print(e)
        # Warn user csv file hasn't been read
        return (
            f"There was an error processing {filename}",
            {},
        )

    # simple column validation: minimum check of exported database
    col_names_2_check = [
        "Cita ID",
        "Voluntari/a",
        "Servei",
        "Hora incio",
        "Hora final",
        "Número de personas",
        "EQUIPAMENTS",
        "Tipologia P1",
        "Gènere P1",
        "Edat P1",
        "Tipologia P2",
        "Gènere P2",
        "Edat P2",
        "Tipologia P3",
        "Gènere P3",
        "Edat P3",
        "Tipologia P4",
        "Gènere P4",
        "Edat P4",
    ]
    # column list above must be in dataframe
    col_check = [col in app_df.columns for col in col_names_2_check]
    # missing columns
    miss_col = [i for (i, v) in zip(col_names_2_check, col_check) if v]

    # col_check: OK
    # if all(col_check):
    #     # transform datetimes (skipped: lost in json, in kpis_calc)
    #     # note: lost in json --> strictly could be here done
    #     app_df.loc[:, "Hora incio"] = pd.to_datetime(
    #         app_df["Hora incio"], format="%d de %B de %Y %H:%M"
    #     )
    #     app_df.loc[:, "Hora final"] = pd.to_datetime(
    #         app_df["Hora final"], format="%d de %B de %Y %H:%M"
    #     )
    # to-be-safe transform small case (skipped: in kpis_calc)
    # app_df.loc[:, "Servei"] = app_df.Servei.str.lower()

    # return ingestion message and read csv
    return (
        (
            [
                f"Uploaded File is {filename}",
                html.Br(),
                f"Last modified datetime is {datetime.fromtimestamp(date)}",
            ],
            # csv to json: sharing data within Dash
            app_df.to_json(orient="split"),
        )
        if all(col_check)
        else (
            [
                f"Uploaded File is {filename}",
                html.Br(),
                f"Last modified datetime is {datetime.fromtimestamp(date)}",
                html.Br(),
                f"KPIs not calculated. Missing columns: {miss_col}",
            ],
            # no dataframe return
            {},
        )
    )


# In[ ]:


@app.callback(
    Output("output-data-upload", "children"),
    Output("csv-df", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
    prevent_initial_call=True,
)
def wrap_csv_read(loaded_file, file_name, file_last_mod):

    # coded as proposed in Dash Doc
    # callback sees changes in content only (eg: not same content with different filename)
    if loaded_file is not None:
        # returned: (msg_out, app_json)
        return read_csv_file(loaded_file, file_name, file_last_mod)


# #### Return Upload message in *Bootstrap Modal*

# In[ ]:


@app.callback(
    Output("my-modal-body", "children"),
    Output("my-modal", "is_open"),
    Input("output-data-upload", "children"),
    Input("btn-close", "n_clicks"),
    State("my-modal", "is_open"),
    prevent_initial_call=True,
)
def update_modal(msg_in, click_close, is_open):

    # identify callback context
    triger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    # specify action by trigger
    if "data-upload" in triger_id:
        return (
            html.P(msg_in),
            not is_open,
        )
    else:
        # button close
        return {}, not is_open


# #### Update Cards Body - KPIs `passejades` and `usuaries`

# In[ ]:


# appointments table: filter, calculate
def kpis_calc(df, ini_date, end_date):

    # json to dataframe
    df = pd.read_json(df, orient="split")

    # transform datetimes
    df.loc[:, "Hora incio"] = pd.to_datetime(
        df["Hora incio"], format="%d de %B de %Y %H:%M"
    )
    df.loc[:, "Hora final"] = pd.to_datetime(
        df["Hora final"], format="%d de %B de %Y %H:%M"
    )

    # cast ini_date
    ini_date = pd.Timestamp(date.fromisoformat(ini_date))
    # cast and include end_date
    end_date = pd.Timestamp(date.fromisoformat(end_date) + timedelta(days=1))

    # minimum date not in appointments: return empty
    if df["Hora incio"].min() < ini_date:
        return (
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            [],
            "",
            {},
            [],
            "",
            {},
        )

    # filter `passejades` and `Hora incio` within dates
    query_passeig_dates = [
        "`Hora incio` >= @ini_date",
        "`Hora incio` <= @end_date",
        "Servei.str.contains('tricicle', case=False)",
    ]
    df_passeig_in_dates = df.query(
        "&".join(query_passeig_dates), engine="python",
    ).reset_index(drop=True)

    # eliminate duplicated `passejades` (keep first)
    passeig_dupli = df_passeig_in_dates.duplicated(
        subset=["Servei", "Hora incio"], keep="first",
    )
    df_passeig_in_dates.drop(
        df_passeig_in_dates[passeig_dupli].index, inplace=True,
    )

    # `passejades` kpi_1: Aproved Number
    query_kpi_1 = "`Número de personas`.str.contains('aprobado', case=False)"
    df_kpi_1 = df_passeig_in_dates.query(query_kpi_1, engine="python",).reset_index(
        drop=True
    )

    # `passejades` kpi_2: Cancelled Number
    query_kpi_2 = "`Número de personas`.str.contains('cancelada', case=False)"
    df_kpi_2 = df_passeig_in_dates.query(query_kpi_2, engine="python",).reset_index(
        drop=True
    )

    # `passejades` kpi_3: Total of aproved hours
    kpi_3 = (df_kpi_1["Hora final"] - df_kpi_1["Hora incio"]).dt.components.hours.sum()

    # `usuaries` kpi_1: Total number
    # query_kpi_1_user = [
    #     f"`Tipologia P{i}`.fillna('N/A').str.contains('usuària', case=False)"
    #     for i in range(1,5)
    # ]
    # query: at least one user in row --> maybe not needed
    # df_kpi_1_user = df_kpi_1.query(
    #     "|".join(query_kpi_1_user),
    #     engine="python",
    # ).reset_index(drop=True)

    # user type columns filters: only users
    users_masks = [
        (df_kpi_1[f"Tipologia P{i}"].fillna("N/A").str.contains("usuària", case=False))
        for i in range(1, 5)
    ]

    # `usuaries` kpi_1: Total number
    kpi_1_user = sum([elem.sum() for elem in users_masks])

    # note below: could be non-users
    # kpi_1_user = pd.to_numeric(
    #     df_kpi_1_user["Número de personas"].str.split().str[1], errors="coerce"
    # ).sum()

    # `usuaries` kpi_2: Gender percentage
    gender_cols_val_count = [
        df_kpi_1[elem][f"Gènere P{i + 1}"].value_counts(dropna=True)
        for i, elem in enumerate(users_masks)
    ]

    # total number of reported genders
    total_gen_report = np.concatenate(gender_cols_val_count).sum()
    # total number of reported females
    total_fema_report = sum(
        elem.Dona for elem in gender_cols_val_count if "Dona" in elem.index
    )
    # total number of reported males (to be used)
    total_male_report = sum(
        elem.Home for elem in gender_cols_val_count if "Home" in elem.index
    )

    # `usuaries` kpi_3: extreme ages
    user_ages = np.concatenate(
        [df_kpi_1[elem][f"Edat P{i + 1}"] for i, elem in enumerate(users_masks)]
    )

    max_age = int(user_ages.max()) if user_ages.size != 0 else "N/A"
    min_age = int(user_ages.min()) if user_ages.size != 0 else "N/A"

    # note below: could be non-users
    # max_age = int(df_kpi_1_user[
    #     [f"Edat P{i}" for i in range(1,5)]
    # ].max().max())
    # min_age = int(df_kpi_1_user[
    #     [f"Edat P{i}" for i in range(1,5)]
    # ].min().min())

    # user types
    user_types = np.unique(
        np.concatenate(
            [
                df_kpi_1[elem][f"Tipologia P{i + 1}"].unique()
                for i, elem in enumerate(users_masks)
            ]
        )
    )
    # dropdown options: user types
    dd_user_options = [{"label": v, "value": v} for v in user_types]

    # dbc dropdown items (not used in favour of dbc select)
    # dd_user_items = [
    #     dbc.DropdownMenuItem(elem, id=f"my-item-{i}", n_clicks=0)
    #     for i, elem in enumerate(user_types)
    # ]

    # amenity types
    amenity_types = df_passeig_in_dates.EQUIPAMENTS.unique()
    # dropdown options: amenity types
    dd_amenity_options = [
        {"label": v, "value": v} if pd.notnull(v) else {"label": "N/A", "value": "N/A"}
        for v in amenity_types
    ]

    # # warn if missing info by passanger numbers --> save and launch after?
    # app_df["Número de personas"].str.split()
    # app_df[col].isnull()

    # return kpis 1 to 6
    return (
        f"{str(len(df_kpi_1))}",
        f"{str(len(df_kpi_2))}",
        f"{str(kpi_3)}",
        f"{str(kpi_1_user)}",
        (
            f"{total_fema_report/total_gen_report*100:3.1f}%"
            if total_gen_report != 0
            else "N/A"
        ),
        (
            f"{str(max_age)} i {str(min_age)} anys"
            if (type(max_age) != str) and (type(min_age) != str)
            else "N/A"
        ),
        dd_user_options,
        "",
        # csv to json: sharing data within Dash
        df_kpi_1.to_json(orient="split"),
        dd_amenity_options,
        "",
        # csv to json: sharing data within Dash
        df_kpi_2.to_json(orient="split"),
    )


# In[ ]:


@app.callback(
    Output("card-val-1", "children"),
    Output("card-val-2", "children"),
    Output("card-val-3", "children"),
    Output("card-val-4", "children"),
    Output("card-val-5", "children"),
    Output("card-val-6", "children"),
    Output("my-user-dd", "options"),
    Output("my-user-dd", "value"),
    Output("df-aprov-dates", "children"),
    Output("my-amenity-dd", "options"),
    Output("my-amenity-dd", "value"),
    Output("df-cancel-dates", "children"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("btn-close", "n_clicks"),
    State("csv-df", "children"),
    prevent_initial_call=True,
)
def update_kpis(start_date, end_date, _, app_df):

    # file not available or inconsistent dates
    if not app_df or (start_date > end_date):
        return (
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            [],
            "",
            {},
            [],
            "",
            {},
        )
    else:
        return kpis_calc(app_df, start_date, end_date)


# #### Update Cards Body - KPIs `usuaries per Tipología`

# In[ ]:


# filtered aproved `passejades` within dates: user type calculations
def kpis_calc_user_type(df_filtered, user_type):

    # json to dataframe
    df = pd.read_json(df_filtered, orient="split")

    # user type columns filters
    user_type_masks = [df[f"Tipologia P{i}"] == user_type for i in range(1, 5)]

    # user type kpi_1: Total number
    kpi_1_user_type = sum([elem.sum() for elem in user_type_masks])

    # user type kpi_2: Gender percentage
    gender_cols_val_count = [
        df[elem][f"Gènere P{i + 1}"].value_counts(dropna=True)
        for i, elem in enumerate(user_type_masks)
    ]

    # user type: total number of reported genders
    user_type_total_gen = np.concatenate(gender_cols_val_count).sum()
    # user type: total number of reported females
    user_type_total_fema = sum(
        elem.Dona for elem in gender_cols_val_count if "Dona" in elem.index
    )
    # user type: total number of reported males (to be used)
    user_type_total_male = sum(
        elem.Home for elem in gender_cols_val_count if "Home" in elem.index
    )

    # user type kpi_3 and 4: extreme and mean ages
    user_type_ages = np.concatenate(
        [df[elem][f"Edat P{i + 1}"] for i, elem in enumerate(user_type_masks)]
    )

    user_type_max_age = int(user_type_ages.max()) if user_type_ages.size != 0 else "N/A"
    user_type_min_age = int(user_type_ages.min()) if user_type_ages.size != 0 else "N/A"
    user_type_mean_age = user_type_ages.mean() if user_type_ages.size != 0 else "N/A"

    # return user type kpis 1 to 4
    return (
        f"{str(kpi_1_user_type)}",
        (
            f"{user_type_total_fema/user_type_total_gen*100:3.1f}%"
            if user_type_total_gen != 0
            else "N/A"
        ),
        (
            f"{str(user_type_max_age)} i {str(user_type_min_age)} anys"
            if (type(user_type_max_age) != str) and (type(user_type_min_age) != str)
            else "N/A"
        ),
        (
            f"{user_type_mean_age:3.1f} anys"
            if type(user_type_mean_age) != str
            else "N/A"
        ),
    )


# In[ ]:


@app.callback(
    Output("card-val-7", "children"),
    Output("card-val-8", "children"),
    Output("card-val-9", "children"),
    Output("card-val-10", "children"),
    Input("my-user-dd", "value"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    State("df-aprov-dates", "children"),
    prevent_initial_call=True,
)
def update_kpis_user_type(user_type, dummy_start, dummy_end, df_in_date):
    if not df_in_date or user_type == "":
        return "N/A", "N/A", "N/A", "N/A"
    else:
        return kpis_calc_user_type(df_in_date, user_type)


# #### Update Cards Body - KPIs `EQUIPAMENTS`

# In[ ]:


# filtered `passejades` within dates: amenity calculations
def kpis_calc_amenity(df_aprov, df_cancel, amenity):

    # json to dataframe: aproved within dates
    df_aprov = pd.read_json(
        df_aprov, orient="split", convert_dates=["Hora incio", "Hora final"],
    )
    # capture empty as "N/A"
    df_aprov.EQUIPAMENTS.fillna(value="N/A", inplace=True)

    # json to dataframe: cancelled within dates
    df_cancel = pd.read_json(
        df_cancel, orient="split", convert_dates=["Hora incio", "Hora final"],
    )
    # capture empty as "N/A"
    df_cancel.EQUIPAMENTS.fillna(value="N/A", inplace=True)

    # filter amenity aproved
    df_kpi_1 = df_aprov.query("EQUIPAMENTS == @amenity").reset_index(drop=True)

    # # transform amenity aproved datetimes (above by pd.read_json)
    # df_kpi_1.loc[:, "Hora incio"] = pd.to_datetime(
    #     df_kpi_1["Hora incio"], format="%d de %B de %Y %H:%M"
    # )
    # df_kpi_1.loc[:, "Hora final"] = pd.to_datetime(
    #     df_kpi_1["Hora final"], format="%d de %B de %Y %H:%M"
    # )

    # filter amenity cancelled
    df_kpi_2 = df_cancel.query("EQUIPAMENTS == @amenity").reset_index(drop=True)

    # `passejades` in amenity kpi_3: Total of aproved hours
    kpi_3 = (df_kpi_1["Hora final"] - df_kpi_1["Hora incio"]).dt.components.hours.sum()

    # user type columns filters: aproved users in amenity
    users_in_amenity = [
        (df_kpi_1[f"Tipologia P{i}"].fillna("N/A").str.contains("usuària", case=False))
        for i in range(1, 5)
    ]

    # kpi_4: Total number of aproved `usuaries` in amenity
    kpi_4 = sum([elem.sum() for elem in users_in_amenity])

    # kpi_5: Gender percentage of aproved `usuaries` in amenity
    gender_cols_count_amenity = [
        df_kpi_1[elem][f"Gènere P{i + 1}"].value_counts(dropna=True)
        for i, elem in enumerate(users_in_amenity)
    ]

    # total number of reported genders in amenity
    total_gen_amenity = np.concatenate(gender_cols_count_amenity).sum()
    # total number of reported females in amenity
    total_fema_amenity = sum(
        elem.Dona for elem in gender_cols_count_amenity if "Dona" in elem.index
    )
    # total number of reported males in amenity (to be used)
    total_male_amenity = sum(
        elem.Home for elem in gender_cols_count_amenity if "Home" in elem.index
    )

    # kpi_6: mean age of aproved `usuaries` in amenity
    user_ages_amenity = np.concatenate(
        [df_kpi_1[elem][f"Edat P{i + 1}"] for i, elem in enumerate(users_in_amenity)]
    )

    amenity_mean_age = (
        user_ages_amenity.mean() if user_ages_amenity.size != 0 else "N/A"
    )

    # return kpis 1 to 6
    return (
        f"{str(len(df_kpi_1))}",
        f"{str(len(df_kpi_2))}",
        f"{str(kpi_3)}",
        f"{str(kpi_4)}",
        (
            f"{total_fema_amenity/total_gen_amenity*100:3.1f}%"
            if total_gen_amenity != 0
            else "N/A"
        ),
        (f"{amenity_mean_age:3.1f} anys" if type(amenity_mean_age) != str else "N/A"),
    )


# In[ ]:


@app.callback(
    Output("card-val-11", "children"),
    Output("card-val-12", "children"),
    Output("card-val-13", "children"),
    Output("card-val-14", "children"),
    Output("card-val-15", "children"),
    Output("card-val-16", "children"),
    Input("my-amenity-dd", "value"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    State("df-aprov-dates", "children"),
    State("df-cancel-dates", "children"),
    prevent_initial_call=True,
)
def update_kpis_amenity(
    amenity, dummy_start, dummy_end, df_aprov_in_date, df_cancel_in_date
):
    if (not df_aprov_in_date and not df_cancel_in_date) or amenity == "":
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    else:
        return kpis_calc_amenity(df_aprov_in_date, df_cancel_in_date, amenity)


# In[ ]:


# Run app and print out the application URL
app.run_server(mode="external")

