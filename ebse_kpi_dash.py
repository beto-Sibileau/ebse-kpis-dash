#!/usr/bin/env python
# coding: utf-8

# ### Intro

# In[ ]:


# python modules
import base64
import csv
from dash import Dash, dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import io
import numpy as np
import pandas as pd
import re
import tempfile


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
                        html.Div(
                            id="validation-state",
                            className="output-validate-state",
                            style={"color": "RoyalBlue", "textAlign": "center",},
                        ),
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
            dbc.Col(create_card("KPI1: Quantitat de persones", 4), width="auto"),
            dbc.Col(create_card("KPI2: Percentatge de dones", 5), width="auto"),
            dbc.Col(
                create_card("KPI3: Persones més grans i més petites", 6), width="auto"
            ),
        ],
        justify="evenly",
    ),
    fluid=True,
)

# In[ ]:

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
                dbc.Col(create_card("KPI4: Quantitat de persones", 14), width="auto"),
                dbc.Col(create_card("KPI5: Percentatge de dones", 15), width="auto"),
                dbc.Col(
                    create_card("KPI6: Mitjana d’edat de persones", 16), width="auto"
                ),
            ],
            justify="evenly",
        ),
    ],
    fluid=True,
)


# In[ ]:


# dbc select: volunteers
dd_volunteer = dbc.Select(id="my-volunteer-dd", options=[], value="",)

# dbc button: download volunteers data
bt_dwd = dbc.Button(
    html.P(
        ["Click to Download ", html.Code("csv"), " File"],
        style={"margin-top": "12px", "fontWeight": "bold",},
    ),
    id="btn-dwd",
    class_name="me-1",
    outline=True,
    color="info",
)

# dbc dropdown and one card and download button below: volunteers
card_row_volunteer = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                "Select Volunteer",
                                style={
                                    "fontWeight": "bold",
                                    "fontSize": "18px",
                                    "marginBottom": "10px",
                                    "textAlign": "center",
                                },
                            ),
                            dd_volunteer,
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
                dbc.Col(create_card("KPI1: Quantitat d’hores", 17), width="auto"),
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                "Full Volunteers List",
                                style={
                                    "fontWeight": "bold",
                                    "fontSize": "18px",
                                    "marginBottom": "10px",
                                    "textAlign": "center",
                                },
                            ),
                            bt_dwd,
                            dcc.Download(id="volunteer-dwd"),
                        ]
                    ),
                    width="auto",
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
app = Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, fontawesome_stylesheet]
)

# to deploy using WSGI server
server = app.server
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
                [amenity_row_type], style={"paddingTop": "0", "margin-bottom": "0",},
            ),
            id="loading-kpis-amenity",
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
        # div card row: volunteers
        dcc.Loading(
            children=html.Div(
                [card_row_volunteer],
                style={"paddingTop": "0", "margin-bottom": "40px",},
            ),
            id="loading-kpi-volunteer",
            type="circle",
            fullscreen=True,
        ),
        # dbc Modal: output msg from load button - wraped by Spinner
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
        # dbc Modal: output msg from download button - wraped by Spinner
        dcc.Loading(
            children=dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Download Message"), close_button=False
                    ),
                    dbc.ModalBody(id="my-modal-body-dwd"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="btn-close-dwd", class_name="ms-auto")
                    ),
                ],
                id="my-modal-dwd",
                is_open=False,
                keyboard=False,
                backdrop="static",
                scrollable=True,
                centered=True,
            ),
            id="loading-modal-dwd",
            type="circle",
            fullscreen=True,
        ),
        # dbc Modal: output msg from validation button - wraped by Spinner
        dcc.Loading(
            children=dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Validation Message"), close_button=False
                    ),
                    dbc.ModalBody(id="my-modal-body-val"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="btn-close-val", class_name="ms-auto")
                    ),
                ],
                id="my-modal-val",
                is_open=False,
                keyboard=False,
                backdrop="static",
                scrollable=True,
                size="lg",
                centered=True,
            ),
            id="loading-modal-val",
            type="circle",
            fullscreen=True,
        ),
        # hidden div: ouput msg from load button
        html.Div(id="output-data-upload", style={"display": "none"}),
        # hidden div: ouput msg download button
        html.Div(id="output-data-dwd", style={"display": "none"}),
        # hidden div: ouput msg validation button
        html.Div(id="output-data-val", style={"display": "none"}),
        # hidden div: share csv-df in Dash
        html.Div(id="csv-df", style={"display": "none"}),
        # hidden div: share df-in-dates in Dash
        html.Div(id="df-in-dates", style={"display": "none"}),
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


# #### Trigger Validation Printing state

# In[ ]:


# showing Validating state trick?
@app.callback(
    Output("validation-state", "children"),
    Input("btn-val", "n_clicks"),
    prevent_initial_call=True,
)
def validate_triggers_spinner(_):
    return None


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
        "Nombre del cliente",
        "Voluntari/a",
        "Servei",
        "Hora incio",
        "Hora final",
        "Número de personas",
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
    miss_col = [i for (i, v) in zip(col_names_2_check, col_check) if not v]

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


# #### Return Download message in *Bootstrap Modal*

# In[ ]:


@app.callback(
    Output("my-modal-body-dwd", "children"),
    Output("my-modal-dwd", "is_open"),
    Input("output-data-dwd", "children"),
    Input("btn-close-dwd", "n_clicks"),
    State("my-modal-dwd", "is_open"),
    prevent_initial_call=True,
)
def update_modal_dwd(msg_dwd, _, is_open_dwd):

    # identify callback context
    triger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    # specify action by trigger
    if "data-dwd" in triger_id:
        return (
            html.P(msg_dwd),
            not is_open_dwd,
        )
    else:
        # button close
        return {}, not is_open_dwd


# #### Return Validation message in *Bootstrap Modal*

# In[ ]:


@app.callback(
    Output("my-modal-body-val", "children"),
    Output("my-modal-val", "is_open"),
    Input("output-data-val", "children"),
    Input("btn-close-val", "n_clicks"),
    State("my-modal-val", "is_open"),
    prevent_initial_call=True,
)
def update_modal_val(msg_val, _, is_open_val):

    # identify callback context
    triger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    # specify action by trigger
    if "data-val" in triger_id:
        return (
            dbc.Container(msg_val),
            not is_open_val,
        )
    else:
        # button close
        return {}, not is_open_val


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

    # filter `Hora incio` within dates
    query_dates = [
        "`Hora incio` >= @ini_date",
        "`Hora incio` <= @end_date",
    ]
    df_in_dates = df.query("&".join(query_dates)).reset_index(drop=True)

    # no entry between dates: return empty
    if df_in_dates.empty:
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
            [],
            "",
            {},
        )

    # eliminate duplicated `Cita ID` (keep first)
    dupli_in_dates = df_in_dates.duplicated(subset="Cita ID", keep="first",)
    df_in_dates.drop(
        df_in_dates[dupli_in_dates].index, inplace=True,
    )

    # filter `passejades` within dates (AND exclude maintenance key words)
    servei_key = "Servei.str.contains('tricicle', case=False)"
    maintain_key = "Servei.str.contains('trasllat|manteniment', case=False)"
    df_passeig_in_dates = df_in_dates.query(
        f"{servei_key}&~{maintain_key}", engine="python",
    ).reset_index(drop=True)

    # client names: `Nombre del cliente`
    client_names = df_passeig_in_dates["Nombre del cliente"].dropna().unique()
    # filter amenities: starting digit/s and point
    amenity_types = [x for x in client_names if re.findall(r"^\d+", x)]

    # dropdown options: amenity types from `Nombre del cliente`
    dd_amenity_options = [
        {"label": " ".join(v.split()[1:]), "value": v}
        # if pd.notnull(v)
        # else {"label": "N/A", "value": "N/A"}
        for v in amenity_types
    ]

    # add N/A if empty clients
    if df_passeig_in_dates["Nombre del cliente"].isnull().any():
        dd_amenity_options.append({"label": "N/A", "value": "N/A"})

    # replace client names as `Usuàries Particulars` if any
    if len(amenity_types) < len(client_names):
        # check if `Usuàries Particulars` in amenity_types
        filter_particulars = (
            pd.Series(amenity_types).str.contains("usuàries particulars", case=False)
            if len(amenity_types) > 0
            else np.array([False])
        )
        if filter_particulars.any():
            private_user = pd.Series(amenity_types)[filter_particulars].values[0]
        else:
            private_user = "Usuàries Particulars"
            dd_amenity_options.append({"label": private_user, "value": private_user})

        # client names to replace
        clients_map = {
            k: private_user
            for k in np.setdiff1d(client_names, amenity_types, assume_unique=True)
        }
        df_passeig_in_dates.replace(clients_map, inplace=True, regex=False)

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

    # kpi_1: Total number of people
    kpi_1_people = pd.to_numeric(
        df_kpi_1["Número de personas"].str.split().str[1], errors="coerce"
    ).sum()

    # kpi_2: Gender percentage (all people)
    gender_cols_val_count = [
        df_kpi_1[f"Gènere P{i}"].value_counts(dropna=True) for i in range(1, 5)
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

    # kpi_3: extreme ages (all people)
    people_ages = np.concatenate([df_kpi_1[f"Edat P{i}"].dropna() for i in range(1, 5)])

    max_age = int(people_ages.max()) if people_ages.size != 0 else "N/A"
    min_age = int(people_ages.min()) if people_ages.size != 0 else "N/A"

    # people types
    people_types = np.unique(
        np.concatenate(
            [df_kpi_1[f"Tipologia P{i}"].dropna().unique() for i in range(1, 5)]
        )
    )

    # dropdown options: people types
    dd_people_options = [{"label": v, "value": v} for v in people_types]

    # filter aproved for volunteers list
    df_volunteer_dates = df_in_dates.query(query_kpi_1, engine="python",).reset_index(
        drop=True
    )
    # replace names if empty: "N/A"
    df_volunteer_dates["Voluntari/a"].fillna(value="N/A", inplace=True)

    # add column hours for volunteers list
    df_volunteer_dates["Hours"] = (
        df_volunteer_dates["Hora final"] - df_volunteer_dates["Hora incio"]
    ).dt.components.hours + (
        df_volunteer_dates["Hora final"] - df_volunteer_dates["Hora incio"]
    ).dt.components.minutes / 60
    # aggregate df_volunteer_dates for volunteers list
    df_volunteer_list = (
        df_volunteer_dates.groupby("Voluntari/a", sort=False)
        .agg({"Hours": "sum", "Servei": "last", "Hora incio": "last",})
        .reset_index()
        .sort_values("Hours", ascending=False, ignore_index=True)
        .rename(columns={"Servei": "Last Servei", "Hora incio": "Last Date"})
    )
    df_volunteer_list.loc[:, "Last Date"] = df_volunteer_list["Last Date"].dt.strftime(
        "%Y-%m-%d"
    )
    df_volunteer_list.loc[:, "Voluntari/a"] = (
        df_volunteer_list["Voluntari/a"]
        .str.replace(r"^\d+.", "", regex=True)
        .str.strip()
    )

    # volunteers: `Voluntari/a`
    volunteer_names = df_volunteer_list["Voluntari/a"].sort_values().values
    # dropdown options: volunteer names
    dd_volunteer_options = [{"label": v, "value": v} for v in volunteer_names]

    # return kpis 1 to 6
    return (
        f"{str(len(df_kpi_1))}",
        f"{str(len(df_kpi_2))}",
        f"{str(kpi_3)}",
        f"{str(kpi_1_people)}",
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
        dd_people_options,
        "",
        # csv to json: sharing data within Dash
        df_kpi_1.to_json(orient="split"),
        dd_amenity_options,
        "",
        # csv to json: sharing data within Dash
        df_kpi_2.to_json(orient="split"),
        dd_volunteer_options,
        "",
        # csv to json: sharing data within Dash
        df_volunteer_list.to_json(orient="split"),
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
    Output("my-volunteer-dd", "options"),
    Output("my-volunteer-dd", "value"),
    Output("df-in-dates", "children"),
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
        [df[elem][f"Edat P{i + 1}"].dropna() for i, elem in enumerate(user_type_masks)]
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
    State("df-aprov-dates", "children"),
    prevent_initial_call=True,
)
def update_kpis_user_type(user_type, df_in_date):
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
    df_aprov["Nombre del cliente"].fillna(value="N/A", inplace=True)

    # json to dataframe: cancelled within dates
    df_cancel = pd.read_json(
        df_cancel, orient="split", convert_dates=["Hora incio", "Hora final"],
    )
    # capture empty as "N/A"
    df_cancel["Nombre del cliente"].fillna(value="N/A", inplace=True)

    # filter amenity aproved
    df_kpi_1 = df_aprov.query("`Nombre del cliente` == @amenity").reset_index(drop=True)

    # filter amenity cancelled
    df_kpi_2 = df_cancel.query("`Nombre del cliente` == @amenity").reset_index(
        drop=True
    )

    # `passejades` in amenity kpi_3: Total of aproved hours
    kpi_3 = (df_kpi_1["Hora final"] - df_kpi_1["Hora incio"]).dt.components.hours.sum()

    # kpi_4: Total number of people in amenity
    kpi_4 = pd.to_numeric(
        df_kpi_1["Número de personas"].str.split().str[1], errors="coerce"
    ).sum()

    # kpi_5: Gender percentage of aproved people in amenity
    gender_cols_count_amenity = [
        df_kpi_1[f"Gènere P{i}"].value_counts(dropna=True) for i in range(1, 5)
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

    # kpi_6: mean age of aproved people in amenity
    people_ages_amenity = np.concatenate(
        [df_kpi_1[f"Edat P{i}"].dropna() for i in range(1, 5)]
    )

    amenity_mean_age = (
        people_ages_amenity.mean() if people_ages_amenity.size != 0 else "N/A"
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
    State("df-aprov-dates", "children"),
    State("df-cancel-dates", "children"),
    prevent_initial_call=True,
)
def update_kpis_amenity(amenity, df_aprov_in_date, df_cancel_in_date):
    if (not df_aprov_in_date and not df_cancel_in_date) or amenity == "":
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    else:
        return kpis_calc_amenity(df_aprov_in_date, df_cancel_in_date, amenity)


# #### Update Cards Body - KPI `Totals per persona voluntària`

# In[ ]:


# filter aggregated volunteer list within dates
def kpi_calc_volunteer(df_volunteer_list, volunteer):

    # json to dataframe
    df = pd.read_json(df_volunteer_list, orient="split")

    # user type columns filters
    kpi_1 = df.query("`Voluntari/a` == @volunteer").Hours.values[0]

    # volunteer kpi
    return f"{str(kpi_1)}"


# In[ ]:


@app.callback(
    Output("card-val-17", "children"),
    Input("my-volunteer-dd", "value"),
    State("df-in-dates", "children"),
    prevent_initial_call=True,
)
def update_kpi_volunteers(volunteer, df_volunteer_dates):
    if not df_volunteer_dates or volunteer == "":
        return "N/A"
    else:
        return kpi_calc_volunteer(df_volunteer_dates, volunteer)


# #### Download Volunteers `csv` File

# In[ ]:


# callback download conversion
@app.callback(
    Output("output-data-dwd", "children"),
    Output("volunteer-dwd", "data"),
    Input("btn-dwd", "n_clicks"),
    State("df-in-dates", "children"),
    prevent_initial_call=True,
)
def download_volunteers_list(_, df_volunteer_dates):
    if not df_volunteer_dates:
        return (
            [
                html.Strong("No Data"),
                html.Br(),
                "1) Please Upload ",
                html.Code("csv"),
                " File",
                html.Br(),
                "2) Please Verify ",
                html.Em("Selected Dates"),
            ],
            None,
        )
    else:
        df = pd.read_json(df_volunteer_dates, orient="split")
        df_temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df_temp_file.flush()
        df.to_csv(
            df_temp_file.name,
            index=False,
            encoding="utf-8-sig",
            quoting=csv.QUOTE_NONNUMERIC,
        )
        return (
            [
                html.Strong("Data Downloaded"),
                html.Br(),
                "File ",
                html.Code("totals_voluntaries.csv"),
            ],
            # dcc.send_data_frame --> encoding not working apparently
            # use instead dcc.send_file
            dcc.send_file(df_temp_file.name, filename="totals_voluntaries.csv"),
        )


# #### Validate Appointments `csv` File: aproved `passejades` missing information

# In[ ]:


# callback validation
@app.callback(
    Output("output-data-val", "children"),
    Input("btn-val", "n_clicks"),
    State("df-aprov-dates", "children"),
    prevent_initial_call=True,
)
def validate_missing(_, df_aprov_in_date):
    if not df_aprov_in_date:

        return [
            html.P(
                [
                    html.Strong("No Data"),
                    html.Br(),
                    "1) Please Upload ",
                    html.Code("csv"),
                    " File",
                    html.Br(),
                    "2) Please Verify ",
                    html.Em("Selected Dates"),
                ]
            )
        ]

    else:

        df = pd.read_json(
            df_aprov_in_date, orient="split", convert_dates=["Hora incio"]
        )
        # split number of aproved users
        df.loc[:, "Número de personas"] = pd.to_numeric(
            df["Número de personas"].str.split().str[1], errors="coerce",
        )

        # users information columns
        user_info_cols = [
            [f"Tipologia P{i}", f"Gènere P{i}", f"Edat P{i}",] for i in range(1, 5)
        ]
        # filter nulls matrix
        null_matrix = np.array(
            [df[elem].notnull().all(axis="columns").values for elem in user_info_cols]
        )

        # # filter incomplete accordingly --> below, inconsistent preferred
        # is_not_complete = [
        #     not null_matrix[:elem, i].all()
        #     for i, elem in enumerate(df["Número de personas"].values)
        # ]

        # filter inconsistent accordingly
        is_not_consistent = [
            null_matrix[:, i].sum() != elem
            for i, elem in enumerate(df["Número de personas"].values)
        ]

        # display columns appended
        user_info_cols.insert(
            0, ["Cita ID", "Servei", "Hora incio", "Número de personas"]
        )
        df_not_complete = df[is_not_consistent][
            np.concatenate(user_info_cols)
        ].reset_index(drop=True)

        if df_not_complete.empty:

            return [
                html.P(
                    [
                        html.Strong("Successfully Validated"),
                        html.Br(),
                        "All ",
                        html.Code("passejades aprovades"),
                        " are ",
                        html.Em("fully completed"),
                    ]
                )
            ]

        else:

            return [
                html.P(
                    [
                        html.Strong("Missing Information"),
                        html.Br(),
                        "Check ",
                        html.Code("Cita ID"),
                        html.Em(" below:"),
                        html.Br(),
                        dbc.Table.from_dataframe(
                            df_not_complete,
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True,
                            size="sm",
                            color="warning",
                        ),
                    ]
                )
            ]


# In[ ]:


if __name__ == "__main__":
    app.run_server(debug=True)
