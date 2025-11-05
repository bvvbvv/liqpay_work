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
    from liqpay_config import LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY,DB
else:
    debug = 0
    is_windows = False  
    site.addsitedir("/usr/local/bin/pay_app/lib/python3.12/site-packages")
    sys.path.insert(0,"/var/www/pay.sns.net.ua/public_html")
    from liqpay_config import LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY,DB
    
    
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask,render_template,request, redirect, flash, jsonify
from liqpay import LiqPay
import base64
import json

from utility4sns import get_os_param, check_contract, make_short_name, insert_after_find_contract, get_after_find_contract,  update_payments_aquire, check_pay_status, send2sns_transaction, error_payments_aquire
if (is_windows ):
    PUBLIC_BASE_URL = "https://nikole-populational-commensurately.ngrok-free.dev"

else:
    PUBLIC_BASE_URL = "https://pay.sns.net.ua"

import logging
from logging.handlers import TimedRotatingFileHandler
from flask import Flask

app = Flask(__name__)

## ---------------------------------------------------------
# 🔧 Настройка логирования Flask
# ---------------------------------------------------------

# Путь к файлу лога (можно изменить)
LOG_FILE = '/var/log/apache2/flask_app.log'

# Создаём обработчик, если ещё не создан
# if not app.logger.handlers:
#     handler = logging.FileHandler(LOG_FILE)
#     handler.setLevel(logging.INFO)

#     # Формат лога: время, уровень, сообщение
#     formatter = logging.Formatter(
#         '%(asctime)s [%(levelname)s] %(message)s',
#         '%Y-%m-%d %H:%M:%S'
#     )
#     handler.setFormatter(formatter)
#     # Отключаем передачу сообщений во встроенный root Apache logger
#     app.logger.propagate = False  
#     # Подключаем к логгеру Flask
#     app.logger.addHandler(handler)
#     app.logger.setLevel(logging.INFO)
    
    # === Настройка ротации логов ===
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

# Создаём handler с ротацией по дате
log_handler = TimedRotatingFileHandler(
    filename='/var/log/apache2/flask_app.log',  # базовое имя
    when='midnight',        # ротация каждый день в 00:00
    interval=1,             # каждые сутки
    backupCount=30,          # хранить 30 старых логов (удаляет старше)
    encoding='utf-8'
)

# Формат имени архива логов
log_handler.suffix = "%d.%m.%Y"  # будет flask_app.log.05.11.2025 и т.п.
log_handler.setFormatter(log_formatter)


debug=1
if(debug):print("!!! LiqPay_TEST app started $$$")
if(debug):app.logger.info('Проверка логгера Flask')
  
@app.route('/')
def index():
    return render_template('index.html', title="Home")

@app.route('/price')
def price():
    return render_template('price.html', title="Price")

@app.route('/security_politics')
def security_politics(): #только полное имя файла, без расширения !!
    return render_template('security_politics.html')

@app.route('/oferta')
def oferta(): #только полное имя фвайла !!
    return render_template('oferta.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        contract = request.form.get('contract')
        contract=re.sub(r'^0+', '', contract)
        amount = request.form.get('amount')
        # Простая валидация: contract - цифры, amount - положительное число
        try:
            if not contract or not contract.strip().isdigit():
                if(debug):app.logger.error('Помилка: Невірний номер договору')
                raise ValueError("Помилка: Невірний номер договору")
            a = float(amount)
            if a <= 0:
                if(debug):app.logger.error('Помилка: Невірна сума платежу')
                raise ValueError("Помилка: Невірна сума платежу")
            
        except Exception as e:
            if(debug):app.logger.error('Exception in form(): %s', str(e))
            return render_template('error.html', message=str(e))
        
    return render_template('form.html', title="Connect")


@app.route('/form_work', methods=['GET', 'POST'])
def form_work():
    if request.method == 'POST':
        contract = request.form.get('contract')
        contract=re.sub(r'^0+', '', contract)
        amount = request.form.get('amount')
        # Простая валидация: contract - цифры, amount - положительное число
        try:
            if not contract or not contract.strip().isdigit():
                if(debug):app.logger.error('Помилка: Невірний номер договору')
                raise ValueError("Помилка: Невірний номер договору")
            a = float(amount)
            if a <= 0:
                if(debug):app.logger.error('Помилка: Невірна сума платежу')
                raise ValueError("Помилка: Невірна сума платежу")
            
        except Exception as e:
            if(debug):app.logger.error('Exception in form_work(): %s', str(e))
            return render_template('error.html', message=str(e))
        
    return render_template('form_work.html', title="Connect")

@app.route('/pay_check_contract', methods=["POST"])
def pay_check_contract(): #
    contract = request.form['contract']
    user_id=''
    if(debug):print(f"### contract {contract}")
    if(debug):app.logger.info(f"### contract {contract}")
    is_find, user_id, full_name, account1, err_message=check_contract(contract, user_id)
    if (is_find == 'success') :
        account1_float=round(account1/100,2)
        abonent_name=full_name.strip()
        abonent_name=re.sub(r'\s+', ' ', abonent_name) # заменяем внутри строки несколько пробелов на один
        short_name=make_short_name(abonent_name)
        if(debug):print(f"!!py_app user_id={user_id}, short_name={short_name}, account1={account1}")
        if(debug):app.logger.info(f"!!py_app user_id={user_id}, short_name={short_name}, account1={account1}")
        order_id=insert_after_find_contract(contract, user_id,abonent_name, account1)
        return render_template('confirm_contract.html', order_id=order_id, short_name=short_name, contract=contract, account1_float=account1_float)
    else :
        if(debug):print(f" err_message={err_message}")
        if(debug):app.logger.error(f" app.py pay_check_contract err_message={err_message}")
        return render_template('error.html',contract=contract, err_message=err_message)        
    
@app.route('/pay_confirm', methods=['POST']) # Вызов из confirm_contract.html  
# Данные договора подтверждены проверкой из my_dipt.sns.net.ua
def pay_confirm():
    if(debug):print (f"777 pay_confirm called ")
    if(debug):app.logger.info(f"777 pay_confirm called ")
    
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
    signature = liqpay.cnb_signature(params)
    data = liqpay.cnb_data(params) 
    #Вызывется из JS confirm_contract.html в новом окне, 
    # вместе с after_pay.html в родительском окне
    payment_url = f"https://www.liqpay.ua/api/3/checkout?data={data}&signature={signature}"
    return jsonify({"payment_url": payment_url})
    

@app.route('/callback', methods=['POST'])
def callback():
    data = request.form.get('data')
    signature = request.form.get('signature')
    #if(debug):print("CALLBACK:", data)
    if(debug):print("### app.py: CALLBACK: \n" )
    if(debug):app.logger.info("### app.py: CALLBACK: ")
    liqpay = LiqPay(LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY)
    # проверка подлинности сообщения
    sign = liqpay.str_to_sign(LIQPAY_PRIVATE_KEY + data + LIQPAY_PRIVATE_KEY)
    if sign != signature:
        return "Invalid signature", 400
    
    decoded_data = json.loads(base64.b64decode(data))
    #if(debug):print(f"app.py: Callback: {decoded_data} \n")
    if(debug):app.logger.info(f"app.py: Callback: {decoded_data} ")
    
    if(decoded_data['currency'] != 'UAH'):
        if(debug):app.logger.error(f" Invalid currency: {decoded_data['currency']}")
        return "Invalid currency: use UAH only !", 400
    
    if(decoded_data['status'] != 'success'):
        if(debug):app.logger.error(f"app.py callback Payment status not success: {decoded_data['status']}")
        if(debug):print(f" Payment status not success: {decoded_data['status']}")
        error_payments_aquire(decoded_data) # обновляем статус в payments_acquire на неуспешный и записываем ошибку
        return "Payment not success", 400
    update_row_count=0
    update_row_count=update_payments_aquire(decoded_data)
    if (update_row_count == 1) : #обновлена запись в payments_acquire
        result, message=send2sns_transaction(decoded_data)
        if(result != 'success'): # произошла ошибка при отправке в sns transaction
            if(debug):print(f" Send to SNS error: {message}")
            if(debug):app.logger.error(f" Send to SNS error: {message}")
            decoded_data['status']='error:sns'
            decoded_data['err_description']=message
            error_payments_aquire(decoded_data) #обновляем статус в payments_acquire на error и записываем ошибку
            # будет повторная попытка из liqpay
            return "error", 400
        else: # запись обновлена и отправлена в sns transaction
            if(debug):print(" Update payments success ")
            if(debug):app.logger.info("app.py Update payments success ")    
            return "success", 200
        
    elif(update_row_count == -1): #запись не обновлена, т.к. уже была со статусом success:sns
            if(debug):print(" Record already updated to success:sns, no action taken ")    
            if(debug):app.logger.info(" Record already updated to success:sns, no action taken ")   
            return "success", 200
    else: #запись не обновлена, по причине ошибки пр
            if(debug):print(f" Error in update_payments_acquire  {decoded_data} ")
            decoded_data['status']='error:sns'
            decoded_data['err_description']='Ошибка в обновлении записи payments_acquire'
            if(debug):app.logger.error(f" app.py Error in update_payments_acquire {decoded_data} ")
            error_payments_aquire(decoded_data) #обновляем статус в payments_acquire на error и записываем ошибку
            return "success", 200

@app.route('/my_result', methods=['GET','POST'])
def my_result():
    if(debug):print ("555 In Result")
    return render_template('close_cur_window.html')
    
@app.route('/wait_transaction') # Вызов из JS confirm_contract.html вместе с открытием окна LiqPay оплаты
def wait_transaction():
    if(debug):print(f" Wait_transaction result")
    return render_template('wait_transaction.html')

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
    if(debug):print(f" ==check_status ncount={ncount}; status={status}")
    return parsed

#=======================================
if __name__ == '__main__':
    app.run(debug=True)
