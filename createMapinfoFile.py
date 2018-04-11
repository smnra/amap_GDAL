#!/usr/bin/python
# -*- coding: CP936 -*-


import sys
import os
import osr
try:
    from osgeo import ogr,gdal
except:
    import ogr

# ��GDAL �� feature ָ�ľ��� mapinfo�е� �� �� ����  �����
#driver = ogr.GetDriverByName("ESRI Shapefile")    # .shp �ļ�����
#driver = ogr.GetDriverByName("Mapinfo File")      # mapinfo   .tab �ļ�����


gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
# ��ȡ�ֶ�����ֵʱ���ã���������������
gdal.SetConfigOption("SHAPE_ENCODING","UTF-8")


class CreateMapFeature():
    def __init__(self,path):
        self.path = path
        self.driver = ogr.GetDriverByName("Mapinfo File")  # mapinfo   .tab �ļ�����

    def newFile(self, filename, fieldList):
        #�������ļ�
        self.filename = filename                        #filename�ļ���,������·�� �ַ�����ʽ
        self.fieldList = fieldList                      #fieldList ,ͼ��ı���ֶ�  �б��ʽ,(("index", 0), ("name",(4,255)), ("lon", 2), ("lat" , 2))
                                                        # �б�Ϊ �ֶε����� �� ��������, 0�������� , 2 ���� ������ , 4�����ַ���(������ַ�����ʽ ���б�ĵڶ���Ԫ��Ϊ 4���ַ����ĳ��ȵ��б�
        if os.path.isfile(self.path + self.filename):  # ����ļ����ڵĻ� ������һ���ļ���
            self.filename = self.path + r"/new_" + self.filename
            print("File is exist,Create anothor, Name is :" + self.filename)
        else:
            self.filename = self.path + self.filename
            print("Create file, Name is :" + self.filename)
        self.dataSource = self.driver.CreateDataSource(self.filename)        # ���� �ļ�
        self.newLayer = self.dataSource.CreateLayer('newLayer')  # ����ͼ��testLayer2
        for self.field in self.fieldList:                 #�����ֶ����ֵ��е������ֶ�
            if self.field[1] == 0 :
                self.fieldType = ogr.OFTInteger
                self.newField = ogr.FieldDefn(self.field[0], self.fieldType)  # ���һ�����ֶ�
            elif self.field[1] == 2 :
                self.fieldType = ogr.OFTReal
                self.newField = ogr.FieldDefn(self.field[0], self.fieldType)  # ���һ�����ֶ�
            elif self.field[1][0] == 4 :
                self.fieldType = ogr.OFTString
                self.newField = ogr.FieldDefn(self.field[0], self.fieldType)  # ���һ�����ֶ�
                self.newField.SetWidth(self.field[1][1])          #������ֶ����ַ����������Ҫָ�����
            self.newLayer.CreateField(self.newField)  # �����ֶ�ָ�䵽layer
        return  self.newLayer                           # ����ֵΪ�½��ļ���ͼ�� Layer ����

    def deleteFile(self, filename):
        self.filename = filename
        self.filename = self.path + self.filename
        if os.path.isfile(self.filename):  # ����ļ����ڵĻ�ɾ��
            self.driver.DeleteDataSource(self.filename)  # ɾ��һ���ļ�
            print("File well be delete :" + self.filename)
        else:
            print("File is not exist :" + self.filename + ",Plase Check it!")

    def createPoint(self, newLayer, x, y, values = []):        #layer ΪҪ��Feature��ӵ��� Layer x ,y Ϊ ���� values Ϊ�ֶ�ֵ�б�
        self.newLayer = newLayer
        self.x = x
        self.y = y
        self.values = values
        # ���һ���µ�Feature
        self.featureDefn = self.newLayer.GetLayerDefn()  # ��ȡFeature ������
        self.newFeature = ogr.Feature(self.featureDefn)  # ����Feature
        # �趨������״
        self.point = ogr.Geometry(ogr.wkbPoint)  # ����һ����
        self.point.AddPoint(self.x, self.y)  # ���� point������
        self.newFeature.SetGeometry(self.point)  # ����Featur�ļ�����״Ϊpoint
        for self.tmpField,self.tmpValue  in zip(self.fieldList, self.values) :
            #�趨Featurĳ�ֶε���ֵ,�������� index �ֶε�ֵΪ 12
            self.newFeature.SetField(self.tmpField[0], self.tmpValue)
        # ��newFeatureд�� self.layer
        self.newLayer.CreateFeature(self.newFeature)
        self.point.Destroy()  # �ͷŶ����ڴ�
        return  self.newFeature                  # ����ֵΪFeature ����


    def createLine(self, newLayer,pointList, fieldValues = []):           #layer ΪҪ��Feature��ӵ��� Layer , points Ϊ���ߵĽڵ�x,y������б��� :((1,1),(3,3),(4,2))
        self.newLayer = newLayer
        self.pointList = pointList
        self.fieldValues = fieldValues
        # ���һ���µ�Feature
        self.featureDefn = self.newLayer.GetLayerDefn()  # ��ȡFeature ������
        self.newFeature = ogr.Feature(self.featureDefn)  # ����Feature
        # �趨������״
        self.line = ogr.Geometry(ogr.wkbLineString)  # ����һ������
        for self.pointPos in self.pointList :
            self.line.AddPoint(self.pointPos[0], self.pointPos[1])  # ѭ��������еĽڵ�
        self.newFeature.SetGeometry(self.line)  # ����Featur�ļ�����״Ϊline
        #�趨Featurĳ�ֶε���ֵ,�������� index �ֶε�ֵΪ 12
        #self.newFeature.SetFieldStringList(self.fieldValues)
        for self.tmpField,self.tmpValue  in zip(self.fieldList, self.fieldValues) :
            #�趨Featurĳ�ֶε���ֵ,�������� index �ֶε�ֵΪ 12
            self.newFeature.SetField(self.tmpField[0], self.tmpValue)
        # ��newFeatureд�� self.layer
        self.newLayer.CreateFeature(self.newFeature)
        self.line.Destroy()  # �ͷŶ����ڴ�
        return  self.newFeature                  # ����ֵΪFeature ����

    def createPolygon(self, newLayer,ringList, fieldValues = []):           #layer ΪҪ��Feature��ӵ��� Layer ,
        self.newLayer = newLayer                              #rings Ϊ��յ�����ring ���б�,������1������2��Ԫ��(�ڻ����⻷)
        self.ringList = ringList                   #��:1����:((0,0),(0,10),(10,10),(10,0))     2����: (((0,0),(0,10),(10,10),(10,0)),((2.5,2.5),(7.5,2.5),(7.5,7.5),(2.5,7.5)))
        self.fieldValues = fieldValues
        # ���һ���µ�Feature
        self.featureDefn = self.newLayer.GetLayerDefn()  # ��ȡFeature ������
        self.newFeature = ogr.Feature(self.featureDefn)  # ����Feature
        # �趨������״
        self.polygon = ogr.Geometry(ogr.wkbPolygon)  # ����polygon����
        self.ring = []      #����ring���б�
        for i,self.ringPos in enumerate(self.ringList) :
            self.ring.append(ogr.Geometry(ogr.wkbLinearRing)) # ����һ���� ring ����ӵ��б� self.ring ��
            for self.tmpRing in self.ringPos :
                self.ring[i].AddPoint(float(self.tmpRing[0]), float(self.tmpRing[1]))  #ѭ����ӵ㵽Ring��
            self.ring[i].CloseRings()  # ��CloseRings�պ�Ring��
            self.polygon.AddGeometry(self.ring[i])   # �ѻ� ring��ӵ�  polygon
        self.newFeature.SetGeometry(self.polygon)   #����Featur�ļ�����״Ϊpolygon (����newFeature Ϊ ���� polygon )
        #�趨Featurĳ�ֶε���ֵ,�������� index �ֶε�ֵΪ 12
        for self.tmpField,self.tmpValue  in zip(self.fieldList, self.fieldValues) :
            #�趨Featurĳ�ֶε���ֵ,�������� index �ֶε�ֵΪ 12
            self.newFeature.SetField(self.tmpField[0], self.tmpValue)
        # ��newFeatureд�� self.layer
        self.newLayer.CreateFeature(self.newFeature)
        #self.polygon.Destroy()  # �ͷŶ����ڴ�
        return  self.newFeature                  # ����ֵΪFeature ����


    def setFieldValue(self,newLayer,valueList):
        self.newLayer = newLayer
        self.valueList = valueList
        for self.tmpField,self.tmpValue  in zip(self.fieldList, self.valueList) :
            #�趨Featurĳ�ֶε���ֵ,�������� index �ֶε�ֵΪ 12
            self.newFeature.SetField(self.tmpField[0], self.tmpValue)

    def close(self,layer):
        layer.ResetReading()  # ��λ
        self.dataSource.Destroy()  # �ر�����Դ���൱���ļ�ϵͳ�����еĹر��ļ�




if __name__ == '__main__':
    newMap = CreateMapFeature('E:\\����\\����\\����\\�о�\\Python\\python3\\gaode_range\\tab\\')
    fieldList = (("index",(4,255)), ("name",(4,255)), ("lon", 2), ("lat" , 2))
    newLayer = newMap.newFile('assss.tab', fieldList)

    #ע�� shape �Ľṹ�� mapinfo��ͼ��ṹ����������ͬ,mapinfoһ��ͼ��Layer�п��԰�������Feature(��,�� ��).
    # ����һ��shape �� Layerֻ����һ�� Frature ����ᱨ�� ERROR 1: Attempt to write non-point (POLYGON) geometry to point shapefile.
    #newMap.createPoint(newLayer, 10, 10,("��ɶ����","����˹������",23.5,102.55))
    #newMap.createPoint(newLayer, 10, 15,("��ɶ����","����˹������",23.6,102.65))
    #newMap.createPoint(newLayer, 10, 17,("��ɶ����","����˹������",23.7,102.75))
    newMap.createPoint(newLayer, 108.930221,  34.239893,("��ɶ����","����˹������",23.8,102.85))

    #newMap.createLine(newLayer,((0,0),(3,4),(5,6),(7,8)),("��ɶ����","����˹������",23.8,102.85))
    #newMap.createLine(newLayer,((10,10),(8,9),(7,6),(3,5)),("��ɶ����","����˹������",23.8,102.85))

    region = [[[108.920221, 34.229893], [108.919324, 34.228498], [108.918226, 34.228962], [108.91807, 34.228619]]]
    newMap.createPolygon(newLayer, region,("ssssss","aaaaaaa",23.8,102.85))

    newMap.close(newLayer)