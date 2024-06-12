from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import plotly.express as px
import utils
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64



app = Flask(__name__)

# Sample DataFrame

df = pd.DataFrame()


def get_data(ticker_list):
    #ticker_list = ("AAPL","MSFT","TSLA","NVDA","SPR","HITI","BARK")
    pf, ret, corr = utils.read_table_for_ticker(ticker_list)
    d0_ret = utils.calculate_d1_reletive_ret(pf)
    return d0_ret, corr


def process_input(user_input):
    # This is the function that processes the user input.
    # You can put any logic you want here.
    l = user_input.split(",")
    l = [x.strip().upper() for x in l]
    return l


@app.route('/', methods = ['GET','POST'])
def index():
    if request.method == "POST":
        user_input = request.form['user_input']
        ticker_list = process_input(user_input)
        print("user input:  ", ticker_list, type(ticker_list))
        d0_ret, corr = get_data(ticker_list)
    # Generate Plotly graph
        fig = go.Figure()
        cols = df.columns
        for ticker in cols:
            fig.add_trace(go.Scatter(x=df['Date'], y=df[ticker], mode='lines', name=ticker))
        
        fig.update_layout(
        title='Stock Prices Over Time',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly')
        
    
        # Convert Plotly graph to JSON format
        graph_json = fig.to_json()
    
        # Render template with data for table and graph
        
        ################ okit
        plt.figure(figsize=(15, 7))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f",annot_kws={"size": 16})
        plt.title('Correlation Matrix Heatmap')
        
        # Save the plot to an in-memory file
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
    
    # Convert the BytesIO object to a base64 string
        img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
    else:
        user_input = None
        img_base64 = None
        
    return render_template('index.html', user_input=user_input, plot_url =img_base64 )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100,debug=True)


# @app.route('/' ,methods=['GET'])
# def index():
#     # Generate Plotly graph
#     fig = go.Figure()
#     cols = df.columns
#     for ticker in cols:
#         fig.add_trace(go.Scatter(x=df['Date'], y=d0_ret[ticker], mode='lines', name=ticker))
    
#     fig.update_layout(
#     title='Stock Prices Over Time',
#     xaxis_title='Date',
#     yaxis_title='Price',
#     template='plotly')
    

#     # Convert Plotly graph to JSON format
#     graph_json = fig.to_json()

#     # Render template with data for table and graph
    
#     ################ okit
#     plt.figure(figsize=(15, 7))
#     sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f",annot_kws={"size": 16})
#     plt.title('Correlation Matrix Heatmap')
    
#     # Save the plot to an in-memory file
#     img = io.BytesIO()
#     plt.savefig(img, format='png')
#     img.seek(0)
#     plt.close()
    
#     # Convert the BytesIO object to a base64 string
#     img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
    
#     return render_template('index.html', img_data=img_base64, graph_json=graph_json)



# @app.route('/', methods=['POST'])
# def submit():
#     user_input = request.form.get('user_input')
#     processed_result = process_input(user_input)
#     return f'You entered: {user_input} <br> {processed_result}'

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)