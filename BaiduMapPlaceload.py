# -*- coding: utf-8 -*-

import requests
import json
import pickle
import time


class BaiduMapPlaceload():
    '''
    该类是对于百度地图地点检索服务（又名Place API）的封装
    通过该类，可以便捷地对于全国或者指定行政区域内的关键词地点进行批量下载。类已经对Place API同一级别下只能显示400条信息的现状进行了优化，并将行政区划字典外挂，最大程度提高运行效率。
    
    成员变量共有如下：
    1. ak 初始化时设置的密钥，必填信息
    2. citynum  需要检索的城市代码，在这里使用百度提供的城市代码列表citycode
    3. keyword  检索关键词
    4. flag 该布尔型变量第一阶段用于判断当前页面是否有20条信息(信息满，可以转至下一面继续查找),第二阶段用于判断当前城市是否满400条信息，如果满，返回False，不满返回True
    5. citycontent 是检索的总结果
    
    依赖：
    import requests
    import json
    import time
    '''
    
    def __init__(self,ak,timesleep = 0):
        '''
        初始化函数需要提交一项必要指标ak,非必要指标timesleep
        1. ak 即百度地图api密钥
        2. timesleep 指定每次GET之间的时间间隔，方便规避并发抓取上限报错
        3. citycontent 是该类目前含有的已经加载下来的数据列表
        4. flag 该变量用于在类已经抓取相应数据之后，显示是否是
        '''
        self.ak = ak
        self.flag = True
        self.citycontent = []
        self.timesleep = timesleep
    
    def _detail(self,cityname):
        '''
        detail函数用于判断当前城市是否含有400条以上的检索信息，如果有，则返回True,通知上级函数将搜索范围下沉到区一级
        
        '''
        self.cityname = cityname
        DownloadQuery = 'http://api.map.baidu.com/place/v2/search?query=%s&region=%s&output=json&city_limit=true&page_size=20&page_num=%d&ak=%s'%(self.keyword,self.cityname,19,self.ak) 
        json_content = json.loads(requests.get(DownloadQuery).text,strict=False)
        if len(json_content['results']) < 20:
            return True
        else:
            return False
    
    def _GenStructInfo(self):
        for index in range(self.length):
            if 'address' not in self.citycontent[index]:
                self.citycontent[index]['address'] = ''
            if 'area' not in self.citycontent[index]:
                self.citycontent[index]['area'] = ''
            if 'city' not in self.citycontent[index]:
                self.citycontent[index]['city'] = ''
            if 'detail' not in self.citycontent[index]:
                self.citycontent[index]['detail'] = ''
            if 'name' not in self.citycontent[index]:
                self.citycontent[index]['name'] = ''
            if 'province' not in self.citycontent[index]:
                self.citycontent[index]['province'] = ''   
            if 'street_id' not in self.citycontent[index]:
                self.citycontent[index]['street_id'] = ''
            if 'telephone' not in self.citycontent[index]:
                self.citycontent[index]['telephone'] = ''
            if 'uid' not in self.citycontent[index]:
                self.citycontent[index]['uid'] = ''
    
    def loadall(self,keyword,CityDict,INFO = True):
        '''
        loadall方法用于加载 在当前给出的CityDict字典中所有的城市的关键词检索结果，有两个必须参数与一个可选参数
        1. keyword 检索关键词
        2. CityDict 城市字典，字典的结构为 {'城市名称':[该城市下辖区的列表]}
        3. INFO 该变量用于指示是否显示当然进度
        '''
        self.keyword = keyword
        self.INFO = INFO
        self.CityDict = CityDict
        for unit in list(CityDict.keys()):
            if self._detail(unit):    
                tmptext = BaiduMapPlaceload(self.ak,self.timesleep)
                self.citycontent += tmptext.loadgen(self.keyword,unit)
                if self.INFO is True:
                    print("The city %s had done success ! total %d "%(tmptext.cityname,tmptext.length))
            else:
                tmptext = BaiduMapPlaceload(self.ak,self.timesleep)
                self.citycontent += tmptext._loadsmall(self.keyword,{unit:self.CityDict[unit]})
        return self.citycontent
            
    def _loadsmall(self,keyword,S_Dict,INFO = True):
        '''
        该函数是中间层函数，用于读取大中城市（相关检索信息大于400条）的检索结果
        '''
        self.cityname = list(S_Dict.keys())[0]
        self.keyword = keyword
        self.arealist = S_Dict[self.cityname]
        self.INFO = INFO
        for areaname in self.arealist:
            tmptext = BaiduMapPlaceload(self.ak,self.timesleep)
            self.citycontent += tmptext.loadgen(self.keyword + ' ' + areaname,self.cityname)
            if self.INFO is True:
                print(("The city %s area %s had done success ! total %d ")%(self.cityname,areaname,tmptext.length))
        return self.citycontent
    
    def loadgen(self,keyword,cityname):
        '''
        loadgen 函数用于对单个小城市或大城市的一个片区进行检索
        返回检索到的数据列表
        '''
        self.keyword = keyword
        self.cityname = cityname
        page_num = 0
        while(self.flag):
            DownloadQuery = 'http://api.map.baidu.com/place/v2/search?query=%s&region=%s&output=json&city_limit=true&page_size=20&page_num=%d&ak=%s'%(self.keyword,self.cityname,page_num,self.ak) 
            json_content = json.loads(requests.get(DownloadQuery).text,strict=False)
            if json_content['status'] == 401:
                print('当前并发量已经超过约定并发配额，限制访问')
                return []
            if json_content['status'] == 302:
                print("request over error")
                return []
            
            content = json_content['results']
            if len(content) < 20:
                self.flag = False
            self.citycontent +=  content
            time.sleep(self.timesleep)
            page_num += 1
        self.length = len(self.citycontent)
        if self.length < 400:
            self.flag = True
        else:
            self.flag = False
        self._GenStructInfo()
        return self.citycontent


if __name__ == '__main__':
    
    CityDict = pickle.load(open('CityDict.pkl','rb'))
    S_Dict = { '武汉市':CityDict['武汉市'],'淮北市':CityDict['淮北市'],'东莞市':CityDict['东莞市'] }
    ak = 'RkwfPwjwfrn3P5XZoNKz7BScyor0nZvW'
    tmptext = BaiduMapPlaceload(ak,0.5)
    content = tmptext.loadall('茶馆',S_Dict)
    

    
    
    
    

