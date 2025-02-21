import sys
sys.path.insert(0, '/home/anunta/auto_baseline/')
sys.path.append('db_mgmt')
from functools import wraps
from flask import request,jsonify
from endpoint_keys import end_point_keys
from endpoint_metadata import metadata
from json import JSONDecoder
from utils.config import db_str_mysql
import dbapi
from datetime import datetime, timedelta


def parse_object_pairs(pairs):
    return pairs

def validate_keys(payload, end_point):
    cur_payload_keys = payload.keys()
    cur_endpoint_keys = set(end_point_keys.get(end_point, []))
    if len(cur_payload_keys) != len(cur_endpoint_keys):
        return False
    cur_payload_keys = set(cur_payload_keys)
    if len(cur_payload_keys - cur_endpoint_keys) != 0:
        return False
    return True


def is_within_last_six_months(date_str):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    six_months_ago = datetime.now() - timedelta(days=30 * 6)
    #return date >= six_months_ago and date <= datetime.now()
    return date >= six_months_ago


def compare_dates(date_str1, date_str2):
    date1 = datetime.strptime(date_str1, '%Y-%m-%d')
    date2 = datetime.strptime(date_str2, '%Y-%m-%d')
    if date1 > date2:
        return False
    return True

def validate_date(payload):
    date = payload["date"]
    if isinstance(date,list):
        if len(date) == 1:
            return True
            #start_date = date[0].split("T")[0]
            #end_date = date[0].split("T")[0]
            #if start_date.count("-") == 1:
            #    start_date = start_date + "-1"
            #    end_date = end_date + "-1"
        else:
            start_date = date[0].split("T")[0]
            end_date = date[1].split("T")[0]    
            date1 = datetime.strptime(start_date, "%Y-%m-%d")
            date2 = datetime.strptime(end_date, "%Y-%m-%d")
            difference = date2 - date1
            number_of_days = difference.days   
            if number_of_days > 180:
                return False
        #if not compare_dates(start_date, end_date):
        #    return False
        #if not is_within_last_six_months(start_date):
        #    return False
        #if not is_within_last_six_months(end_date):
        #    return False
    return True    



def validate_parameter_pollution(data, endpoint):
    decoder = JSONDecoder(object_pairs_hook=parse_object_pairs)
    payload = decoder.decode(data)
    actual_length = len(set(end_point_keys.get(endpoint, [])))
    cur_length = len(payload)
    if actual_length != cur_length:
        return False
    return True


def validate_size(payload):
    payload_size = sys.getsizeof(payload)
    mb_size = payload_size/(1024*1024)
    if mb_size > 5:
        return False
    return True


def validate_input(payload):
    print(payload, "aaaa")
    for k,v in payload.items():
        mdata = metadata.get(k)
        if mdata == None:continue
        print(mdata, "ddd")
        v_type = mdata["type"]
        if v_type == "integer":
            if isinstance(v, int):
                if mdata.get("maximum") and v > mdata["maximum"]:return False
                if mdata.get("minimum") and v < mdata["minimum"]:return False
            else:return False
        if v_type == "string":        
            if isinstance(v, str):
                values = mdata.get("values")
                if values and v not in values:return False
            else:return False    
        if v_type == "list":        
            if isinstance(v, list):
                value_type = mdata.get("value_type")
                for item in v:
                    if value_type == "string":
                        if not isinstance(item, str):return False
                    elif value_type == "dictionary":
                        if not isinstance(item, dict):return False    
                        for each in item:
                            if not isinstance(each, str):return False
            else:return False                
                    
        if v_type == "dictionary":            
            if isinstance(v, dict):  
                value_type = mdata.get("key_type")
                for item in v:
                    if not isinstance(item, str):return False
            else:return False
        
        if v_type == "set":
            if isinstance(v, set):
                value_type = mdata.get("value_type")
                for item in v:
                    if not isinstance(item, str):return False            
            else:return False        

        if v_type == "tuple":
            if isinstance(v, tuple):
                value_type = mdata.get("value_type")
                for item in v:
                    if not isinstance(item, str):return False
            else:return False
        
        if v_type == "multiple":
            found = 0
            allow_types = mdata["allowed_types"]
            print(allow_types)
            for a_type in allow_types:
                if a_type == "integer":
                    if isinstance(v, int):
                        found = 1
                if a_type == "string":
                    if isinstance(v, str):
                        found = 1
                if a_type == "list":
                    if isinstance(v, list):
                        found = 1
            if found == 0:
                return False

    return True


def validate_token(payload, current_token, end_point):
    if end_point == "addUser":return True
    uid = -1
    if "uid" in payload:
        uid = payload["uid"]
    if "userid" in payload:
        uid = payload["userid"]
    if "user_id" in payload:
        uid = payload["user_id"]
    if "admin_id" in payload:
        uid = payload["admin_id"]
    actual_token = dbapi.get_actual_token(db_str_mysql, uid)
    if current_token != actual_token:
        return False
    return True

def validate_header(referrer_policy, endpoint):
    if endpoint == "addUser":return True
    if referrer_policy != "no-referrer":
        return False
    return True

def validate_main(end_point):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            payload = request.get_json()
            raw_payload = request.data.decode('utf-8')
            current_token = request.headers['Token']
            referrer_policy = ""
            if end_point != "addUser":
                current_token = request.headers['Token']
                referrer_policy = request.headers['Referrer-Policy']
            if not validate_size(payload):
                return jsonify({'message' : 'Input length is exceeding the limit.'}), 400
            if not validate_keys(payload, end_point):
                return jsonify({'message' : 'The passed keys are outside the valid range.'}), 400
            if not validate_parameter_pollution(raw_payload, end_point):
                return jsonify({'message' : 'The passed keys are outside the valid range.'}), 400
            if not validate_input(payload):
                return jsonify({'message' : 'The passed values are outside the valid range.'}), 400
            #if "date" in payload and not validate_date(payload):
            #    return jsonify({'message' : 'Please select the date from past six months'}), 200
            if not validate_token(payload, current_token, end_point):
                return jsonify({'message' : 'Token is invalid!'}), 400
            if not validate_header(referrer_policy, end_point):
                return jsonify({'message' : 'The passed headers are outside the valid range.'}), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator



if __name__ == "__main__":
    validate_main("getFilterData")
    #validate_main("getHostpoolCostBydate")
    pass
