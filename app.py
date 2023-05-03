import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import os
import tempfile
import base64
import io

Clean_text=[]

from NLP_Judicial import Cleaned_Pdf_Text,store_to_Pdf

app = dash.Dash(__name__)



sidebar = html.Div(
    id="sidebar",
    children=[
        html.P("This is a sidebar")
    ]
)

# Linking the external CSS file
external_stylesheets = ['https://example.com/style.css']


# Defining the layout of the app
# Defining the layout of the app
app.layout = html.Div([
    # Header component
    html.Header([
        # html.H1('My Dashboard')
    ]),
    
    # Content Section
    html.Div(
        id="main-content",
        children=[
            # sidebar
            html.Div(
                id="instructions-sidebar",
                children=[
                    html.H2("INSTRUCTIONS"),
                    html.P("This project is primarily focused on cleaning PDF files, which involves several tasks such as removing irrelevant data, headers, citations, and punctuation. Additionally, formatting errors will be corrected, and the file will be optimized for better performance. The aim is to provide a clean, organized, and error-free PDF file that can be used for various purposes."),
                    html.P("Regular maintenance and updates are necessary to keep the project current with new rules or file additions, ensuring accurate and efficient voice translations that meet the client's needs"),
                    html.Ul([
                        html.Li("Upload the messy PDF file to the application."),
                        html.Li("Click on the Start button to initiate the cleaning process"),
                        html.Li("Lorem Ipsum is simply dummy text of the"),
                        html.Li("Once the cleaning process is complete, download the clean file by clicking on the \"Download\" button."),
                        html.P(""),

                    ])
                ]
            ),
            
            # File upload section
            html.Div(
                className="upload-section",
                children=[
                    html.Div(
                        className="attachment-section",
                        children=[
                            html.H3("Attachments"),
                            dcc.Upload(
                                id="upload-data",
                                children=[
                                    html.Div(
                                        className="drag-upload",
                                        children=[
                                            html.Img(src='/assets/icons/upload.svg'),
                                        # html.P("Drag file is here or") + html.A("Upload")
                                        html.Div([
                                                html.Span("Drag file is here or  "),
                                                html.A("Upload")
                                                ])
                                        ]
                                    )
                                ],
                                multiple=False,
                                accept='.pdf'
                            ),
                            html.Div(
                                className="file-progress",
                                children=[
                                    html.Div(id="output-file"),
                                    html.Button("Start", id="process-file", disabled=True),
                                ]),
                        ]
                    ),
                    dcc.Loading(
                        id="loading",
                        # New section
                        children=[
                            html.Div(
                                className="documents-section",
                                children=[
                                    html.Div(
                                        className="document-heading",
                                        children=[
                                            html.H3("Documents"),
                                            # Download button and link section
                                            html.Button('Download', id='btn_download'),
                                            dcc.Download(id='download_pdf'),
                                        ]),
                                        html.Div(id="output"),
                                        #This is For showing the Icon
                                        html.Div(id='image-container')
                                        # html.Button("Download", id="btn_downlode", disabled=True)
                                ]
                            )
                        ],
                    ),
                    # Status of download section
                    html.Div(id="status_of_download"),
                ]
            ),
        ]),
])

# Call back for the File name

@app.callback(Output("output-file", "children"),
              Output("process-file", "disabled"),
              Input("upload-data", "filename"),
              State("upload-data", "contents"))
def update_output(filename, contents):
     if filename is not None:
            print(filename)
            return html.P("{}".format(filename)), False
     else:
        return html.P("No file uploaded yet"), True


# Call back for the Cleaning PDF

@app.callback(Output("output", "children"),
            #   Output("download-link", "disabled"),
              Input("process-file", "n_clicks"),
              State("upload-data", "filename"),
              State("upload-data", "contents"),

              prevent_initial_call=True)
def process_file(n_clicks, filename,contents):
    if n_clicks is not None and filename is not None:

        # clean_text=Cleaned_Pdf_Text(filename)
        contents = contents.encode('utf8').split(b';base64,')[1]
        # Save the bytes to a temporary file
        with open('tmp.pdf', 'wb') as f:
            f.write(base64.decodebytes(contents))
        # Extract the text from the temporary file
        try:
            text = Cleaned_Pdf_Text('tmp.pdf')
            store_to_Pdf(text,"Clean__file.txt")
        except TypeError as e:
            # code to handle the error
            print("An error occurred:", str(e))
            return "There is some Error in the file which is "+str(e)
        
        global Clean_text
        Clean_text=text


        return "File processed successfully: File name is "+filename,False
    else:
        return "Not File selected",True

    

#Call back for downloading the PDF

@app.callback(Output('download_pdf', 'data'),
              State("upload-data", "filename"),
              [Input('btn_download', 'n_clicks')],
              prevent_initial_call=False)

def download_pdf(file_name,n_clicks):
    if file_name and n_clicks is not None:
        print(file_name)
        file_path = os.path.join(os.getcwd(),"Clean__file.pdf")  # assuming file is named 'example.pdf'
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'rb') as f:
            pdf_bytes = f.read()
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        return dcc.send_bytes(pdf_bytes, filename="Clean__"+file_name+'output.pdf', mimetype='application/pdf')
    


@app.callback(
    Output('image-container', 'children'),
    State("upload-data", "filename"),
    Input("process-file", "n_clicks")
)
def update_image(file_name,click):

    print(click)
    if file_name is None:
        return html.Img(src='/assets/icons/docs.svg')
    else:
        return html.Div('')

if __name__ == '__main__':
    app.run_server(debug=True,port=8080)