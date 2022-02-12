#!/usr/bin/python
# -*- coding: UTF-8 -*-
import math
#print(round(0.998,2))

#统计重复项 输出重复项的index 不统计None
def Get_Duplicate_ValueIndex(Original_List,Check_Value):
    Index_Value = []
    temlist = [ i for i in Original_List ]
    if Check_Value != None:
        while 1:
            try:
                index_value = temlist.index(Check_Value)
                Index_Value.append(index_value)
                temlist[index_value] = None
            except:
                break

    return Index_Value

#嵌套列表寻找到重复index
def Get_Duplicate_ValueIndex_Nestedlist (Original_List,Check_Value):
    Index_Value = []
    for i in range(0,len(Original_List)):
        index_value = Get_Duplicate_ValueIndex(Original_List[i] ,Check_Value)
        if len(index_value) != 0:
            Index_Value.append([i,index_value])
    return Index_Value


def Get_Mid_Point(Point1,Point2):
    if len(Point1) == 2:
        Mid_P = [(Point1[0]+Point2[0])/2, (Point1[1]+Point2[1])/2]
    if len(Point1) == 3:
        Mid_P = [(Point1[0]+Point2[0])/2, (Point1[1]+Point2[1])/2, (Point1[2]+Point2[2])/2]
    return Mid_P

def Get_Points_Dist(Point1,Point2):
    if len(Point1) == 2:
        Dist = ( (Point1[0]-Point2[0])**2+(Point1[1]-Point2[1])**2 )**0.5
    if len(Point1) == 3:
        Dist = ( (Point1[0]-Point2[0])**2+(Point1[1]-Point2[1])**2 + (Point1[2]-Point2[2])**2 )**0.5

    return Dist


def Add_List(LIST0,LIST1):
    new_LIST = []
    for i in range( 0,len(LIST0) ):
        new_LIST.append( LIST0[i]+LIST1[i] )
    return new_LIST

def Mult_List(LIST0,num):
    new_LIST = []
    for i in range( 0,len(LIST0) ):
        new_LIST.append( LIST0[i]*num )
    return new_LIST

def bubbleSort(objects,keys):
    for i in range(1, len(objects)):
        for j in range(0, len(objects)-i):
            if keys[j] > keys[j+1]:
                objects[j], objects[j + 1] = objects[j + 1], objects[j]
                keys[j],  keys[j + 1] =  keys[j + 1],  keys[j]
    return objects





def main():
    a = [ None ,None ,None ,None ,None ,1,2,34,56,1,]
    print('Get_Duplicate_ValueIndex:',Get_Duplicate_ValueIndex(a,1))
    b = [ [None ,None] ,[None ,None] ,[None ,1,],[2,34,56],[1,5,56,5,456,1]]
    print('Get_Duplicate_ValueIndex_Nestedlist:',Get_Duplicate_ValueIndex_Nestedlist(b,1))

    a=[[1],2,3,4,5,[6]]
    b=[[1],2,3,4,5,[6]]
    print(a==b)

    P1 = (2,4)
    P2 = (7,9)
    print(Get_Mid_Point(P1,P2))
    print(Get_Points_Dist(P1,P2))

    P1 = (2,4,6)
    P2 = (7,9,11)
    print(Get_Mid_Point(P1,P2))
    print(Get_Points_Dist(P1,P2))

    print(Add_List(P1,P2))
    print(Mult_List(P1,100))


    print(180*math.atan(1)/math.pi)


if __name__ == '__main__':
    main()
    print(__name__)
