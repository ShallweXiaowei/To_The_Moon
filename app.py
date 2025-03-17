from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pandas as pd
import plotly.express as px
import utils
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import index_forming
import json
import matplotlib
import math
matplotlib.use('agg')

app = Flask(__name__)

# Sample DataFrame
df = pd.DataFrame()
ind_table, ind_dic = utils.get_industry_dic()
cik_map = utils.read_table_all("CIK_map", "CIK_map")
cik_map.index = cik_map["ticker"]
entity_name_dic = cik_map.to_dict()["entity"]


###self index dictionary
self_index_list = pd.read_csv('self_index_list.csv')
self_index_dict = self_index_list.to_dict()
self_index_columns = self_index_dict.keys()


def get_data(ticker_list):
    pf, ret, corr = utils.read_table_for_ticker(ticker_list)
    d0_ret = utils.calculate_d1_reletive_ret(pf)
    return d0_ret, corr

def process_input(user_input):
    l = user_input.split(",")
    l = [x.strip().upper() for x in l]
    return l

@app.route('/', methods=['GET', 'POST'])
def index():
    sectors = ind_dic.keys()
    user_input, dropdown1, dropdown2 = None, None, None
    if request.method == "POST":
        if 'user_input' in request.form:
            selected = request.form.get('user_input')
            selected = process_input(selected)
        elif 'dropdown1' in request.form:
            dropdown1 = request.form.get('dropdown1')
            dropdown2 = request.form.get('dropdown2')
            selected = ind_dic[dropdown1][dropdown2]
        print("user input:  ", selected, type(selected))
        d0_ret, corr = get_data(selected)
        fig = go.Figure()
        for stock in d0_ret.columns:
            fig.add_trace(go.Scatter(x=d0_ret.index, y=d0_ret[stock], mode='lines', name=stock))
        fig.update_layout(title='Stock Prices', xaxis_title='Date', yaxis_title='Price ($)', showlegend=True, height=700)
        ret_base = fig.to_html(full_html=False)
        plt.figure(figsize=(15, 7))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", annot_kws={"size": 16})
        plt.title('Correlation Matrix Heatmap')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
        return render_template('index.html', plot_div=ret_base, user_input=user_input, plot_url=img_base64, dropdown1_options=sectors, selected=",".join(selected))
    else:
        return render_template('index.html', dropdown1_options=sectors)

@app.route('/get_sub_options', methods=['POST'])
def get_sub_options():
    selected_option = request.json.get('selected_option')
    sub_options = list(ind_dic[selected_option].keys())
    return jsonify(sub_options)

@app.route('/screener', methods=['GET', 'POST'])
def screener():
    table_html = ind_table.to_html(classes='table table-striped', index=False)
    sectors = ind_dic.keys()
    selected = "select some text here"
    if request.method == "POST":
        dropdown1 = request.form.get('dropdown1')
        dropdown2 = request.form.get('dropdown2')
        selected = ind_dic[dropdown1][dropdown2]
        entity_df = pd.DataFrame(index=selected)
        entity_df.loc[:, "entity name"] = entity_df.index.map(entity_name_dic)
        df_html = entity_df.to_html(classes='table table-striped', index=True)
        return render_template('screener.html', message=",".join(selected), table=df_html, dropdown1_options=sectors)
    else:
        return render_template('screener.html', dropdown1_options=sectors)

@app.route('/self_index')
def self_index():
    return render_template('self_index.html')


### 获取自定义index
@app.route('/api/indexes')
def get_indexes():
    return jsonify(list(self_index_columns))


# API 1：获取所有 sector
@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    return jsonify(list(ind_dic.keys()))

# API 2：获取某 sector 下的 industry
@app.route('/api/industries/<sector>', methods=['GET'])
def get_industries(sector):
    if sector not in ind_dic:
        return jsonify({'error': 'Sector not found'}), 404
    return jsonify(list(ind_dic[sector].keys()))

# API 3：获取股票数据，支持时间范围
@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    industries = request.args.get('industries')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    tickers = request.args.get('tickers', '').split(',')
    indexes = request.args.get('indexes', '').split(',')
    
    mean_df = pd.DataFrame()
    
    if industries:
        #return jsonify({'error': 'No industries selected'}), 400

        industry_list = industries.split(',')

        stock_codes = {}
        for sector, industries_dict in ind_dic.items():
            for industry in industry_list:
                if industry in industries_dict:
                    stock_codes[industry] = industries_dict[industry]

        if not stock_codes:
            return jsonify({'error': 'No stocks found'}), 404

        mean_dict = {}
        for k, v in stock_codes.items():
            mean_dict[k] = index_forming.get_d0_return(v,start_date,end_date)
            print("questing data-----start date: %s"%start_date)

            
            
        industry_mean = pd.DataFrame(mean_dict)
        mean_df = pd.concat([mean_df, industry_mean],axis = 1)


    #### check if user input tickers
    if tickers != [""]:
        print(tickers)
        tickers = [ticker.strip() for ticker in tickers]
        individual_ret = index_forming.get_d0_return(tickers,start_date,end_date,mean = False)
        mean_df = pd.concat([mean_df, individual_ret],axis = 1)
        
    #### check if self index is selected:
    if indexes != [""]:
        for indexx in indexes:
            print(indexx)
            tickers = list(self_index_dict[indexx].values())
            print(tickers)
            tickers = [x for x in tickers if x]
            tickers = [item for item in tickers if not isinstance(item, float) or not math.isnan(item)]
            index_ret = index_forming.get_d0_return(tickers,start_date,end_date,mean = True)
            index_ret.name = indexx
            mean_df = pd.concat([mean_df, index_ret],axis = 1)
        

    #print(mean_df)
    mean_df.to_csv("mean_df.csv")
    mean_df.index.name = 'timestamps'
    json_data = mean_df.reset_index().to_json(orient='records', date_format='iso')
    return jsonify(json.loads(json_data))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)