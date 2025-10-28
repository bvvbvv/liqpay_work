from datetime import time


def check_contract(contract, user_id_in):
    import requests

    # Данные для отправки
    payload = {
        'contract': contract,
        'user_id': user_id_in
    }

    # Отправка POST-запроса
    #response = requests.post('http://mytest.com/work/myscript.php', data=payload)
    #print ("ch 555111")
    #response = requests.post('liqpay/check_contract.php', data=payload)
    #response = requests.get('http://liqpay/check_contract.php', params=payload)
    #response = requests.get('http://pay_dipt/check_contract.php', params=payload)
    try:
        #response = requests.post('http://pay_dipt/check_contract.php', data=payload, timeout=3)
        response = requests.post('https://my-dipt.sns.net.ua/new/work_bvv/check_contract.php', data=payload, timeout=3)
    except requests.exceptions.Timeout:
        return 'not_find', '0', 'Не найдено', '0.0','Помилка: Перевищено час очікування відповіді сервера статистики.'
        
    # Проверка успешности запроса
    if response.status_code == 200:
        # Получение ответа в формате JSON
        result = response.json()
        # Извлечение данных
        is_find = result.get('is_find')
        user_id = result.get('user_id')
        full_name = result.get('full_name')
        account1 = result.get('account1')
        err_message='';
        if (is_find != 'success'):
            err_message = ' Договір № <b>' + contract + '</b> не знайдено.'
            
       # print(f"#py_ch: is_find={is_find}, user_id={user_id}, full_name={full_name}, accoint1={account1}")
        return is_find, user_id, full_name, account1, err_message
    else:
        print(f"utility4sns: check_contract: Помилка запиту: {response.status_code}")
        return 'error', '0', 'Не найдено', '0.0', 'Помилка звернення до сервера статистики, код :<b>' + str(response.status_code)+'</b>'
    
# def send2transaction(user_id, summ):
#     import requests

#     # Данные для отправки
#     payload = {
#         'summ': summ,
#         'user_id': user_id
#     }
#     # Отправка POST-запроса
#     #response = requests.post('http://mytest.com/work/myscript.php', data=payload)
#     try:
#         response = requests.post('http://pay_dipt/send2transaction.php', data=payload, timeout=3)
#     except requests.exceptions.Timeout:
#         return 'error', '0', 'Не найдено', '0.0','Помилка:  Перевищено час очікування відповіді сервера  transaction.'
        

#     # Проверка успешности запроса
#     if response.status_code == 200:
#         # Получение ответа в формате JSON
#         result = response.json()
#         # Извлечение данных
#         res1 = result.get('res1')
#         res2 = result.get('res2')
#         print(f"res1={res1}, res2={res2}")
#     else:
#         print(f"utility4sns send2transaction:  Помилка запроса: {response.status_code}")
#         return 'error', '0', 'Не найдено', '0.0', 'Помилка звернення до transaction, код <b>'+ str(response.status_code)+'</b>'
  
def send2sns_transaction(decoded_data):
    import requests, time, pytz, re
    import datetime
    from datetime import datetime as dt
    NMaxRequest=5
    MaxSecond = 5
    SleepSecond=3
    success = False
    response_text = None
     # Данные для отправки
    #  Переводим в часовой пояс Kyiv
    ts_ms = decoded_data['create_date']  # timestamp в миллисекундах
    ts_sec = ts_ms / 1000
    dt_utc = dt.fromtimestamp(ts_sec, tz=datetime.timezone.utc)
    kyiv_tz = pytz.timezone("Europe/Kyiv")
    dt_kyiv = dt_utc.astimezone(kyiv_tz)
    datepay = dt_kyiv.strftime("%Y-%m-%d %H:%M:%S")  # Например: 11-10-2025 15:30:12
    
    description=decoded_data['description']
    match=re.search(r"\s#(\d{1,7})#;", description)
    if(match):
        user_id=match.group(1)
    
    amount = decoded_data['amount']
    order_id = decoded_data['order_id']
    transaction_id=decoded_data['transaction_id']
    payload = {
        'amount': amount,
        'user_id': user_id,
        'transaction_is': transaction_id,
        'datepay':datepay    
    }
    #REMOTE_URL='http://pay_dipt/send2transaction.php'
    REMOTE_URL='https://my-dipt.sns.net.ua/new/work_bvv/send2transaction.php'
    for attempt in range(1, NMaxRequest + 1):
        try:
            response = requests.post(REMOTE_URL,data=payload,timeout=MaxSecond)
        except requests.exceptions.Timeout:
        
            
            # Если удалённый сервер ответил
            if response.status_code == 200:
                try:
                    resp_json = response.json()
                    if resp_json.get("result") == "OK":
                      #  print("[Callback] Удалённый сервер подтвердил приём (OK)")
                        success = True
                        response_text = response.text
                        break
                except:
                    print("[Callback] Ответ сервера не JSON. Продолжаем попытки...")

        except requests.exceptions.Timeout:
            print(f"[Callback] Сервер {REMOTE_URL} не ответил за {MaxSecond} сек")
            return 'error', '0', 'Не найдено', '0.0','Сервер transaction {REMOTE_URL} не відповів за {MaxSecond} сек'
        except Exception as e:
            print(f"[Callback] Помилка соединения: {e}")
            return 'error', '0', 'Не найдено', '0.0','Помилка підключення до сервера transaction: {e}'
        
        time.sleep(SleepSecond)  # задержка между попытками

    if not success:
        print("[Callback] Не удалось отправить данные на удалённый сервер после всех попыток")
        return 'error', '0', 'Не найдено', '0.0','Не вдалось підключитись до сервера transaction після всіх спроб'

    # Обязательно вернуть LiqPay "success", иначе они снова дернут callback!
    #return "success", 200
    
    else:
     #обновляем иаблицу payments_acquire
        conn=get_db_connection()
        cur = conn.cursor()
        resp_json["result"]
        trans_id=resp_json["trans_id"]
        old_account1=resp_json["old_account1"]
        new_account1=resp_json["new_account1"]
        status =resp_json["status"] 
        cur.execute("""
            update payments_acquire set status= %s, sns_transaction_id=%s,old_account1=%s, new_account1=%s  where order_id= %s
            """, (status,trans_id, old_account1,new_account1, order_id)
        )
        updated_row_count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        print(f" ***** Success Update table payments_acquire : {updated_row_count}")     
        
        
def make_short_name(full_name):

    last_name, sec_name, par_name = full_name.split()
    ln=len(last_name)
    
    if ln > 5:
        s_last=last_name[:2]+'.'*(ln-4)+last_name[ln-2:ln]  #первые две и последние две буквы фамилии
    elif ln > 2:
        s_last=last_name[0]+'.'*(ln-2)+last_name[ln-1]  #первая и последняя буквы  буквы фамилии
    else :
        s_last=last_name[0]+'.'
        
    s_name=sec_name[0]
    s_par=par_name[0]
    
    
    return s_last+' '+s_name+'. '+s_par+'.' 

def get_db_connection():
    import psycopg2
    from liqpay_config_loc import LIQPAY_PUBLIC_KEY, LIQPAY_PRIVATE_KEY,DB
    try:
        conn = psycopg2.connect(
        host=DB["host"],
        database=DB["database"],
        user=DB["user"],
        password=DB["password"],
        port=DB.get("port", 5432)
        )
        return conn
    except Exception as e:
        print("DB sns_pay_base connection error:", e)
        return None # Возвращаем None в случае ошибки подключе
    
def insert_after_find_contract(contract, user_id, abonent_name, account1):
    import uuid
    conn=get_db_connection()
    cur = conn.cursor()
    order_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO payments_acquire (order_id, contract, user_id, abonent_name,old_account1, status)
        VALUES (%s, %s, %s, %s,%s,%s) ON CONFLICT (order_id) DO NOTHING
        RETURNING ID 
        """, (order_id, contract, user_id, abonent_name, account1,"after_find_contract") 
    )
    insert_id = cur.fetchone()[0]
    print(f"## ins 555 insert_id={insert_id} order_id={order_id}")
    conn.commit()
    cur.close()
    conn.close()
    return order_id

def get_after_find_contract(order_id):
    conn=get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        select contract, abonent_name, user_id from payments_acquire where order_id= %s
        """, (order_id, )
    )
    row = cur.fetchone()
    if row:
        contract, abonent_name, user_id = row
        #print("Одна строка:", contract, abonent_name)
    else:
        print("Нет данных")
    
    conn.commit()
    cur.close()
    conn.close()
    return contract, abonent_name, user_id

def update_payments_aquire(decoded_data):
    import re
    description=decoded_data['description']
        # вытаскиваем номер договора из описания
        # match=re.search(r"\s№(\d{4,6};", description)
        # if(match):
        #     contract=match.group(0)
        
        # вытаскиваем имя плательщика из описания
    match=re.search(r"\sПлатник:(.*)$", description)
    if(match):
        payer_name=match.group(0)
        
    import pytz, datetime       
    # Переводим в часовой пояс Kyiv
    ts_ms = decoded_data['create_date']  # timestamp в миллисекундах
    ts_sec = ts_ms / 1000
    dt_utc = datetime.datetime.fromtimestamp(ts_sec, tz=datetime.timezone.utc)
    kyiv_tz = pytz.timezone("Europe/Kyiv")
    dt_kyiv = dt_utc.astimezone(kyiv_tz)
    payment_date = dt_kyiv.strftime("%Y-%m-%d %H:%M:%S")  # Например: 11-10-2025 15:30:12
   
    order_id = decoded_data['order_id']
    status = decoded_data['status']+':bank'
    amount = decoded_data['amount']
    sender_first_name = decoded_data["sender_first_name"]
    sender_last_name = decoded_data["sender_last_name"]
    sender_full_name=sender_first_name +' '+ sender_last_name
    mask2 = decoded_data["sender_card_mask2"]
    sender_bank = decoded_data["sender_card_bank"]
    liqpay_order_id = decoded_data['liqpay_order_id']
    bank_transaction_id=decoded_data['transaction_id']
    conn=get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        update payments_acquire set amount =%s, payment_date= %s, status= %s,
        liqpay_order_id= %s, payer_name= %s, sender_full_name= %s, sender_bank= %s, 
        sender_card_mask2= %s, bank_transaction_id= %s where order_id= %s
        """, (amount, payment_date, status, liqpay_order_id, payer_name,sender_full_name, sender_bank,  mask2, bank_transaction_id, order_id)
    )
    updated_row_count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f" Success Update table payments_acquire : {updated_row_count}")
    return updated_row_count

def check_pay_status(order_id):
    from flask import jsonify
    conn=get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    select status, contract, amount, abonent_name, payer_name, sender_full_name, old_account1, new_account1,
    payment_date  from payments_acquire where order_id= %s
    """, (order_id, )
    )
    row = cur.fetchone()
    if row:
        status, contract, amount, abonent_name, payer_name, sender_full_name, old_account1, new_account1, payment_date = row
        print("@@@ get_payments_status:", status, contract, amount, abonent_name, payer_name, sender_full_name, old_account1, new_account1 )
    else:
        print("Нет данных")
    
    #print(f"## ins 555 insert_id={insert_id} order_id={order_id}")
    conn.commit()
    cur.close()
    conn.close()
    data_json=jsonify({
        "status":status,
        "contract":contract,
        "amount": amount,
        "abonent_name":abonent_name,
        "payer_name":payer_name,
        "sender_full_name":sender_full_name,
        "old_account1":old_account1,
        "new_account1":new_account1,
        "payment_date":payment_date
    })
    return data_json

def get_os_param():
    import platform
    import os
    os_name=platform.system()
    if os_name == 'Windows':
        debug = 1
        is_windows = True
        is_ngrok = True #"(для локальной отладки через ngrok)"
    else:
        debug = 0
        is_windows = False
        is_ngrok = False #(для боевого сервера)
    return debug, is_windows, is_ngrok
    
    
    # os_release=platform.release()
    # os_version=platform.version()
    # machine=platform.machine()
    # processor=platform.processor()
    # python_version=platform.python_version()
    # cwd=os.getcwd()
    # return {
    #     "os_name":os_name,
    #     "os_release":os_release,
    #     "os_version":os_version,
    #     "machine":machine,
    #     "processor":processor,
    #     "python_version":python_version,
    #     "cwd":cwd
    # }

