import pyautocad
import sqlite3
import math
import copy
import numpy as np
import Tools


class YJKFloor:
    def __init__(self) :
        self.No_ = 0          #YJK 自然层号 从1开始排
        self.StdFlrID = 0     #YJK 标准层号  也是各层构件索引层号
        self.LevelB = 0.0     #YJK 层底标高
        self.Height = 0.0     #YJK 层高

class YJKSection:
    def __init__(self) :
        self.ID =  0                        #YJK 截面ID  类型为int
        self.YJK_Define_Name = 'KZ'         #YJK 标注截面名  已在YJK中人为定义好
        self.Self_Define_Name = 'KZ'        #自定义 标注截面名  按照截面从大到小顺序定义
        self.Mat = 5                        #YJK 材质   5钢材 6混凝土 10刚体 16轻骨料混凝土
        self.Kind = 3                       #YJK 截面类型  1矩形  2H形 3圆形  7箱型 □  8圆管 P 26热轧型钢
        self.ShapeName = '123'              #YJK shape value 转化成截面名  26 [450, 200, 14, 9] ---- H450X200X9X14
        self.ShapeData = 123                #YJK shape value 转化成与截面名对应的截面数据信息  H450X200X9X14 ----- [450, 200, 9, 14]
        self.ShapeArea = 0                  #截面面积

class YJKColum:
    def __init__(self) :
        self.JtID = [ 0 ]                  #YJK Joint号   类型为int
        self.CenterCoordinate = [ 0 ,0 ]
        self.Section = 0                   #YJKSection 类
        self.Rotation = 0
        self.CornerCoordinate = []
        self.TaggingCoordinate = []

    def Get_Corner_Tagging_Coordinate(self):
        C_Coor = self.CenterCoordinate
        ShapeData = self.Section.ShapeData
        if self.Section.Kind == 1 :
            h = ShapeData[1]
            b = ShapeData[0]
        elif self.Section.Kind == 2 or self.Section.Kind == 26 or self.Section.Kind == 7 :
            h = ShapeData[0]
            b = ShapeData[1]
        elif self.Section.Kind == 3 or self.Section.Kind == 8  :
            self.Rotation = 0
            h = ShapeData[0]
            b = ShapeData[0]
        else :
            h = ShapeData[1]
            b = ShapeData[0]

        C_Sect = [h,b]

        if self.Rotation == 0 :
            cp1 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([ C_Sect[1]/2, C_Sect[0]/2,0]))
            cp2 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([ C_Sect[1]/2,-C_Sect[0]/2,0]))
            cp3 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([-C_Sect[1]/2,-C_Sect[0]/2,0]))
            cp4 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([-C_Sect[1]/2, C_Sect[0]/2,0]))
            self.CornerCoordinate = [cp1,cp2,cp3,cp4]
        else:
            r = self.Rotation
            x,y = C_Sect[1]/2, C_Sect[0]/2
            x1 = x*math.cos(r) - y*math.sin(r)
            y1 = x*math.sin(r) + y*math.cos(r)
            cp1 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([ x1, y1,0]))

            x,y = C_Sect[1]/2,-C_Sect[0]/2
            x1 = x*math.cos(r) - y*math.sin(r)
            y1 = x*math.sin(r) + y*math.cos(r)
            cp2 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([ x1, y1,0]))

            x,y = -C_Sect[1]/2,-C_Sect[0]/2
            x1 = x*math.cos(r) - y*math.sin(r)
            y1 = x*math.sin(r) + y*math.cos(r)
            cp3 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([ x1, y1,0]))

            x,y = -C_Sect[1]/2, C_Sect[0]/2
            x1 = x*math.cos(r) - y*math.sin(r)
            y1 = x*math.sin(r) + y*math.cos(r)
            cp4 = list(np.array([C_Coor[0],C_Coor[1],0]) + np.array([ x1, y1,0]))

            self.CornerCoordinate = [cp1,cp2,cp3,cp4]


        C_centerP_Negtive = Tools.Mult_List( self.CenterCoordinate , -1 )
        if self.Section.Kind == 3 or self.Section.Kind == 8  :
            Vector = Tools.Mult_List( Tools.Add_List( self.CornerCoordinate[0], C_centerP_Negtive ), 0.5**0.5 )
            self.TaggingCoordinate = Tools.Add_List( self.CenterCoordinate, Vector )
        else :

            keys = []
            for each in self.CornerCoordinate :
                relative_CornerCoordinate = Tools.Add_List(each,C_centerP_Negtive)
                keys.append(relative_CornerCoordinate[1]*10**10+relative_CornerCoordinate[0])
            C_Coor = [ i for i in self.CornerCoordinate]
            self.TaggingCoordinate = Tools.bubbleSort(C_Coor,keys)[-1]

class YJKBeam:
    def __init__(self) :
        self.Grid = [ 0 , 1 ]                                     # 无嵌套 顺序排列
        self.JtID = [ 0 , 1 , 2 ]                                 # 无嵌套 顺序排列
        self.Coordinate = [ [(0 ,0), (1,1)], [(0 ,0), (1,1)] ]    # 与Grid一一对应
        self.Connection = [ [1,3], [0,0] ]                        # 与Grid一一对应 0 o r3代表刚接 1代表铰接
        self.Rank = None                                          # 主梁为0   依次往后推
        self.Overhanging = 0                                      # 是否悬挑  0 false  1 ture
        self.Section = 0                                          # 实际上会是一个 YJKSection 类
        self.Length = 1000
        self.Vector = [0,1]
        self.TaggingCoordinate = [1,0]                            # 文字标注位置
        self.TaggingRotation = 0                                  # 文字标注需转动角度


    def reverseBeam(self):
        self.Grid.reverse()
        self.JtID.reverse()
        self.Coordinate.reverse()
        self.Connection.reverse()
        #print(self.Connection)
        #print(self.Coordinate)
        for i in range(0,len(self.Connection)):
            self.Connection[i].reverse()
            self.Coordinate[i].reverse()
        self.getBeamProperty()

    # 合并成功需满足 1.两根梁标识向量相同或相反 2.两根梁存在相同节点 3.两根梁截面相同 4.共节点处两根梁均为刚接
    def mergeBeam(self, AddedBeam) :

        if round(abs(self.Vector[0]*AddedBeam.Vector[0] + self.Vector[1]*AddedBeam.Vector[1] ) , 3 ) == 1:

            if self.JtID[-1] == AddedBeam.JtID[0]:
                if self.Section.ID == AddedBeam.Section.ID :
                    if  self.Connection[-1][-1] != 1 and AddedBeam.Connection[0][0] != 1 :
                        #print('success')
                        del AddedBeam.JtID[0]
                        self.Grid.extend( AddedBeam.Grid )
                        self.JtID.extend( AddedBeam.JtID )
                        self.Coordinate.extend( AddedBeam.Coordinate )
                        self.Connection.extend( AddedBeam.Connection )
                        self.getBeamProperty()
                        return 'success'

            elif self.JtID[-1] == AddedBeam.JtID[-1] and self.JtID[0] != AddedBeam.JtID[0]  :
                if self.Section.ID == AddedBeam.Section.ID :
                    if  self.Connection[-1][-1] != 1 and AddedBeam.Connection[-1][-1] != 1 :
                        #print('success')
                        AddedBeam.reverseBeam()
                        del AddedBeam.JtID[0]
                        self.Grid.extend( AddedBeam.Grid )
                        self.JtID.extend( AddedBeam.JtID )
                        self.Coordinate.extend( AddedBeam.Coordinate )
                        self.Connection.extend( AddedBeam.Connection )
                        self.getBeamProperty()
                        return 'success'

            else :
                return "fail"
        else:
            return "fail"

    # 从breakJt处打断梁  沿着Vector方向  beam0 为前半段  beam1为后半段   若打断节点为起点或终点  返回[self , None]
    def breakBeam(self, breakJt) :
        if breakJt in self.JtID :

            if breakJt != self.JtID[0] and breakJt != self.JtID[-1] :
                Beam_0 = YJKBeam() #前半段
                Beam_1 = YJKBeam() #后半段
                Break_Jt_Index = self.JtID.index(breakJt)

                Beam_0.Grid = [ self.Grid[i] for i in range(0,Break_Jt_Index) ]
                Beam_1.Grid = [ self.Grid[i] for i in range(Break_Jt_Index,len(self.Grid)) ]

                Beam_0.JtID = [ self.JtID[i] for i in range(0,Break_Jt_Index+1) ]
                Beam_1.JtID = [ self.JtID[i] for i in range(Break_Jt_Index,len(self.JtID)) ]

                Beam_0.Coordinate = [ self.Coordinate[i] for i in range(0,Break_Jt_Index) ]
                Beam_1.Coordinate = [ self.Coordinate[i] for i in range(Break_Jt_Index,len(self.Grid)) ]

                Beam_0.Connection = [ self.Connection[i] for i in range(0,Break_Jt_Index) ]
                Beam_1.Connection = [ self.Connection[i] for i in range(Break_Jt_Index,len(self.Grid)) ]

                Beam_0.Section = self.Section
                Beam_1.Section = self.Section

                Beam_0.getBeamProperty()
                Beam_1.getBeamProperty()
                return [Beam_0, Beam_1]
            else :
                return [self, None]

    def getBeamProperty(self) :
        x1 = self.Coordinate[0][0][0]
        x2 = self.Coordinate[-1][-1][0]
        y1 = self.Coordinate[0][0][-1]
        y2 = self.Coordinate[-1][-1][-1]
        self.Length = ( (x1 - x2)**2 + (y1 - y2)**2 )**0.5
        self.Vector = [ (x2 - x1)/self.Length , (y2 - y1)/self.Length ]

        normal_Vector = [ -self.Vector[1],self.Vector[0] ]
        if round(normal_Vector[1],4) == 0 :
            normal_Vector = [ -1 , 0 ]
        elif normal_Vector[1] < 0 :
            normal_Vector = Tools.Mult_List(normal_Vector,-1)


        Beam_mid_point = Tools.Get_Mid_Point( [x1,y1],[x2,y2] )
        self.TaggingCoordinate = Tools.Add_List( Beam_mid_point, Tools.Mult_List(normal_Vector,100) )

        if normal_Vector[1] != 0:
            self.TaggingRotation = -1 * math.atan(normal_Vector[0]/normal_Vector[1])
        if normal_Vector[1] == 0:
            self.TaggingRotation = math.pi/2

class YJKData:

    #输入参数floor：为自然层号,从 1 开始排
    #输入参数BaseFloor：为自然层号,也从 1 开始排且默认为 1
    def __init__(self,fileDir,floor,Basefloor = 1):
        self.fileDir = fileDir
        self.floor = self.Get_All_FloorData()[floor-1].StdFlrID                 #由YJK-CAD模块输入  值为欲绘制楼层的 StdFlrID
        self.Basefloor = self.Get_All_FloorData()[Basefloor-1].StdFlrID         #基准层默认为首层
        self.CAD_Base_Coor = self.get_CAD_Base_Coor()                           #基准层最右下柱中心点
        print('1658485',self.CAD_Base_Coor)

    #得到全楼的相对原点
    def get_CAD_Base_Coor(self):

        CAD_Base_Coor = None#[0,0]

        #得到basefloor的所有JtID
        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()
        sql = '''SELECT JtID FROM tblColSeg WHERE StdFlrID = %s ''' %(self.Basefloor)
        cursor.execute(sql)
        JtID_list = cursor.fetchall()

        #JtID转化坐标
        JtC_list = self.Trans_JtID_2_Coordinate(JtID_list,get_relative_coor = 0)

        for i in range(0, len(JtC_list)):
            success_find_Base = 1
            for ii in range(0, len(JtC_list)):
                Vector = Tools.Add_List( JtC_list[ii], Tools.Mult_List(JtC_list[i],-1) )
                if Vector[0] <= 0 and Vector[1] <= 0:
                    if ii != i :
                        success_find_Base = 0
                        break
            if success_find_Base :
                CAD_Base_Coor = JtC_list[i]
                break
        return CAD_Base_Coor

    #得到楼层数据
    def Get_All_FloorData(self):
        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()
        sql = '''SELECT No_ FROM tblFloor '''
        cursor.execute(sql)
        all_No_ = [ i[0] for i in cursor.fetchall() ]
        all_Floor = []
        for each in all_No_:
            tem_floor = YJKFloor()
            tem_floor.No_ = each

            sql = '''SELECT StdFlrID FROM tblFloor WHERE No_ = %s ''' %(each)
            cursor.execute(sql)
            tem_floor.StdFlrID = cursor.fetchall()[0][0]

            sql = '''SELECT LevelB FROM tblFloor WHERE No_ = %s ''' %(each)
            cursor.execute(sql)
            tem_floor.LevelB = cursor.fetchall()[0][0]

            sql = '''SELECT Height FROM tblFloor WHERE No_ = %s ''' %(each)
            cursor.execute(sql)
            tem_floor.Height = cursor.fetchall()[0][0]

            all_Floor.append(tem_floor)


        return all_Floor  #[(int,),...(int,),]

    # 得到所有梁柱截面类的列表
    def Trans_Section_Info(self):  #输出所有的梁截面类及柱截面类

        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()

        def getAllSection(AllShapeVal) :
            AllSection = []
            for i in range( 0, len(AllShapeVal) ) :
                tem_section = YJKSection()
                ShapeVal = AllShapeVal[i]
                ShapeVal = ShapeVal[0].split(',')
                ShapeVal = [int(i) for i in ShapeVal if i !='']

                #1矩形
                if ShapeVal[0] == 1 :
                    tem_section.Kind = ShapeVal[0]
                    del ShapeVal[0]
                    tem_section.ID = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.Mat = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_Shape = [i for i in ShapeVal if i != 0]
                    tem_section.ShapeName = str(tem_Shape[0])+'X'+str(tem_Shape[1])
                    tem_section.ShapeData = [ tem_Shape[0], tem_Shape[1] ]
                    tem_section.ShapeArea = tem_section.ShapeData[0]*tem_section.ShapeData[1]





                #2H形
                elif ShapeVal[0] == 2 :
                    tem_section.Kind = ShapeVal[0]
                    del ShapeVal[0]
                    tem_section.ID = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.Mat = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_Shape = [i for i in ShapeVal if i != 0]
                    tem_section.ShapeName = "H "+str(tem_Shape[1])+'X'+str(tem_Shape[2])+'X'+str(tem_Shape[0])+'X'+str(tem_Shape[3])
                    tem_section.ShapeData = [ tem_Shape[1], tem_Shape[2], tem_Shape[0], tem_Shape[3] ]
                    tem_section.ShapeArea = 2*tem_section.ShapeData[1]*tem_section.ShapeData[3] + (tem_section.ShapeData[0]-2*tem_section.ShapeData[3])*tem_section.ShapeData[2]

                #3圆形
                elif ShapeVal[0] == 3 :
                    tem_section.Kind = ShapeVal[0]
                    del ShapeVal[0]
                    tem_section.ID = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.Mat = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_Shape = [i for i in ShapeVal if i != 0]
                    tem_section.ShapeName = str(tem_Shape[0])
                    tem_section.ShapeData = [ tem_Shape[0] ,  tem_Shape[0] ]
                    tem_section.ShapeArea = int(math.pi*(tem_section.ShapeData[0]**2)/4)

                #7箱型 □
                elif ShapeVal[0] == 7 :
                    tem_section.Kind = ShapeVal[0]
                    del ShapeVal[0]
                    tem_section.ID = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.Mat = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_Shape = [i for i in ShapeVal if i != 0]
                    tem_section.ShapeName = "□ "+str(tem_Shape[1])+'X'+str(tem_Shape[0])+'X'+str(tem_Shape[3])+'X'+str(tem_Shape[2])
                    tem_section.ShapeData = [ tem_Shape[1], tem_Shape[0], tem_Shape[3], tem_Shape[2] ]
                    tem_section.ShapeArea = 2*tem_section.ShapeData[1]*tem_section.ShapeData[3] + 2*(tem_section.ShapeData[0]-2*tem_section.ShapeData[3])*tem_section.ShapeData[2]

                #8圆管 P
                elif ShapeVal[0] == 8 :
                    tem_section.Kind = ShapeVal[0]
                    del ShapeVal[0]
                    tem_section.ID = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.Mat = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_Shape = [i for i in ShapeVal if i != 0]
                    tem_section.ShapeName = "P "+str(tem_Shape[0])+'X'+str(int(tem_Shape[0])-int(tem_Shape[1]))
                    tem_section.ShapeData = [ tem_Shape[0], int(tem_Shape[0])-int(tem_Shape[1]) ]
                    tem_section.ShapeArea = int(math.pi*(tem_section.ShapeData[0]**2)/4 - math.pi*(tem_section.ShapeData[1]**2)/4)

                #26热轧型钢
                elif ShapeVal[0] == 26 :
                    tem_section.Kind = ShapeVal[0]
                    del ShapeVal[0]
                    del ShapeVal[0]
                    del ShapeVal[0]
                    tem_section.ID = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.Mat = ShapeVal[-1]
                    del ShapeVal[-1]
                    del ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_Shape = [i for i in ShapeVal if i != 0]
                    tem_section.ShapeName = "H "+str(tem_Shape[0])+'X'+str(tem_Shape[1])+'X'+str(tem_Shape[3])+'X'+str(tem_Shape[2])
                    tem_section.ShapeData = [ tem_Shape[0], tem_Shape[1], tem_Shape[3], tem_Shape[2] ]
                    tem_section.ShapeArea = 2*tem_section.ShapeData[1]*tem_section.ShapeData[3] + (tem_section.ShapeData[0]-2*tem_section.ShapeData[3])*tem_section.ShapeData[2]

                elif ShapeVal[0] != 26 :
                    tem_section.Kind = ShapeVal[0]
                    del ShapeVal[0]
                    tem_section.ID = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.Mat = ShapeVal[-1]
                    del ShapeVal[-1]
                    tem_section.ShapeData = [i for i in ShapeVal if i != 0]
                    tem_section.ShapeName = 'Undefine' + str(i)

                AllSection.append(tem_section)

            for i in range( 0,len(AllSection) ) :

                sql = ''' SELECT ShapeVal FROM tblProperty WHERE ID = %s ''' %( AllSection[i].ID )
                conn.text_factory = lambda x : str(x, encoding='gbk', errors='ignore')
                cursor.execute(sql)
                JYK_Section_Name = cursor.fetchall()

                if len( JYK_Section_Name ) > 0 :
                    AllSection[i].YJK_Define_Name = JYK_Section_Name[0][0]

                else :
                    AllSection[i].YJK_Define_Name = 'Undefine'+ str(i)
                #print(each.Name)

            return AllSection

        sql = ''' SELECT ShapeVal FROM tblColSect '''
        cursor.execute(sql)
        All_Colum_ShapeVal = cursor.fetchall() #得到所有 ShapeVal 栏的数据
        All_Colum_Section = getAllSection(All_Colum_ShapeVal)

        keys = [ i.Mat*10**21 + i.Kind*10**19 + i.ShapeData[0]*10**14 + i.ShapeData[1]*10**9 + i.ShapeArea  for i in All_Colum_Section ]
        All_Colum_Section = Tools.bubbleSort(All_Colum_Section,keys)
        #定义钢柱的编号
        Steel_C_Sect_num = 0
        for i in range(0,len(All_Colum_Section)):
            if All_Colum_Section[i].Mat == 5 :
                Steel_C_Sect_num += 1
                All_Colum_Section[i].Self_Define_Name = 'GKZ' + str(Steel_C_Sect_num)


        sql = ''' SELECT ShapeVal FROM tblBeamSect '''
        cursor.execute(sql)
        All_Beam_ShapeVal = cursor.fetchall() #得到所有 ShapeVal 栏的数据
        All_Beam_Section = getAllSection(All_Beam_ShapeVal)

        keys =[ i.Mat*10**21 + i.Kind*10**19 + i.ShapeData[0]*10**14 + i.ShapeData[1]*10**9 + i.ShapeArea for i in All_Beam_Section ]
        All_Beam_Section = Tools.bubbleSort(All_Beam_Section,keys)
        #定义钢梁的编号
        Steel_B_Sect_num = 0
        for i in range(0,len(All_Beam_Section)):
            if All_Beam_Section[i].Mat == 5 :
                Steel_B_Sect_num += 1
                All_Beam_Section[i].Self_Define_Name = 'GL' + str(Steel_B_Sect_num)


        return [All_Colum_Section, All_Beam_Section]

    # 柱节点列表(单层柱所有节点号)
    def Get_Colum_Jt_list(self):
        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()
        sql = '''SELECT JtID FROM tblColSeg WHERE StdFlrID = %s ''' %(self.floor)
        cursor.execute(sql)
        C_JtID = cursor.fetchall()
        return C_JtID  #[(int,),...(int,),]

    # 梁线列表 （单层所有梁线）
    def Get_Beam_Grid_list(self):
        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()
        sql = '''SELECT GridID FROM tblBeamSeg WHERE StdFlrID = %s ''' %(self.floor)
        cursor.execute(sql)
        B_GridID = cursor.fetchall()

        return B_GridID   #[(int,),...(int,),]

    # 梁节点列表 （单层梁所有节点号）
    def Get_Beam_Jt_list(self):

        B_JtID = [] #[(Jt1ID,Jt2ID),...(Jt1ID,Jt2ID)]

        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()

        B_GridID = self.Get_Beam_Grid_list() #[(int,),...(int,),]

        for i in range(0,len(B_GridID)):

            sql = '''SELECT Jt1ID FROM tblGrid WHERE StdFlrID = %s AND ID = %s ''' %(self.floor , B_GridID[i][0])
            cursor.execute(sql)
            Jt1ID = cursor.fetchall() #[(int,)]

            sql = '''SELECT Jt2ID FROM tblGrid WHERE StdFlrID = %s AND ID = %s ''' %(self.floor , B_GridID[i][0])
            cursor.execute(sql)
            Jt2ID = cursor.fetchall() #[(int,)]

            Temp_J12 = (Jt1ID[0][0], Jt2ID[0][0])

            B_JtID.append(Temp_J12)

        return B_JtID #[(Jt1ID,Jt2ID),...(Jt1ID,Jt2ID)] #[(Jt1ID,Jt2ID),...(Jt1ID,Jt2ID)]

    # 梁刚铰接信息列表
    def Get_Beam_Connection_list(self):

        Beam_Connection = [] #[(B_Start_Connection,B_End_Connection),...(B_Start_Connection,B_End_Connection)]

        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()

        sql = '''SELECT ID FROM tblBeamSeg WHERE StdFlrID = %s ''' %(self.floor)
        cursor.execute(sql)
        Beam_ID = cursor.fetchall() #[(int,)]


        for i in range(0,len(Beam_ID)):

            sql = '''SELECT ShapeVal FROM tblProperty WHERE ID = %s AND Name = "SpBeam" ''' %(Beam_ID[i][0] )
            conn = sqlite3.connect(self.fileDir)
            cursor = conn.cursor()
            cursor.execute(sql)
            Property = cursor.fetchall()
            #print(Property)
            Property = Property[0][0] #[(int,)]

            Property = Property.strip(',').split(',')
            B_Start_Connection = int(float(Property[0]))
            B_End_Connection = int(float(Property[1]))

            Temp_Connection12 = [B_Start_Connection, B_End_Connection]

            Beam_Connection.append(Temp_Connection12)
        #print(Beam_Connection)
        return Beam_Connection #[(B_Start_Connection,B_End_Connection),...(B_Start_Connection,B_End_Connection)]

    # 梁截面列表
    def Get_Beam_Section_list(self):

        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()

        All_Section_List = self.Trans_Section_Info()[1]
        All_Section_List_ID = [i.ID for i in All_Section_List]

        Beam_Section = []

        #template_beam_section = {'ID':0,'Name':0,'Mat':0,'Kind':0,'Shape':0}

        sql = '''SELECT ID FROM tblBeamSeg WHERE StdFlrID = %s ''' %(self.floor)
        cursor.execute(sql)
        Beam_ID = cursor.fetchall() #[(int,)]

        for i in range(0,len(Beam_ID)):

            sql = '''SELECT SectID FROM tblBeamSeg WHERE StdFlrID = %s AND ID = %s ''' %(self.floor, Beam_ID[i][0])
            cursor.execute(sql)
            B_SectID = cursor.fetchall() #[(int,),...(int,),]

            Section_Index = All_Section_List_ID.index(B_SectID[0][0])
            Beam_Section.append( All_Section_List[Section_Index] )


        return Beam_Section

    #JtID转换坐标 可设置得到YJK原始坐标or相对坐标
    def Trans_JtID_2_Coordinate(self,JtID_list, get_relative_coor = 1):

        JtC_list = []

        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()
        try:
            if len(JtID_list[0]) == 1 :
                for i in range(0,len(JtID_list)) :
                    sql = '''SELECT X FROM tblJoint WHERE ID = %s ''' %(JtID_list[i][0])
                    cursor.execute(sql)
                    X = round(cursor.fetchall()[0][0] ,2 ) #int or float

                    sql = '''SELECT Y FROM tblJoint WHERE ID = %s ''' %(JtID_list[i][0])
                    cursor.execute(sql)
                    Y = round(cursor.fetchall()[0][0] ,2 ) #int or float

                    if get_relative_coor :
                        JtC_list.append( Tools.Add_List( [X,Y], Tools.Mult_List(self.CAD_Base_Coor,-1) ) )
                    else :
                        JtC_list.append([X,Y])


            elif len(JtID_list[0]) == 2 :

                    for i in range(0,len(JtID_list)) :
                        sql = '''SELECT X FROM tblJoint WHERE ID = %s ''' %(JtID_list[i][0])
                        cursor.execute(sql)
                        X1 = round( cursor.fetchall()[0][0] ,2 )#int or float

                        sql = '''SELECT Y FROM tblJoint WHERE ID = %s ''' %(JtID_list[i][0])
                        cursor.execute(sql)
                        Y1 = round( cursor.fetchall()[0][0] ,2 )#int or float

                        sql = '''SELECT X FROM tblJoint WHERE ID = %s ''' %(JtID_list[i][1])
                        cursor.execute(sql)
                        X2 = round( cursor.fetchall()[0][0] ,2 )#int or float

                        sql = '''SELECT Y FROM tblJoint WHERE ID = %s ''' %(JtID_list[i][1])
                        cursor.execute(sql)
                        Y2 = round( cursor.fetchall()[0][0] ,2 )#int or float

                        if get_relative_coor :
                            JtC_list.append([
                                            Tools.Add_List( [X1,Y1], Tools.Mult_List(self.CAD_Base_Coor,-1) ) ,
                                            Tools.Add_List( [X2,Y2], Tools.Mult_List(self.CAD_Base_Coor,-1) )
                                            ])
                        else :
                            JtC_list.append( [ [X1,Y1], [X2,Y2] ] )

            else :
                print('???????????你喂给我的是啥玩意啊，本函数不认识')
        except :
            return '???????????你喂给我的是啥玩意啊，你跟我俩闹呢'

        return JtC_list   #[(x,y),...(x,y),] or [((x1,y1),(x2,y2)),...((x1,y1),(x2,y2)),]

    def Get_All_Colum(self):
        conn = sqlite3.connect(self.fileDir)
        cursor = conn.cursor()
        all_colum = []
        C_JID = self.Get_Colum_Jt_list()
        C_Coor = self.Trans_JtID_2_Coordinate(C_JID)
        C_Sect = []
        C_Rota = []

        All_Section_List = self.Trans_Section_Info()[0]
        All_Section_List_ID = [i.ID for i in All_Section_List]

        for each in C_JID :
            sql = '''SELECT SectID FROM tblColSeg WHERE JtID = %s ''' %(each[0])
            cursor.execute(sql)
            SectID = cursor.fetchall()[0][0]

            sql = '''SELECT Rotation FROM tblColSeg WHERE JtID = %s ''' %(each[0])
            cursor.execute(sql)
            Rotation = float(cursor.fetchall()[0][0])

            Section_Index = All_Section_List_ID.index(SectID)
            C_Sect.append( All_Section_List[Section_Index] )
            C_Rota.append(Rotation)

        for i in range(0,len(C_JID)):
            tem_colum = YJKColum()
            tem_colum.JtID = C_JID[i][0]
            #print(C_Coor[i])
            tem_colum.CenterCoordinate = [C_Coor[i][0], C_Coor[i][1], 0]
            tem_colum.Section = C_Sect[i]
            tem_colum.Rotation = (C_Rota[i]/180)*math.pi
            tem_colum.Get_Corner_Tagging_Coordinate()
            all_colum.append(tem_colum)


        return all_colum

    def Get_All_Beam(self):

        Beam_Line = self.Get_Beam_Grid_list()
        Beam_Joint = self.Get_Beam_Jt_list()
        Beam_Coordinate = self.Trans_JtID_2_Coordinate(Beam_Joint)
        Beam_Connection = self.Get_Beam_Connection_list()
        Beam_Section = self.Get_Beam_Section_list()
        all_beam = []

        for i in range(0,len(Beam_Line)):
            tem_beam = YJKBeam()
            tem_beam.Grid = [Beam_Line[i][0]]
            tem_beam.JtID = [Beam_Joint[i][0],Beam_Joint[i][-1]]
            tem_beam.Coordinate = [[ i for i in Beam_Coordinate[i] ]]
            tem_beam.Connection = [Beam_Connection[i]]
            tem_beam.Section = Beam_Section[i]
            #print(tem_beam.Coordinate)
            tem_beam.getBeamProperty()

            #print(tem_beam.Section)
            all_beam.append(tem_beam)

        return all_beam

        #分开主次梁

    # 通过关键点 合并beam  并区分出较高一级与较低一级的梁
    def Merge_By_KeyPoint(self,keyJt,Beam,Beam_Rank):

        Beam_Main = []
        Beam_Overhanging = []
        Beam_Sec = Beam   #逐步挑选出更main的梁
        Beam_need_grow = []

        #--------------------------------------------------------------------------------------
        #第一次遍历输入的keyJt
        for i in range(0,len(Beam_Sec)):
            if Beam_Sec[i].JtID[0] in keyJt and Beam_Sec[i].JtID[-1] in keyJt:
                Beam_Sec[i].Rank = Beam_Rank
                Beam_Main.append(Beam_Sec[i])
                Beam_Sec[i] = None
            elif Beam_Sec[i].JtID[0] in keyJt and Beam_Sec[i].JtID[-1] not in keyJt:
                Beam_need_grow.append(Beam_Sec[i])
                Beam_Sec[i] = None
            elif Beam_Sec[i].JtID[0]  not in keyJt and Beam_Sec[i].JtID[-1] in keyJt:
                Beam_Sec[i].reverseBeam()
                Beam_need_grow.append(Beam_Sec[i])
                Beam_Sec[i] = None
        while None in Beam_Sec:
            Beam_Sec.remove(None)


        # 合并可以合并的悬挑梁
        B_identJt = [i.JtID[-1] for i in Beam_need_grow]
        for i in range(0,len(Beam_need_grow)):
            Index = Tools.Get_Duplicate_ValueIndex( B_identJt, B_identJt[i] )
            if len(Index) > 1:
                for ii in Index:
                    if Beam_need_grow[i].mergeBeam(Beam_need_grow[ii]) == 'success':
                        Beam_Main.append(Beam_need_grow[i])
                        Beam_need_grow[i].Rank = Beam_Rank
                        Beam_need_grow[i]=None
                        Beam_need_grow[ii]=None
                        B_identJt[i]=None
                        B_identJt[ii]=None
                        break
        while None in B_identJt:
            Beam_need_grow.remove(None)
            B_identJt.remove(None)

        #----------------------------------------------------------------------------------
        #处理完所有在keyJt节点上的梁之后开始向前延申  直到没有新的Beam_Sec加进来

        while 1 :
            B_identJt = [i.JtID[-1] for i in Beam_need_grow]
            for i in range(0,len(Beam_Sec)):
                if Beam_Sec[i].JtID[0] in B_identJt:
                    Index = Tools.Get_Duplicate_ValueIndex( B_identJt, Beam_Sec[i].JtID[0] )
                    for ii in Index:
                        if Beam_need_grow[ii].mergeBeam(Beam_Sec[i]) == 'success':
                            Beam_Sec[i] = None
                            break
                elif Beam_Sec[i].JtID[-1] in B_identJt:
                    Index = Tools.Get_Duplicate_ValueIndex( B_identJt, Beam_Sec[i].JtID[-1] )
                    for ii in Index:
                        if Beam_need_grow[ii].mergeBeam(Beam_Sec[i]) == 'success':
                            Beam_Sec[i] = None
                            break
            #while 1 终止条件
            if None not in Beam_Sec :
                break

            while None in Beam_Sec:
                Beam_Sec.remove(None)
            # 合并可以合并的悬挑梁
            B_identJt = [i.JtID[-1] for i in Beam_need_grow]
            for i in range(0,len(Beam_need_grow)):
                Index = Tools.Get_Duplicate_ValueIndex( B_identJt, B_identJt[i] )
                if len(Index) > 1:
                    for ii in Index:
                        if Beam_need_grow[i].mergeBeam(Beam_need_grow[ii]) == 'success':
                            Beam_Main.append(Beam_need_grow[i])
                            Beam_need_grow[i].Rank = Beam_Rank
                            Beam_need_grow[i]=None
                            Beam_need_grow[ii]=None
                            B_identJt[i]=None
                            B_identJt[ii]=None
                            break
            while None in B_identJt:
                Beam_need_grow.remove(None)
                B_identJt.remove(None)

            #print(len(Beam_Sec),'Beam_Sec')
            #print(len(Beam_need_grow),'Beam_need_grow')
            #print(len(Beam_Main),'Beam_Main')
            #print('-------------------------')

        #----------------------------------------------------------------------------------
        #打断搭在主梁上的悬挑梁 与柱连接部分编入主梁  其余编入次梁
        #若 need_grow_Beam 终点搭在其他主梁上   则将 need_grow_Beam 也编入主梁
        #Beam_Main 不断更新直到数量不再增加
        while 1 :
            Beam_Main_num = len(Beam_Main)

            Beam_need_grow_Mid_Jt = []
            Beam_Main_Mid_Jt_Nonestedlist = []   #Beam_Main_Mid_Jt 无嵌套

            #获取主梁中间节点集合（去重）
            for i in range(0,len(Beam_Main)):
                Mid_jt = [j for j in Beam_Main[i].JtID]
                del Mid_jt[0]
                del Mid_jt[-1]
                for each in Mid_jt:
                    if each not in Beam_Main_Mid_Jt_Nonestedlist:
                        Beam_Main_Mid_Jt_Nonestedlist.append(each)

            #获取悬挑梁除起点外的节点集合： [ ... [第i根悬挑梁上所有除起点外的节点] ...]
            for i in range(0,len(Beam_need_grow)):
                Mid_jt = [j for j in Beam_need_grow[i].JtID]
                del Mid_jt[0]
                #del Mid_jt[-1]
                Beam_need_grow_Mid_Jt.append(Mid_jt)
                #print(Mid_jt)

            #获取搭在主梁上的悬挑梁的index  以及与主梁重合的 节点 ： [ ... [悬挑梁的index，[所有重合节点节点号]] ...]
            Index = []
            for i in range(0,len(Beam_need_grow_Mid_Jt)) :
                tem_coincidentJt = []
                for ii in range(0,len(Beam_need_grow_Mid_Jt[i])) :
                    if Beam_need_grow_Mid_Jt[i][ii] in Beam_Main_Mid_Jt_Nonestedlist:
                        tem_coincidentJt.append(Beam_need_grow_Mid_Jt[i][ii])
                if len(tem_coincidentJt) > 0:
                    tem_coincidentJt.reverse()
                    Index.append([i,tem_coincidentJt])
            #print(Index)

            #从悬挑端出发依次断开悬挑梁  与柱连接部分编入主梁  其余编入次梁
            #若 need_grow_Beam 终点搭在其他主梁上   则将 need_grow_Beam 也编入主梁
            for i in range(0,len(Index)) :
                for ii in range(0,len(Index[i][-1])) :
                    breakJt = Index[i][-1][ii]
                    print(Index[i])
                    dividedBeam = Beam_need_grow[Index[i][0]].breakBeam(breakJt)
                    Beam_need_grow[Index[i][0]] = dividedBeam[0]
                    dividedBeam[0].Rank = Beam_Rank
                    Beam_Main.append( dividedBeam[0] )
                    if dividedBeam[-1] != None:
                        Beam_Sec.append( dividedBeam[-1] )
                Beam_need_grow[Index[i][0]] = None

            while None in Beam_need_grow:
                Beam_need_grow.remove(None)

            if len(Beam_Main) == Beam_Main_num :
                break
        #----------------------------------------------------------------------------------

        #若Beam_need_grow中的梁终点未搭在其他任何主梁上且起点为刚接 则为真-悬挑梁
        #若Beam_need_grow中的梁终点未搭在其他任何主梁上且起点为铰接 则编入次梁
        for i in range(0, len(Beam_need_grow) ):
            if Beam_need_grow[i].Connection[0][0] == 1 :
                Beam_Sec.append( Beam_need_grow[i] )
                Beam_need_grow[i] = None
            else :
                Beam_need_grow[i].Rank = Beam_Rank
                Beam_need_grow[i].Overhanging = 1
        while None in Beam_need_grow:
            Beam_need_grow.remove(None)

        Beam_Main.extend(Beam_need_grow)

        return {'higher_class_beam': Beam_Main , 'lower_class_beam': Beam_Sec }

    # 对所有梁进行 合并&分级 操作
    def Divide_Beam_Class(self):
        all_beam = self.Get_All_Beam()
        Divide_Beam = []
        keyJt = [ i[0] for i in self.Get_Colum_Jt_list() ]

        # 首次筛选  得到主梁以及其他
        tem_beam_list = self.Merge_By_KeyPoint(keyJt,all_beam,0)
        higher_class_beam = tem_beam_list['higher_class_beam']
        lower_class_beam = tem_beam_list['lower_class_beam']
        Divide_Beam.extend(higher_class_beam)

        # 循环筛选  直到lower_class_beam中元素不再减少 或 为空集
        beamclass = 0
        while 1 :
            lower_class_beam_num = len(lower_class_beam)
            #获取higher_class_beam主梁中间节点集合（去重）
            #keyJt = []
            for i in range(0,len(higher_class_beam)):
                higher_class_beam_jt = [j for j in higher_class_beam[i].JtID]
                for each in higher_class_beam_jt:
                    if each not in keyJt:
                        keyJt.append(each)

            beamclass = beamclass + 1
            tem_beam_list = self.Merge_By_KeyPoint(keyJt,lower_class_beam,beamclass)
            higher_class_beam = tem_beam_list['higher_class_beam']
            lower_class_beam = tem_beam_list['lower_class_beam']
            Divide_Beam.extend(higher_class_beam)
            #print(len(lower_class_beam))
            if len(lower_class_beam) == lower_class_beam_num or len(lower_class_beam) == 0:
                for i in range(0,len(lower_class_beam)):
                    lower_class_beam[i].Rank = beamclass + 1
                    Divide_Beam.append(lower_class_beam[i])
                break

        return Divide_Beam
















#
