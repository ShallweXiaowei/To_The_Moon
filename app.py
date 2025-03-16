from flask import Flask, render_template, request, session, redirect, url_for,jsonify
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
matplotlib.use('agg')



app = Flask(__name__)

# Sample DataFrame

df = pd.DataFrame()
ind_table, ind_dic = utils.get_industry_dic()
cik_map = utils.read_table_all("CIK_map", "CIK_map")
cik_map.index = cik_map["ticker"]
entity_name_dic = cik_map.to_dict()["entity"]



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
    sectors = ind_dic.keys()

    user_input, dropdown1, dropdown2 = None,None,None
    if request.method == "POST":
        
        if 'user_input' in request.form:
            selected =  request.form.get('user_input')
            selected = process_input(selected)
            
        elif 'dropdown1' in request.form:
            dropdown1 = request.form.get('dropdown1')
            dropdown2 = request.form.get('dropdown2')
            selected = ind_dic[dropdown1][dropdown2]
        
        print("user input:  ", selected, type(selected))
        d0_ret, corr = get_data(selected)
        #d0_ret.index = d0_ret.index.map(lambda x: x.split(" ")[0])
        
        fig = go.Figure()

        # Add traces for each stock
        for stock in d0_ret.columns:
            fig.add_trace(go.Scatter(x=d0_ret.index, y=d0_ret[stock], mode='lines', name=stock))
        
        # Customize layout
        fig.update_layout(
            title='Stock Prices',
            yaxis_title='Return',
            xaxis = dict(
                title = "Date",
                rangeslider = dict(visible = True),
                type = 'date'
                ),
            showlegend=True,
            height = 700
        )
        
        # Convert Plotly figure to JSON for JavaScript embedding
        ret_base = fig.to_html(full_html=False)

        # Render template with data for table and graph
        
        ################ okit
        plt.figure(figsize=(15, 7))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f",annot_kws={"size": 16})
        plt.title('Correlation Matrix Heatmap')
        
        # Save the plot to an in-memory file
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(1)
        plt.close()
    
    # Convert the BytesIO object to a base64 string
        img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
        return render_template('index.html', plot_div = ret_base, user_input=user_input, 
                               plot_url =img_base64,dropdown1_options = sectors,
                               selected = ",".join(selected))

    else:
        return render_template('index.html',dropdown1_options = sectors)

@app.route('/get_sub_options', methods=['POST'])
def get_sub_options():
    selected_option = request.json.get('selected_option')
    sub_options  = list(ind_dic[selected_option].keys())
    return jsonify(sub_options)


@app.route('/screener',methods = ['GET','POST'])
def screener():
    table_html = ind_table.to_html(classes='table table-striped', index=False)
    sectors = ind_dic.keys()
    selected = "select some text here"
    
    if request.method == "POST":
        dropdown1 = request.form.get('dropdown1')
        dropdown2 = request.form.get('dropdown2')
        selected = ind_dic[dropdown1][dropdown2]        
        entity_df = pd.DataFrame(index = selected)
        entity_df.loc[:,"entity name"] = entity_df.index.map(entity_name_dic)
        df_html = entity_df.to_html(classes='table table-striped', index=True)
        
        return render_template('screener.html',message = ",".join(selected),table = df_html, dropdown1_options = sectors)
    
    else:
        return render_template('screener.html', dropdown1_options = sectors)


@app.route('/submit', methods=['POST'])
def submit():
    text = request.form.get('textbox')
    return f'You entered: {text}'


''' 
self index forming backend functions

'''

@app.route('/self_index')
def self_index():
    return render_template('self_index.html')

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



@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    # 获取请求参数
    industries = request.args.get('industries')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 验证行业参数
    if not industries:
        return jsonify({'error': '未选择行业'}), 400

    industry_list = industries.split(',')

    # 获取股票代码
    stock_codes = {}
    for sector, industries_dict in ind_dic.items():
        for industry in industry_list:
            if industry in industries_dict:
                stock_codes[industry] = industries_dict[industry]

    if not stock_codes:
        return jsonify({'error': '未找到股票数据'}), 404

    # 计算收益率
    mean_dict = {}
    for k, v in stock_codes.items():
        mean_dict[k] = index_forming.get_d0_return(v)

    # 转换为 DataFrame
    mean_df = pd.DataFrame(mean_dict)

    # 根据时间范围过滤数据
    if start_date and end_date:
        mean_df = mean_df.loc[start_date:end_date]

    # 设置索引名称并转换为 JSON
    mean_df.index.name = 'timestamps'
    json_data = mean_df.reset_index().to_json(orient='records', date_format='iso')

    return jsonify(json.loads(json_data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100,debug=True)
    
    
    
