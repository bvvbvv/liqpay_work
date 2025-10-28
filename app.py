## Создано на основе LiqPay_design/app_test_loc.py
#!/usr/local/bin/pay_app/bin/python3
####!/usr/bin/python3
import sys 
import site
import os, re
import platform
os_name=platform.system()
if os_name == 'Windows':
    debug = 1
    is_windows = True
    sys.path.insert(0,"/d:/Python Project/LiqPay_work")
else:
    debug = 0
    is_windows = False  
    site.addsitedir("/usr/local/bin/pay_app/lib/python3.12/site-packages")
    sys.path.insert(0,"/var/www/pay.sns.net.ua/public_html")
    
    
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask,render_template,request, redirect, flash, jsonify
from liqpay import LiqPay
#from liqpay import liqpay
import base64
import json
from liqpay_config_loc import LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY,DB
import debugpy
from utility4sns import get_os_param, check_contract, make_short_name, insert_after_find_contract, get_after_find_contract,  update_payments_aquire, check_pay_status, send2sns_transaction, get_db_connection
# Конфигурация публичного URL вашего приложения ngrok
#debug,is_windows, ngrok= get_os_param()
if (is_windows ):
    PUBLIC_BASE_URL = "https://nikole-populational-commensurately.ngrok-free.dev"
else:
    PUBLIC_BASE_URL = "https://pay.sns.net.ua"


app = Flask(__name__)
if(debug):print("!!! LiqPay_TEST app started $$$")
    
@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/about')
def about():
    return render_template('about.html', title="About Us")

@app.route('/price')
def price():
    return render_template('price.html', title="Price")

@app.route('/send_contact')
def send_contact():
    return render_template('error.html', title="Send Error")

@app.route('/security_politics')
def security_politics(): #только полное имя файла, без расширения !!
    return render_template('security_politics.html')

@app.route('/oferta')
def oferta(): #только полное имя фвайла !!
    return render_template('oferta.html')

@app.route('/error')
def error(): #только полное имя фвайла !!
    return render_template('error.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        msg = request.form.get('message')
        # Здесь можно сохранять сообщение или отправлять email
        return render_template('success.html', message="Message sent. Thank you!")
    return render_template('contact.html', title="Contact")

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        contract = request.form.get('contract')
        amount = request.form.get('amount')
        # Простая валидация: contract - цифры, amount - положительное число
        try:
            if not contract or not contract.strip().isdigit():
                raise ValueError("Помилка: Невірний номер договору")
            a = float(amount)
            if a <= 0:
                raise ValueError("Помилка: Невірна сума платежу")
            # Успешный результат
            return render_template('success.html', message=f"Payment for contract {contract} of €{a:.2f} accepted.")
        except Exception as e:
            return render_template('error.html', message=str(e))
    return render_template('form.html', title="Connect")

@app.route('/pay_check_contract', methods=["POST"])
def pay_check_contract(): #
    if(debug):print ("pc 111")
    contract = request.form['contract']
    if(debug):print ("pc 222")
    user_id=''
    if(debug):print(f"### contract {contract}")
    is_find, user_id, full_name, account1, err_message=check_contract(contract, user_id)
    if (is_find == 'success') :
        account1_float=round(account1/100,2)
        abonent_name=full_name.strip()
        abonent_name=re.sub(r'\s+', ' ', abonent_name) # заменяем внутри строки несколько пробелов на один
        short_name=make_short_name(abonent_name)
        if(debug):print(f"!!py_app user_id={user_id}, short_name={short_name}, account1={account1}")
        order_id=insert_after_find_contract(contract, user_id,abonent_name, account1)
        return render_template('confirm_contract.html', order_id=order_id, short_name=short_name, contract=contract, account1_float=account1_float)
    else :
        if(debug):print(f" err_message={err_message}")
        return render_template('error.html',contract=contract, err_message=err_message)        
    
@app.route('/pay_confirm', methods=['POST']) # Данные договора подтверждены проверкой из my_dipt.sns.net.ua
def pay_confirm():
    if(debug):print (f"777 pay_confirm called ")
    # pay_action = request.form['pay_action']
    # if(debug):print (f"777 pay_action {pay_action} ")
    # if pay_action != 'confirm_pay' :
    #     return render_template('form.html')
    
    # else :
    #     return render_template('index.html')
    
    order_id = request.form['order_id']
    amount = request.form['amount']
    payer_name = request.form['payer_name']
    test="test"
    if(debug):print("confirm 111")
    contract, abonent_name, user_id=get_after_find_contract(order_id)
    short_name=make_short_name(abonent_name)
    liqpay = LiqPay(LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)
    params = {
        "action": "pay",
        "amount": amount,
        "currency": "UAH",
        "description": f"Сплата по договору №{contract}; #{user_id}#; Абонент (скор) {short_name}; Платник:{payer_name}",
        "order_id": order_id,
        "version": "3",
        #"redirect_to_shop" : "1",
        #"sandbox": 1,  # УБЕРИТЕ sandbox: 1, когда запустите "вживую"
        #"server_url": "https://pay.sns.net.ua/callback",
        "server_url": f"{PUBLIC_BASE_URL}/callback",
        #"result_url": "https://pay.sns.net.ua/result"
        "result_url": f"{PUBLIC_BASE_URL}/my_result",
    }
    if(debug):print("confirm 333")
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params)
    payment_url = f"https://www.liqpay.ua/api/3/checkout?data={data}&signature={signature}"
    if(debug):print("confirm 444")
    return jsonify({"payment_url": payment_url})
    #return render_template('liqpay_form.html', data=data, signature=signature)
    

@app.route('/callback', methods=['POST'])
def callback():
    data = request.form.get('data')
    signature = request.form.get('signature')
    #if(debug):print("CALLBACK:", data)
    if(debug):print("CALLBACK: \n" )
    liqpay = LiqPay(LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)
    # проверка подлинности сообщения
    sign = liqpay.str_to_sign(LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY)
    if sign != signature:
        return "Invalid signature", 400
    
    decoded_data = json.loads(base64.b64decode(data))
    if(decoded_data['currency'] != 'UAH'):
        return "Invalid currency: use UAH only !", 400
    update_row_count=update_payments_aquire(decoded_data)
    if(update_row_count == 1) :
        send2sns_transaction(decoded_data)
        return "success", 200
    else:
        return jsonify({"Update payments error": "ok"}), 400

@app.route('/my_result', methods=['POST'])
def my_result():
    if(debug):print ("555 In Result")
    return render_template('close_cur_window.html')
    #data = request.form.get('data')
    #signature = request.form.get('signature')
    # Декодировать data
    #decoded_data = json.loads(base64.b64decode(data).decode('utf-8'))
    # decoded_data = json.loads(base64.b64decode(data))
    # order_id=decoded_data.get('order_id')
    return render_template('after_pay.html', order_id=order_id) 
    # Тут можно показать пользователю страницу "успех/ошибка"
    # return f"""
    #     <h1>Статус платежу: {decoded_data.get('status')}</h1>
    #     <p>Сума: {decoded_data.get('amount')}</p>
    #     <p>Договір: {decoded_data.get('order_id')}</p>
    #     <p>Маска карти: {decoded_data.get('sender_card_mask2')}</p>
    #     <p>Дякуємо за оплату!</p>
    # """

@app.route('/test_after_pay')
def test_after_pay():
    if(debug):print(f" Test After_pay")
    return render_template('after_pay.html',order_id='294f7625-2094-4778-8eb4-38f452189381')

@app.route('/after_pay')
def after_pay():
    if(debug):print(f" After_pay")
    return render_template('after_pay.html')

@app.route('/send_message')
def send_message():
    if(debug):print(f" Send Message After_pay")
    return render_template('error.html')

@app.route('/repeat_pay', methods=['POST'])
def repeat_pay():
    if(debug):print(f" Repeat Pay After_pay")
    return render_template('form.html')

@app.route('/check_payments_status')
def check_payments_status():
    order_id = request.args.get('order_id')
    ncount = request.args.get('ncount')
    data=check_pay_status(order_id)
    json_text=data.get_data(as_text=True)
    parsed=json.loads(json_text)
    status=parsed['status']
    if(debug):print(f"==check_status ncount={ncount}; status={status}")
    return parsed

#=======================================
if __name__ == '__main__':
    app.run(debug=True)
