from flask import Flask, make_response, jsonify, request, redirect, url_for, jsonify, send_from_directory
from flask.views import MethodView
from flask_cors import CORS
import sys
import os
import time
import jwt
import asyncio
from functools import wraps
import datetime
from datetime import datetime, timedelta
from validate_params import validate_main
import apis.autobase_main as main_page
import apis.EUV_main as EUV
#import apis.customer_model_page as customer_model_page
import apis.sanath as customer_model_page
import apis.model_details as model_details
import apis.device_page as device_page
import apis.retrain_model as retrain_model
import apis.filter_data as filter_data
#import apis.table_export as table_export
import apis.tb as table_export
import apis.update_freq as update_freq
import apis.sign_in as sign_in
import decrypt
sys.path.insert(0, '/home/anunta/auto_baseline')
from utils.config import db_str_mysql, mysql_india
from utils.config import SECRET_KEY
sys.path.append('db_mgmt')
import dbapi
import json


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
#CORS(app, origins = ['https://autobaselineapi.anuntatech.com', 'autobaseline.anuntatech.com'])

app.config['SECRET_KEY'] = SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            # Decode the token
            secret_key = decrypt.get_decrypted_secret_key()
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)

    return decorated


class SignIn(MethodView):
    def get(self):
        return "Responding to a GET request"

    def post(self):
        data_dict = request.get_json()
        email = data_dict.get('email')
        def_dict = sign_in.sign_in(data_dict)
        if def_dict.get("p_status") == "User successfully logged in":
            token_exp_time = datetime.utcnow() + timedelta(minutes=500)
            secret_key = decrypt.get_decrypted_secret_key()
            token = jwt.encode({'user': def_dict['email'], 'exp': token_exp_time}, secret_key)
            def_dict['jwt_token'] = token
            timestamp = token_exp_time.strftime('%Y-%m-%d %H:%M:%S')
            data = dbapi.store_token(db_str_mysql, def_dict['uid'], token, timestamp)
            data = dbapi.store_token(mysql_india, def_dict['uid'], token, timestamp)
        if def_dict.get('message') == "Please Enter Valid Email":
            return jsonify(def_dict), 400
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/SignIn", view_func=SignIn.as_view("SignIn"))


class ValidateEmail(MethodView):
    def get(self):
        """ Responds to GET requests """

    @token_required
    @validate_main('ValidateEmail')
    def post(self):
        data_dict = request.get_json()
        if 1:#try:
            def_dict = sign_in.validate_email(data_dict)
            token = jwt.encode({'user' : def_dict['email'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=500)}, app.config['SECRET_KEY'])
            if def_dict["p_status"] == "User Email Validated successfully!":
               def_dict['jwt_token'] = token
               def_dict['jwt_token'] = token
            return jsonify(def_dict)

app.add_url_rule("/cqIDPpApi/ValidateEmail", view_func=ValidateEmail.as_view("ValidateEmail"))

class GetCustomerData(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetCustomerData")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = main_page.get_customer_data_list(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetCustomerData", view_func=GetCustomerData.as_view("GetCustomerData"))

class GetCustomerData_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetCustomerData_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = EUV.get_EUV_customer_data_list(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetCustomerData_EUV", view_func=GetCustomerData_EUV.as_view("GetCustomerData_EUV"))

class GetCustomerModelsData(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetCustomerModelsData")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = customer_model_page.get_customer_model_data_v1(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetCustomerModelsData", view_func=GetCustomerModelsData.as_view("GetCustomerModelsData"))

class GetCustomerModelsData_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetCustomerModelsData_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = customer_model_page.euv_get_customer_model_data(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetCustomerModelsData_EUV", view_func=GetCustomerModelsData_EUV.as_view("GetCustomerModelsData_EUV"))

class GetModelDetails(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetModelDetails")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = model_details.get_model_data(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetModelDetails", view_func=GetModelDetails.as_view("GetModelDetails"))

class GetModelDetails_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetModelDetails_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = model_details.get_model_data(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetModelDetails_EUV", view_func=GetModelDetails_EUV.as_view("GetModelDetails_EUV"))

class getFilterData(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("getFilterData")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = filter_data.get_filter_data(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/getFilterData", view_func=getFilterData.as_view("getFilterData"))


class getFilterData_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("getFilterData_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = filter_data.get_filter_data_EUV(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/getFilterData_EUV", view_func=getFilterData_EUV.as_view("getFilterData_EUV"))

class RetrainModel(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("RetrainModel")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = retrain_model.retrain_model_v1(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/RetrainModel", view_func=RetrainModel.as_view("RetrainModel"))

"""class RetrainModel_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("RetrainModel_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = retrain_model.retrain_model_EUV(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/RetrainModel_EUV", view_func=RetrainModel_EUV.as_view("RetrainModel_EUV"))"""

class UpdateTrainingFrequency(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("UpdateTrainingFrequency")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = update_freq.get_update_freq(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/UpdateTrainingFrequency", view_func=UpdateTrainingFrequency.as_view("UpdateTrainingFrequency"))

class UpdateTrainingFrequency_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("UpdateTrainingFrequency_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = update_freq.get_update_freq_EUV(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/UpdateTrainingFrequency_EUV", view_func=UpdateTrainingFrequency_EUV.as_view("UpdateTrainingFrequency_EUV"))

class UpdateCustomerStatus(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("UpdateCustomerStatus")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = main_page.update_customer_status(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/UpdateCustomerStatus", view_func=UpdateCustomerStatus.as_view("UpdateCustomerStatus"))

class UpdateCustomerStatus_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("UpdateCustomerStatus_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = EUV.update_customer_status_EUV(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/UpdateCustomerStatus_EUV", view_func=UpdateCustomerStatus_EUV.as_view("UpdateCustomerStatus_EUV"))

class GetErrorLogs(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetErrorLogs")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = main_page.get_error_logs(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetErrorLogs", view_func=GetErrorLogs.as_view("GetErrorLogs"))

class GetErrorLogs_EUV(MethodView):
    def get(self):
        return "Responding to a GET request"

    @token_required
    @validate_main("GetErrorLogs_EUV")
    def post(self):
        data_dict = request.get_json()
        if 1:
            def_dict = EUV.get_error_logs_EUV(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/GetErrorLogs_EUV", view_func=GetErrorLogs_EUV.as_view("GetErrorLogs_EUV"))

class SignOut(MethodView):
    def get(self):
        return "Responding to a GET request "
    
    @token_required
    @validate_main("SignOut")
    def post(self):
        data_dict = request.get_json()
        if 1:
            data_dict = sign_in.sign_out(data_dict)
            if data_dict.get('message', "") == "User Successfully LogedOut":
                return jsonify(data_dict)
            else:
                return jsonify(data_dict)

app.add_url_rule("/AutoBaseApi/SignOut", view_func=SignOut.as_view("SignOut"))

class Table_Export(MethodView):
    def get(self):
        return "Responding to a GET request = "
    @token_required
    @validate_main('Table_Export')
    def post(self):
        data_dict = request.json
        if 1:#try
            def_dict = table_export.table_export(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/Table_Export", view_func = Table_Export.as_view("Table_Export"))

class Table_Sort(MethodView):
    def get(self):
        return "Responding to a GET request = "
    @token_required
    @validate_main('Table_Sort')
    def post(self):
        data_dict = request.json
        if 1:#try
            def_dict = table_export.table_sort(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/Table_Sort", view_func = Table_Sort.as_view("Table_Sort"))

class Device_Data(MethodView):
    def get(self):
        return "Responding to a GET request = "
    @token_required
    @validate_main('Device_Data')
    def post(self):
        data_dict = request.json
        if 1:#try
            def_dict = device_page.euv_get_customer_model_data_v1(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/Device_Data", view_func = Device_Data.as_view("Device_Data"))

class Device_Filter(MethodView):
    def get(self):
        return "Responding to a GET request = "
    @token_required
    @validate_main('Device_Filter')
    def post(self):
        data_dict = request.json
        if 1:#try
            def_dict = device_page.get_device_filter_data(data_dict)
        return jsonify(def_dict)

app.add_url_rule("/AutoBaseApi/Device_Filter", view_func = Device_Filter.as_view("Device_Filter"))

class generateotp(MethodView):
    def get(self):
        return  "response to generate_otp request"
    #@token_required
    #@validate_main('generateotp')
    def post(self):
         data = request.get_json()
         response = sign_in.send_otp_to_email(data)
         return jsonify(response)
app.add_url_rule('/AutoBaseApi/generateotp',view_func=generateotp.as_view("generateotp"))

class ValidateOTP(MethodView):
    def get(self):
        return "response to validate_otp request"
    #@token_required
    #@validate_main
    def post(self):
        data = request.get_json()
        response = sign_in.generate_validate_otp(data)
        return jsonify(response)
app.add_url_rule('/AutoBaseApi/ValidateOTP',view_func=ValidateOTP.as_view("ValidateOTP"))

class Reset_Password(MethodView):
    def get(self):
        """ Responds to GET requests """
        #return "Responding to a GET request"
        return
    #@token_required
    #@validate_main('Reset_Password')
    def post(self):
        if 1:#try
            data_dict = request.get_json()
            def_dict = sign_in.reset_password(data_dict)
            print(def_dict, "aaaaaaa")
            if def_dict['message'] == 'Successfully Changed Password':
                #dbApi.delete_user_from_wrong_login_info(db_str_mysql_new, data_dict['email'])
                return jsonify({'message': 'password updated successfully'}), 200
            else:
                return jsonify({"message": "An error occurred", "details": def_dict}), 400

app.add_url_rule("/AutoBaseApi/Reset_Password", view_func =  Reset_Password.as_view("Reset_Password"))

class resendOTP(MethodView):
    def get(self, uid):
        """ Responds to GET requests """
        if 1:#try:
            def_dict = sign_in.resendOTP(uid)
        return jsonify(def_dict)
        #except:
        #   def_dict = {'p_code': '', 'p_status': 'API Error', 'uid': ''}
        #   return jsonify(def_dict)
    @token_required
    @validate_main('resendOTP')
    def post(self):
        return "Responding to a POST request"

app.add_url_rule("/cqIDPpApi/resendOTP/<uid>", view_func=resendOTP.as_view("resendOTP"))

if __name__ == "__main__":
     app.run(debug=False, host = '0.0.0.0', port = 5001)
