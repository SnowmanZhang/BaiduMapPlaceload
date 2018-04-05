# BaiduMapPlaceload

百度地图API数据加载接口(Python)


该类(BaiduMapPlaceload)是对于百度地图地点检索服务（又名Place API）的封装
通过使用该类，可以便捷地对于全国或者指定行政区域内的关键词地点进行批量下载。类已经对Place API同一级别下只能显示400条信息的现状进行了优化，并将行政区划字典外挂，最大程度提高运行效率。
    
成员变量共有如下：
    
1. ak 初始化时设置的密钥，必填信息
2. citynum  需要检索的城市代码，在这里使用百度提供的城市代码列表citycode
3. keyword  检索关键词
4. flag 该布尔型变量第一阶段用于判断当前页面是否有20条信息(信息满，可以转至下一面继续查找),第二阶段用于判断当前城市是否满400条信息，如果满，返回False，不满返回True
5. citycontent 是检索的总结果
    
## 依赖

```python
import requests
import json
import time
```

## 示例

1. 对单个城市进行关键词查找，关键词为"医院"

```python

from BaiduMapPlaceload import BaiduMapPlaceload

hospital = BaiduMapPlaceload(ak,0.5)
hospitallist = hospital.loadgen('医院','淮北市')

```

2. 对全国范围进行关键词查找，关键词依然是"医院"

```python
from BaiduMapPlaceload import BaiduMapPlaceload
import pickle

CityDict = pickle.load(open('CityDict.pkl','rb'))
hospital = BaiduMapPlaceload(ak,0.5)
hospitallist = hospital.loadall('医院',CityDict)

```

## CityDict是什么

