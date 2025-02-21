end_point_keys = {
        'SignIn':['email', 'password'],
        'UpdateCustomerStatus':["user_id", "customer_id", "status", "date", "customer"],
        'GetCustomerData':['uid'],
        'GetErrorLogs':['user_id', 'model_id'],
        'SignOut':['uid'],
        'getFilterData':['customer_id', 'userid'],
        'GetCustomerModelsData':['cost_types', 'resource_types', 'subscriptions', 'customer_id', 'userid', 'filter', 'rowsCountPerTable'],
        'GetModelDetails':['model_name', 'start_date', 'customer_id', 'user_id', 'model_id'],
        'Table_Export':["key","currentPage","rowsCountPerTable","uid"],
        'UpdateTrainingFrequency':["user_id", "customer_id", "Type", "freq_time", "day"],
        'Table_Sort':["key", "sort_order", "column_id", "tab_name", "rowsCountPerTable", "currentPage", "uid"],
        'RetrainModel':['customer_id', 'model_id', 'user_id'],
        'GetCustomerData_EUV':['uid'],
        "UpdateCustomerStatus_EUV":['customer', 'customer_id', 'date', 'status', 'user_id'],
        "Device_Data":['uid', 'customer_id', 'device_ips', 'search_key'],
        "Device_Filter":['customer_id', 'uid'],
        "getFilterData_EUV":['userid']
        }
