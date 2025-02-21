#from redis import Redis
from diskcache import Cache
import uuid
import pickle
import math
import ast
import copy
from datetime import datetime
import datetime
from datetime import datetime
#directory = "/home/anunta/cache_paginate/cache.db"
directory = "/home/anunta/cache_paginate"
ttl_time = 1800

rt =  ['All',"Virtual Machines", "Virtual Network", "Storage", "Bandwidth", "Virtual Machines Licenses", "Microsoft Defender For Cloud", "Backup", "Expressroute", "Azure NetApp Files", "Load Balancer", "VPN Gateway", "Azure Database For Postgresql", "Automation", "Azure DNS", "Others"]

class table_paginate:
    def __init__(self ):
        pass

    def storeData1(self, data_dict, count):
        cache = Cache(directory)
        mkey = str(uuid.uuid4())
        if 1:#try:
           cache.set("%s_org" %mkey, data_dict, expire = ttl_time)
           cache.set("%s" %mkey, data_dict, expire = ttl_time)
        cache.close()
        no_of_rows = count
        page_no = 1
        org_ykeys = len(data_dict["tdata"])
        no_of_pages = int(math.ceil(org_ykeys/no_of_rows))
        res_dict = self.getPageData(mkey, page_no, no_of_rows)
        return res_dict


    def storeData(self, data_dict):
        cache = Cache(directory)
        mkey = str(uuid.uuid4())
        if 1:#try:
           cache.set("%s_org" %mkey, data_dict, expire = ttl_time)
           cache.set("%s" %mkey, data_dict, expire = ttl_time)
        cache.close()
        no_of_rows = 10
        page_no = 1
        org_ykeys = len(data_dict["tdata"])
        no_of_pages = int(math.ceil(org_ykeys/no_of_rows))
        res_dict = self.getPageData(mkey, page_no, no_of_rows)
        return res_dict

    def storeData_v1(self, data_dict):
        cache = Cache(directory)
        mkey = str(uuid.uuid4())
        data_dict["org"] = data_dict
        cache.set("%s" %mkey, data_dict, expire = ttl_time)
        cache.close()
        no_of_rows = 10
        page_no = 1
        length = 0
        if data_dict:
            length = len(data_dict["tdata"])
        no_of_pages = int(math.ceil(length/no_of_rows))
        data_dict = self.getPageData(mkey, page_no, no_of_rows)
        data_dict["total_pages"] = no_of_pages
        rec = length
        data_dict["records"] = rec
        return data_dict

    def getPageData(self, key, page_no, no_of_rows, org = False):
        cache = Cache(directory)
        if org:
            stored_data = cache.get("%s_org"%key)
        else:
            stored_data = cache.get(key)
        data = stored_data['tdata']
        cache.close()
        length = len(data)
        if no_of_rows=="all":
           all_data = data[:]
           no_of_pages = int(math.ceil(len(all_data)/10))
           no_of_rows = len(data)
        else:
           all_data = data[(page_no-1) * no_of_rows : ((page_no-1) * no_of_rows) + no_of_rows]
           no_of_pages = int(math.ceil(len(all_data)/no_of_rows))
        rec = length
        no_of_pages = int(math.ceil(length/no_of_rows))
        return {"tdata":all_data, "key": key, "total_pages": no_of_pages, "records": rec}

    def apply_sort(self, sort_order, data, index=0):
        if sort_order == 0:
            data_list = sorted(data["tdata"], key=lambda x: x[index])
            data["tdata"] = data_list

        elif sort_order == 1:
            data_list = sorted(data["tdata"], key=lambda x: x[index], reverse=True)
            data["tdata"] = data_list
        else:
            return data
        return data

    def apply_sort2(self, sort_order, data, index=0):
        if sort_order == 0:
            data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %y"))
            data["tdata"] = data_list

        elif sort_order == 1:
            data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %y"), reverse=True)
            data["tdata"] = data_list
        else:
            return data
        return data

    '''def apply_sort3(self, sort_order, data, index=0):
        if sort_order == 0:
            #data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %Y"))
            #data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %Y %H:%M"))
            data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %Y %H:%M") if ' ' in x[index].strip() and len(x[index].split()) > 3 else datetime.strptime(x[index], "%d %b %Y"))

            data["tdata"] = data_list

        elif sort_order == 1:
            #data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %Y "), reverse=True)
            #data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %Y %H:%M"), reverse = True)
            data_list = sorted(data["tdata"], key=lambda x: datetime.strptime(x[index], "%d %b %Y %H:%M") if ' ' in x[index].strip() and len(x[index].split()) > 3 else datetime.strptime(x[index], "%d %b %Y"), reverse=True)

            data["tdata"] = data_list
        else:
            return data
        return data'''

    def apply_sort3(self, sort_order, data, index=0):
        def sort_key(x):
            date_str = x[index]
            if date_str == "01 Jan 9000":
                return datetime.min
            elif ' ' in date_str.strip() and len(date_str.split()) > 3:
                date_format = "%d %b %Y %H:%M"
            else:
                date_format = "%d %b %Y"
            return datetime.strptime(date_str, date_format)

        if sort_order == 0:
            data_list = sorted(data["tdata"], key=sort_key)
        elif sort_order == 1:
            data_list = sorted(data["tdata"], key=sort_key, reverse=True)
        else:
            return data

        data["tdata"] = data_list
        return data

    def sortData(self, key, no_of_rows, column_id, sort_order, tab_name):
        cache = Cache(directory)
        data = cache.get(key)
        all_data = copy.deepcopy(data)
        if sort_order == 2:
            data = cache.get("%s_org"%key)
        cache.close()
        page_no = 1
        index = 0
        if column_id  == 0:
            if tab_name == "model_detail":
                data = self.apply_sort2(sort_order, data, 0)
            else: 
                data = self.apply_sort(sort_order, data, 0)
            index = 0

        if column_id  == 1:
            data = self.apply_sort(sort_order, data, 1)
            index = 1

        if column_id  == 2:
            if tab_name == "device_page":
                data = self.apply_sort3(sort_order, data, 2)
            else:
                data = self.apply_sort(sort_order, data, 2)

            index = 2

        if column_id  == 3:
            data = self.apply_sort(sort_order, data, 3)
            index = 3

        if column_id  == 4:
            if tab_name == "customer_model":
                data = self.apply_sort3(sort_order, data, 4)
                for row in data['tdata']:
                    for i in range(len(row)):
                        if row[i] == "01 jan 9000":
                            row[i] = '-'
            else:
                data = self.apply_sort(sort_order, data, 4)
            index = 4

        if column_id  == 5:
            data = self.apply_sort(sort_order, data, 5)
            index = 5
        if column_id  == 6:
            data = self.apply_sort(sort_order, data, 6)
            index = 6
        length = len(data["tdata"])
        if no_of_rows == "all":
           no_of_rows = len(data["tdata"])
           start = 0
           end = len(data["tdata"])
        else:
           start = (page_no-1) * no_of_rows
           end = ((page_no-1) * no_of_rows) + no_of_rows
           end = min(end, length)
        ntdata = [data["tdata"][item] for item in range(start, end)]
        ntdata = self.apply_sort(sort_order, {"tdata":ntdata}, index)
        all_data_list = self.apply_sort(sort_order, {"tdata":data["tdata"]}, index)
        all_data["tdata"] = all_data_list["tdata"]
        try:
           cache.set("%s" %key, all_data, expire = ttl_time)
        except Exception as e:
            pass
        cache.close()
        if no_of_rows == 0:
            no_of_rows = 0
        else:
            no_of_pages = int(math.ceil(length/no_of_rows))
            rec = length
            return {"tdata": ntdata, "key": key, "total_pages": no_of_pages, "records": rec}


    def sortData_v1(self, key, page_no, no_of_rows, column_id, sort_order):
        print(directory)
        cache = Cache(directory)
        print(cache)
        data = cache.get(key)
        data_list = data['tdata']
        if sort_order == 2:
            res = self.getPageData( key, page_no, no_of_rows, True)
            return res
        cache.close()
        page_no = 1
        index = 0
        if column_id in [0,1,2,3,4]:
            if sort_order == 1:
                sorted_data = sorted(data_list, key=lambda x: x[column_id])
            else:
                sorted_data = sorted(data_list, key=lambda x: x[column_id], reverse=True)

        if no_of_rows=="all":
           no_of_rows = len(sorted_data)
           ntdata = sorted_data[:]
        else:
           ntdata = sorted_data[(page_no-1) * no_of_rows : ((page_no-1) * no_of_rows) + no_of_rows]
        if 1:
           cache.set("%s" %key, sorted_data, expire = ttl_time)
           data = cache.get(key)
        cache.close()
        no_of_pages = int(math.ceil(len(sorted_data)/no_of_rows))
        rec = len(sorted_data)
        return { "tdata": ntdata, "key": key, "total_pages": no_of_pages, "records": rec}


    def delete_key(self, key):
        return


    def sort_dict_list(self, dict_list, order_list):
        sorted_list = sorted(dict_list, key=lambda x: order_list.index(x.get('subscription')) if x.get('subscription') in order_list else len(order_list))
        for item in dict_list:
            if item not in sorted_list:
                sorted_list.append(item)
        return sorted_list


    def getAllGraphData(self, data_dict):
        key, color_dict_list, date_str, ykeys = data_dict["key"],data_dict["color_dict"], data_dict["date_str"], data_dict['ykeys']
        color_dict = {}
        for temp_dict in color_dict_list:
            color_dict[temp_dict["subscription"]] = temp_dict["color"]
        data = self.cache.get(key)
        try:
            data = ast.literal_eval(data)
        except:
            return {"data": [], 'total':0}
        ntykeys = data["tykeys"]
        if "Total" in ntykeys:
            ntykeys.remove("Total")
        ntdata = []
        other_color = color_dict.get("others", "#2bd")
        total_cnt = 0
        d = []
        for col_data in data["tdata"]:
           if col_data["d_date"]!= date_str:continue
           default_keys = col_data.keys()
           for yelm in ntykeys:
              tmp = {}
              if not str(col_data.get(yelm, "")): continue
              total_cnt+=col_data[yelm]
              if "d_date" in default_keys:
                 tmp["date"] = col_data["d_date"]
              if "name" in default_keys:
                 tmp["subscription"] = yelm
              tmp['color'] = color_dict.get(yelm, other_color)
              tmp["loader"] = "false"
              tmp["price"] = col_data[yelm]
              ntdata.append(tmp)
        for tmp in ntdata:
            for yelm in ntykeys:
                if tmp['subscription'] != yelm:continue
                perc = round(tmp['price']/total_cnt * 1.0,2)
                tmp["p"] = round(perc*100,2)
                tmp['total'] = total_cnt
        sorted_list = self.sort_dict_list(ntdata, ykeys)
        return {"data": sorted_list, 'total':total_cnt}

    def getPageData_csv(self, key, page_no, no_of_rows):
        cache = Cache(directory)
        data = cache.get(key)
        cache.close()
        tdata  = data["tdata"]
        tykeys = data["tykeys"]
        if no_of_rows=="all":
           no_of_rows = len(tykeys)
           ntykeys = tykeys[:]
        else:
           ntykeys = tykeys[(page_no-1) * no_of_rows : ((page_no-1) * no_of_rows) + no_of_rows]
        if "Total" in ntykeys:
            ntykeys.remove("Total")
            ntykeys.insert(0, "Total")

        ntdata = []
        for col_data in tdata:
           tmp = {}
           default_keys = col_data.keys()
           for yelm in ntykeys:
              if not str(col_data.get(yelm, "")): continue
              tmp[yelm] = col_data[yelm]
              if yelm+"_Curr" in default_keys:
                 tmp[yelm+"_Curr"] = col_data[yelm+"_Curr"]
              if yelm+"_cur" in default_keys:
                 tmp[yelm+"_cur"] = col_data[yelm+"_cur"]
              if yelm+"_CID" in default_keys:
                 tmp[yelm+"_CID"] = col_data[yelm+"_CID"]
              if yelm+"_P" in default_keys:
                 tmp[yelm+"_P"] = col_data[yelm+"_P"]
              if yelm+"_A" in default_keys:
                 tmp[yelm+"_A"] = col_data[yelm+"_A"]
              if "d_date" in default_keys:
                 tmp["d_date"] = col_data["d_date"]
              if "name" in default_keys:
                 tmp["name"] = col_data["name"]
              if "name_2" in default_keys:
                 tmp["name_2"] = col_data["name_2"]
           ntdata.append(tmp)
        no_of_pages = int(math.ceil(len(tykeys)/no_of_rows))
        rec = len(tykeys)
        if "Total" in tykeys:
           rec = rec - 1
        return {"tykeys": ntykeys, "tdata": ntdata, "txkeys": data["txkeys"], "key": key, "total_pages": no_of_pages, "records": rec}







if __name__=="__main__":
    data_dict ={"tdata": [
    ['Mode 1', 'k526th09-1345', 'virtual machine', 'azure', '2023-06-15', 16.98, 1],
    ['Mode 2', 'm526th09-9824', 'storage', 'partner', '2024-01-30', 10.55, 3],
    ['Mode 3', 'a526th09-4763', 'bandwidth', 'azure', '2023-08-12', 5.67, 2],
    ['Mode 4', 'c526th09-6985', 'virtual network', 'partner', '2024-03-11', 3.85, 1],
    ['Mode 5', 't526th09-5432', 'virtual machine', 'azure', '2023-05-22', 19.65, 3],
    ['Mode 6', 'x526th09-2490', 'storage', 'partner', '2023-07-03', 13.45, 2],
    ['Mode 7', 'l526th09-3816', 'bandwidth', 'azure', '2024-02-07', 12.23, 1],
    ['Mode 8', 'y526th09-5721', 'virtual network', 'partner', '2024-04-01', 14.50, 3],
    ['Mode 9', 'p526th09-6548', 'virtual machine', 'azure', '2023-11-24', 8.97, 2],
    ['Mode 10', 'u526th09-8735', 'storage', 'partner', '2024-03-21', 11.72, 1],
    ['Mode 11', 'o526th09-4165', 'bandwidth', 'azure', '2023-09-19', 6.89, 3],
    ['Mode 12', 'v526th09-1398', 'virtual network', 'partner', '2023-12-14', 10.33, 2],
    ['Mode 13', 'z526th09-5321', 'virtual machine', 'azure', '2023-02-05', 17.14, 1],
    ['Mode 14', 'n526th09-2953', 'storage', 'partner', '2024-04-05', 2.67, 3],
    ['Mode 15', 'd526th09-4987', 'bandwidth', 'azure', '2023-10-08', 9.45, 2],
    ['Mode 16', 'q526th09-7456', 'virtual network', 'partner', '2023-11-29', 18.99, 1],
    ['Mode 17', 'r526th09-3810', 'virtual machine', 'azure', '2023-05-12', 13.87, 3],
    ['Mode 18', 's526th09-2849', 'storage', 'partner', '2024-02-25', 3.45, 2],
    ['Mode 19', 'e526th09-9825', 'bandwidth', 'azure', '2023-08-25', 11.34, 1],
    ['Mode 20', 'w526th09-5609', 'virtual network', 'partner', '2023-09-01', 16.12, 3],
    ['Mode 21', 'h526th09-1197', 'virtual machine', 'azure', '2023-01-10', 9.77, 2],
    ['Mode 22', 'i526th09-6783', 'storage', 'partner', '2023-07-17', 6.83, 1],
    ['Mode 23', 'g526th09-2941', 'bandwidth', 'azure', '2023-12-28', 14.34, 3],
    ['Mode 24', 'j526th09-8309', 'virtual network', 'partner', '2024-01-03', 1.23, 2],
    ['Mode 25', 'k526th09-7260', 'virtual machine', 'azure', '2023-06-20', 19.89, 1],
    ['Mode 26', 'm526th09-2345', 'storage', 'partner', '2023-03-29', 3.77, 3],
    ['Mode 27', 'a526th09-5234', 'bandwidth', 'azure', '2024-02-10', 7.56, 2],
    ['Mode 28', 'c526th09-7345', 'virtual network', 'partner', '2023-04-05', 2.68, 1],
    ['Mode 29', 't526th09-8732', 'virtual machine', 'azure', '2024-03-16', 12.43, 3],
    ['Mode 30', 'x526th09-1674', 'storage', 'partner', '2023-07-13', 16.89, 2],
    ['Mode 31', 'l526th09-2958', 'bandwidth', 'azure', '2023-10-25', 15.67, 1],
    ['Mode 32', 'y526th09-8734', 'virtual network', 'partner', '2023-09-07', 4.34, 3],
    ['Mode 33', 'p526th09-6724', 'virtual machine', 'azure', '2023-11-17', 19.45, 2],
    ['Mode 34', 'u526th09-3156', 'storage', 'partner', '2023-04-09', 3.34, 1],
    ['Mode 35', 'o526th09-4328', 'bandwidth', 'azure', '2023-12-30', 13.23, 3],
    ['Mode 36', 'v526th09-1573', 'virtual network', 'partner', '2023-03-03', 6.54, 2],
    ['Mode 37', 'z526th09-5834', 'virtual machine', 'azure', '2023-06-18', 8.89, 1],
    ['Mode 38', 'n526th09-9247', 'storage', 'partner', '2024-01-25', 2.56, 3],
    ['Mode 39', 'd526th09-6729', 'bandwidth', 'azure', '2023-10-11', 15.76, 2],
    ['Mode 40', 'q526th09-3925', 'virtual network', 'partner', '2023-09-14', 11.24, 1],
    ['Mode 41', 'r526th09-5634', 'virtual machine', 'azure', '2024-04-07', 17.89, 3],
    ['Mode 42', 's526th09-8972', 'storage', 'partner', '2023-08-23', 7.65, 2],
    ['Mode 43', 'e526th09-1035', 'bandwidth', 'azure', '2023-05-08', 19.44, 1],
    ['Mode 44', 'w526th09-6149', 'virtual network', 'partner', '2024-02-12', 14.68, 3],
    ['Mode 45', 'h526th09-8731', 'virtual machine', 'azure', '2023-11-09', 12.55, 2],
    ['Mode 46', 'i526th09-9376', 'storage', 'partner', '2024-01-15', 5.43, 1],
    ['Mode 47', 'g526th09-7435', 'bandwidth', 'azure', '2024-03-20', 10.12, 3],
    ['Mode 48', 'j526th09-3245', 'virtual network', 'partner', '2023-07-28', 1.09, 2],
    ['Mode 49', 'k526th09-5039', 'virtual machine', 'azure', '2023-09-11', 4.56, 1],
    ['Mode 50', 'm526th09-2973', 'storage', 'partner', '2023-10-13', 18.01, 3]
]
}
    obj = table_paginate()
    key ='09a59340-6df9-4406-ae4b-6681a9de8d43'
    page_no = 1
    no_of_rows = 10
    #obj.getPageData( key, page_no, no_of_rows)
    #jjj
    print(obj.sortData(key, page_no, no_of_rows, 1, 0))
    #kkk
    #jjj
    #obj.storeData(data_dict)
    #obj.storeData(data_dict)
    #obj.delete_key("abc2214c-5f11-4f89-b390-1b6364b2bdab")

