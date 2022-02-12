import pyautocad
import ReadYJK
import Tools


pyacad = pyautocad.Autocad(create_if_not_exists=True)

#刚接符号
def Rigid_Symbol(p1,p2): #p1起点 p2终点

    dist_p1p2 = Tools.Get_Points_Dist(p2,p1)
    vector_p1p2 = Tools.Add_List( p2, Tools.Mult_List(p1,-1) )
    p2 =  Tools.Add_List( Tools.Mult_List(vector_p1p2,375/dist_p1p2) , p1)

    pnts = [pyautocad.APoint(p1),pyautocad.APoint(p2)]
    pnts = [i for j in pnts for i in j]
    pnts = pyautocad.aDouble(pnts)
    Symbol = pyacad.model.AddPolyLine(pnts)

    # 绘制刚接符号
    segmentIndex = 0  # 要修改第X段的线宽
    startWidth = 375  # 起点线宽
    endWidth = 0      # 终点线宽
    Symbol.SetWidth(segmentIndex, startWidth, endWidth)

    # 符号颜色
    Symbol.Color = 0

#画单根钢梁  #输入参数为ReadYJK.YJKBeam类
def Draw_Steel_Beam(YJKBeam , All_YJKColum):
    YJKBeam_Start_JtID = YJKBeam.JtID[0]
    YJKBeam_End_JtID = YJKBeam.JtID[-1]

    B_vector = YJKBeam.Vector
    B_vector.append(0)

    B_start = [ YJKBeam.Coordinate[0][0][0], YJKBeam.Coordinate[0][0][1], 0]
    B_end   = [ YJKBeam.Coordinate[-1][-1][0], YJKBeam.Coordinate[-1][-1][1], 0]
    Beam_mid_point = Tools.Get_Mid_Point(B_start,B_end)

    dist_from_colum = 200
    dist_from_otherbeam = 150

    if YJKBeam.Rank == 0 :
        if YJKBeam.Overhanging == 0 :
            All_YJKColum_JtID = [ i.JtID for i in All_YJKColum ]
            Index = Tools.Get_Duplicate_ValueIndex(All_YJKColum_JtID,YJKBeam_Start_JtID)
            YJKColum_Start = All_YJKColum[Index[0]]

            C_1_cp1 = YJKColum_Start.CornerCoordinate[0]
            C_1_cp2 = YJKColum_Start.CornerCoordinate[1]
            C_1_cp3 = YJKColum_Start.CornerCoordinate[2]
            C_1_cp4 = YJKColum_Start.CornerCoordinate[3]

            C_1_p12 = Tools.Get_Mid_Point(C_1_cp1,C_1_cp2)
            C_1_p23 = Tools.Get_Mid_Point(C_1_cp2,C_1_cp3)
            C_1_p34 = Tools.Get_Mid_Point(C_1_cp3,C_1_cp4)
            C_1_p41 = Tools.Get_Mid_Point(C_1_cp4,C_1_cp1)
            C_1_center = [ C_1_p12, C_1_p23, C_1_p34, C_1_p41 ]

            Arc_point = C_1_p12
            Min_distance = Tools.Get_Points_Dist(Beam_mid_point,Arc_point)
            for i in C_1_center :
                if Tools.Get_Points_Dist(Beam_mid_point,i) < Min_distance :
                    Min_distance = Tools.Get_Points_Dist(Beam_mid_point,i)
                    Arc_point = i

            New_B_start = Tools.Add_List( B_start, Tools.Mult_List(B_vector, (Tools.Get_Points_Dist(B_start,Arc_point) + dist_from_colum)) )


            Index = Tools.Get_Duplicate_ValueIndex(All_YJKColum_JtID,YJKBeam_End_JtID)
            if len(Index) != 0 :
                YJKColum_End = All_YJKColum[Index[0]]
                C_1_cp1 = YJKColum_End.CornerCoordinate[0]
                C_1_cp2 = YJKColum_End.CornerCoordinate[1]
                C_1_cp3 = YJKColum_End.CornerCoordinate[2]
                C_1_cp4 = YJKColum_End.CornerCoordinate[3]

                C_1_p12 = Tools.Get_Mid_Point(C_1_cp1,C_1_cp2)
                C_1_p23 = Tools.Get_Mid_Point(C_1_cp2,C_1_cp3)
                C_1_p34 = Tools.Get_Mid_Point(C_1_cp3,C_1_cp4)
                C_1_p41 = Tools.Get_Mid_Point(C_1_cp4,C_1_cp1)
                C_1_center = [ C_1_p12, C_1_p23, C_1_p34, C_1_p41 ]

                Arc_point = C_1_p12
                Min_distance = Tools.Get_Points_Dist(Beam_mid_point,Arc_point)
                for i in C_1_center :
                    if Tools.Get_Points_Dist(Beam_mid_point,i) < Min_distance :
                        Min_distance = Tools.Get_Points_Dist(Beam_mid_point,i)
                        Arc_point = i
                New_B_end = Tools.Add_List( B_end, Tools.Mult_List(B_vector, -1*(Tools.Get_Points_Dist(B_end,Arc_point) + dist_from_colum)) )

            else:
                New_B_end = Tools.Add_List( B_end, Tools.Mult_List(B_vector, -1*dist_from_otherbeam))

            beam_line_list = []
            beam_line_list.append(New_B_start)
            beam_line_list.append(New_B_end)

        elif YJKBeam.Overhanging == 1:
            All_YJKColum_JtID = [ i.JtID for i in All_YJKColum ]
            YJKBeam_Start_JtID = YJKBeam.JtID[0]
            Index = Tools.Get_Duplicate_ValueIndex(All_YJKColum_JtID,YJKBeam_Start_JtID)
            YJKColum_Start = All_YJKColum[Index[0]]
            #YJKColum_Start_CornerCoordinate = YJKColum_Start.CornerCoordinate
            C_1_cp1 = YJKColum_Start.CornerCoordinate[0]
            C_1_cp2 = YJKColum_Start.CornerCoordinate[1]
            C_1_cp3 = YJKColum_Start.CornerCoordinate[2]
            C_1_cp4 = YJKColum_Start.CornerCoordinate[3]

            #print( YJKBeam.Vector,'YJKBeam.Vector' )
            B_vector = YJKBeam.Vector
            B_vector.append(0)
            #print( YJKBeam.Vector )
            B_start =[ YJKBeam.Coordinate[0][0][0], YJKBeam.Coordinate[0][0][1], 0]
            B_end = [ YJKBeam.Coordinate[-1][-1][0], YJKBeam.Coordinate[-1][-1][1], 0]
            Beam_mid_point = Tools.Get_Mid_Point(B_start,B_end)

            C_1_p12 = Tools.Get_Mid_Point(C_1_cp1,C_1_cp2)
            C_1_p23 = Tools.Get_Mid_Point(C_1_cp2,C_1_cp3)
            C_1_p34 = Tools.Get_Mid_Point(C_1_cp3,C_1_cp4)
            C_1_p41 = Tools.Get_Mid_Point(C_1_cp4,C_1_cp1)
            C_1_center = [ C_1_p12, C_1_p23, C_1_p34, C_1_p41 ]

            Arc_point = C_1_p12
            Min_distance = Tools.Get_Points_Dist(Beam_mid_point,Arc_point)
            for i in C_1_center :
                if Tools.Get_Points_Dist(Beam_mid_point,i) < Min_distance :
                    Min_distance = Tools.Get_Points_Dist(Beam_mid_point,i)
                    Arc_point = i
            #print( Tools.Get_Points_Dist(B_start,Arc_point) + 350.0)
            New_B_start = Tools.Add_List( B_start, Tools.Mult_List(B_vector, (Tools.Get_Points_Dist(B_start,Arc_point) + dist_from_colum)) )
            beam_line_list = []
            beam_line_list.append(New_B_start)
            beam_line_list.append(B_end)
    else :
        beam_line_list = []
        if YJKBeam.Overhanging == 0 :
            New_B_start = Tools.Add_List( B_start, Tools.Mult_List(B_vector, dist_from_otherbeam))
            New_B_end = Tools.Add_List( B_end, Tools.Mult_List(B_vector, -1*dist_from_otherbeam))

            beam_line_list.append(New_B_start)
            beam_line_list.append(New_B_end)
        elif YJKBeam.Overhanging == 1 :
            New_B_start = Tools.Add_List( B_start, Tools.Mult_List(B_vector, dist_from_otherbeam))

            beam_line_list.append(New_B_start)
            beam_line_list.append(B_end)

    pnts = [pyautocad.APoint(i) for i in beam_line_list]
    pnts = [i for j in pnts for i in j]
    pnts = pyautocad.aDouble(pnts)
    CADBeam = pyacad.model.AddPolyLine(pnts)


    segmentIndex = 0
    startWidth = 150
    endWidth = 150
    #Beam.Linetype = 'BYLAYER'
    #print(YJKBeam.Rank,'B[i].Rank')
    #print(YJKBeam.Section,'B[i].Rank')
    if YJKBeam.Rank != 0 :
        CADBeam.Color = 3
        pass
    CADBeam.ConstantWidth = 120     # 线宽


    if YJKBeam.Connection[0][0] == 0 or YJKBeam.Connection[0][0] == 3:
        Rigid_Symbol(beam_line_list[0],beam_line_list[-1])
    if YJKBeam.Connection[-1][-1] == 0 or YJKBeam.Connection[-1][-1] == 3:
        Rigid_Symbol(beam_line_list[-1],beam_line_list[0])

#画单根钢柱  #输入参数为ReadYJK.YJKColum类
def Draw_Steel_Colum(YJKColum):
    if YJKColum.Section.Kind == 1 or YJKColum.Section.Kind == 7 :
        cp1 = YJKColum.CornerCoordinate[0]
        cp2 = YJKColum.CornerCoordinate[1]
        cp3 = YJKColum.CornerCoordinate[2]
        cp4 = YJKColum.CornerCoordinate[3]

        pnts = [pyautocad.APoint(cp1),pyautocad.APoint(cp2),pyautocad.APoint(cp3),pyautocad.APoint(cp4)]#,pyautocad.APoint(cp1),pyautocad.APoint(cp2)]
        pnts = [i for j in pnts for i in j]
        pnts = pyautocad.aDouble(pnts)
        Colum = pyacad.model.AddPolyLine(pnts)

        Colum.Closed = True
        Colum.Linetype = 'BYLAYER'
        #Colum.color = 'acByLayer'
        Colum.ConstantWidth = 60

    elif  YJKColum.Section.Kind == 2 or YJKColum.Section.Kind == 26 :

        cp1 = YJKColum.CornerCoordinate[0]
        cp2 = YJKColum.CornerCoordinate[1]

        cp3 = YJKColum.CornerCoordinate[2]
        cp4 = YJKColum.CornerCoordinate[3]
        cp14 = Tools.Get_Mid_Point(cp1,cp4)
        cp23 = Tools.Get_Mid_Point(cp2,cp3)

        pnts = [pyautocad.APoint(cp1),pyautocad.APoint(cp4),pyautocad.APoint(cp14),pyautocad.APoint(cp23),pyautocad.APoint(cp2),pyautocad.APoint(cp3)]#,pyautocad.APoint(cp1),pyautocad.APoint(cp2)]
        pnts = [i for j in pnts for i in j]
        pnts = pyautocad.aDouble(pnts)
        Colum = pyacad.model.AddPolyLine(pnts)

        #Colum.Closed = True
        Colum.Linetype = 'BYLAYER'
        #Colum.color = 'acByLayer'
        Colum.ConstantWidth = 60

    elif  YJKColum.Section.Kind == 8 or YJKColum.Section.Kind == 3 :

        cp1 = YJKColum.CornerCoordinate[0]
        cp2 = YJKColum.CornerCoordinate[1]

        cp3 = YJKColum.CornerCoordinate[2]
        cp4 = YJKColum.CornerCoordinate[3]
        cp14 = Tools.Get_Mid_Point(cp1,cp4)
        cp23 = Tools.Get_Mid_Point(cp2,cp3)

        pnts = [pyautocad.APoint(cp14),pyautocad.APoint(cp23),pyautocad.APoint(cp14),]#,pyautocad.APoint(cp1),pyautocad.APoint(cp2)]
        pnts = [i for j in pnts for i in j]
        pnts = pyautocad.aDouble(pnts)
        Colum = pyacad.model.AddPolyLine(pnts)
        Colum.SetBulge(0,1)
        Colum.SetBulge(1,1)

        #Colum.Closed = True
        Colum.Linetype = 'BYLAYER'
        #Colum.color = 'acByLayer'
        Colum.ConstantWidth = 60

#画全楼柱
def Draw_All_Colum(YJKData):

    layers_nums = pyacad.ActiveDocument.Layers.count
    layers_names = [pyacad.ActiveDocument.Layers.Item(i).Name for i in range(layers_nums)]

    try:
        index = layers_names.index('S-STEL-COLU')
        pyacad.ActiveDocument.ActiveLayer = pyacad.ActiveDocument.Layers.Item(index)
    except:
        LayerObj = pyacad.ActiveDocument.Layers.Add('S-STEL-COLU')
        pyacad.ActiveDocument.ActiveLayer = LayerObj
        LayerObj.color = 4


    C= YJKData.Get_All_Colum()

    for i in range(0,len(C)):
        Draw_Steel_Colum(C[i])

#画全楼梁
def Draw_All_Beam(YJKData):

    layers_nums = pyacad.ActiveDocument.Layers.count
    layers_names = [pyacad.ActiveDocument.Layers.Item(i).Name for i in range(layers_nums)]
    try:
        index = layers_names.index('S-STEL-BEAM')
        pyacad.ActiveDocument.ActiveLayer = pyacad.ActiveDocument.Layers.Item(index)
    except:
        LayerObj = pyacad.ActiveDocument.Layers.Add('S-STEL-BEAM')
        pyacad.ActiveDocument.ActiveLayer = LayerObj
        LayerObj.color = 4
        LayerObj.Linetype = 'BYLAYER'


    C= YJKData.Get_All_Colum()
    B= YJKData.Divide_Beam_Class()
    for each in B :
        #if each.Overhanging == 1:
            Draw_Steel_Beam(each,C)

#标注柱子截面
def Tagging_Colum(YJKData, Draw_Colum_Table = 1 ,taggingYJK_Define_Name = 0 , text_hight = 300 ):

    LayerObj = pyacad.ActiveDocument.Layers.Add('S-COLU-TEXT')
    pyacad.ActiveDocument.ActiveLayer = LayerObj
    LayerObj.color = 7

    try:
        pyacad.ActiveDocument.ActiveTextStyle = pyacad.ActiveDocument.TextStyles.Item("TSSD_Label")
    except:
        pyacad.ActiveDocument.TextStyles.Item("STANDARD").SetFont("等线 Light", False, False, 1, 0 or 0)
        pyacad.ActiveDocument.ActiveTextStyle = pyacad.ActiveDocument.TextStyles.Item("STANDARD")

    all_C_Sect = YJKData.Trans_Section_Info()[0]

    if Draw_Colum_Table :
        #将所有柱截面名称做成块 并生成柱表
        Steel_C_Sect_num = 0
        for i in range(0,len(all_C_Sect)):
            if all_C_Sect[i].Mat == 5 :
                Steel_C_Sect_num += 1

                if taggingYJK_Define_Name :
                    #截面编号名，需写入块的文字
                    name_textString = all_C_Sect[i].YJK_Define_Name
                else :
                    #截面编号名，需写入块的文字
                    name_textString = all_C_Sect[i].Self_Define_Name
                #块名，同截面编号名，因为块名不可有 * 这样的字符，所以一概将*替换为XX
                blockname = name_textString.replace('*','XX')

                #!!!废了老劲了  1.用Add创建新块并不会覆盖旧块  2.block本身可遍历，所以可用一个循环将块清空
                #块子空间的插入点
                insertPnt_In_Block = pyautocad.APoint(0, 0)
                blockObj = pyacad.ActiveDocument.Blocks.Add( insertPnt_In_Block, blockname )
                for each in blockObj:
                    each.delete()

                #将截面编号名写入块
                name_textObj = blockObj.AddText(name_textString, insertPnt_In_Block, text_hight)
                name_textObj.Alignment = 12

                #列出name_ 以及 ShapeName_ 形成柱表
                #截面编号名 的basepoint （GKZ1）
                name_BP = pyautocad.APoint(-50000, 10000-Steel_C_Sect_num*text_hight*1.8)
                #截面尺寸名 的basepoint（H500X200X15X20）
                ShapeName_BP = pyautocad.APoint(-50000+3000, 10000-Steel_C_Sect_num*text_hight*1.8)
                name_blockObj = pyacad.model.InsertBlock(name_BP, blockname, 1, 1, 1, 0 )
                ShapeName_textObj = pyacad.model.AddText(all_C_Sect[i].ShapeName , ShapeName_BP, text_hight)


    #标注柱子截面
    C = YJKData.Get_All_Colum()
    for i in range(0,len(C)):
        if taggingYJK_Define_Name :
            #截面编号名，需写入块的文字
            name_textString = C[i].Section.YJK_Define_Name
        else :
            #截面编号名，需写入块的文字
            name_textString = C[i].Section.Self_Define_Name

        Colum_Annotation_Line_P_list = [C[i].TaggingCoordinate]
        Colum_Annotation_Line_P_list.append( Tools.Add_List( Colum_Annotation_Line_P_list[0] , [text_hight*1.5,text_hight*2,0] ) )
        Colum_Annotation_Line_P_list.append( Tools.Add_List( Colum_Annotation_Line_P_list[1] , [text_hight*len(name_textString),0,0] ) )
    
        pnts = [pyautocad.APoint(i) for i in Colum_Annotation_Line_P_list]
        pnts = [i for j in pnts for i in j]
        pnts = pyautocad.aDouble(pnts)
        Colum_Annotation_Line = pyacad.model.AddPolyLine(pnts)

        blockname = name_textString.replace('*','XX')
        AP = Colum_Annotation_Line_P_list[1]
        insertPnt = pyautocad.APoint(AP[0], AP[1])
        RetVal = pyacad.model.InsertBlock(insertPnt, blockname, 1, 1, 1, 0 )

#标注梁截面
def Tagging_Beam(YJKData, Draw_Beam_Table = 1 ,taggingYJK_Define_Name = 0 , text_hight = 300 ):
    LayerObj = pyacad.ActiveDocument.Layers.Add('S-BEAM-TEXT')
    pyacad.ActiveDocument.ActiveLayer = LayerObj
    LayerObj.color = 7

    try:
        pyacad.ActiveDocument.ActiveTextStyle = pyacad.ActiveDocument.TextStyles.Item("TSSD_Label")
    except:
        pyacad.ActiveDocument.TextStyles.Item("STANDARD").SetFont("等线 Light", False, False, 1, 0 or 0)
        pyacad.ActiveDocument.ActiveTextStyle = pyacad.ActiveDocument.TextStyles.Item("STANDARD")

    all_B_Sect = YJKData.Trans_Section_Info()[1]

    if Draw_Beam_Table :
        #将所有梁截面名称做成块 并生成梁表
        Steel_B_Sect_num = 0
        for i in range(0,len(all_B_Sect)):
            if all_B_Sect[i].Mat == 5 :
                Steel_B_Sect_num += 1

                if taggingYJK_Define_Name :
                    #截面编号名，需写入块的文字
                    name_textString = all_B_Sect[i].YJK_Define_Name
                else :
                    #截面编号名，需写入块的文字
                    name_textString = all_B_Sect[i].Self_Define_Name
                #块名，同截面编号名，因为块名不可有 * 这样的字符，所以一概将*替换为XX
                blockname = name_textString.replace('*','XX')

                #!!!废了老劲了  1.用Add创建新块并不会覆盖旧块  2.block本身可遍历，所以可用一个循环将块清空
                #块子空间的插入点
                insertPnt_In_Block = pyautocad.APoint(0, 0)
                blockObj = pyacad.ActiveDocument.Blocks.Add( insertPnt_In_Block, blockname )
                for each in blockObj:
                    each.delete()

                #将截面编号名写入块
                name_textObj = blockObj.AddText(name_textString, insertPnt_In_Block, text_hight)
                name_textObj.Alignment = 13

                #列出name_ 以及 ShapeName_ 形成梁表
                #截面编号名 的basepoint （GKZ1）
                name_BP = pyautocad.APoint(-50000, 50000-Steel_B_Sect_num*text_hight*1.8)
                #截面尺寸名 的basepoint（H500X200X15X20）
                ShapeName_BP = pyautocad.APoint(-50000+3000, 50000-Steel_B_Sect_num*text_hight*1.8)
                name_blockObj = pyacad.model.InsertBlock(name_BP, blockname, 1, 1, 1, 0 )
                ShapeName_textObj = pyacad.model.AddText(all_B_Sect[i].ShapeName , ShapeName_BP, text_hight)

    #标注梁截面
    B = YJKData.Divide_Beam_Class()
    for i in range(0,len(B)):
        if taggingYJK_Define_Name :
            #截面编号名，需写入块的文字
            name_textString = B[i].Section.YJK_Define_Name
        else :
            #截面编号名，需写入块的文字
            name_textString = B[i].Section.Self_Define_Name

        blockname = name_textString.replace('*','XX')
        AP = B[i].TaggingCoordinate
        insertPnt = pyautocad.APoint(AP[0], AP[1])
        RetVal = pyacad.model.InsertBlock(insertPnt, blockname, 1, 1, 1, B[i].TaggingRotation )
        #pyacad.model.AddText( str(B[i].TaggingRotation) , insertPnt, text_hight)



def main():

    fileDir = r'J:\2020\北京副中心\地下模型（不含夹层及两侧下沉庭院）20210513\施工图\dtlmodel.ydb'
    #fileDir = r'J:\2020\东升科技园\YJKceshi\施工图\dtlmodel.ydb'
    #fileDir = r'C:\Users\2020055\Desktop\2022.2.11.ydb'

    YJKData = ReadYJK.YJKData(fileDir, floor = 9, Basefloor = 1)

    Draw_All_Colum( YJKData )
    Draw_All_Beam( YJKData )
    Tagging_Colum(YJKData, Draw_Colum_Table = 1, taggingYJK_Define_Name = 0 , text_hight = 300 )
    Tagging_Beam(YJKData, Draw_Beam_Table = 1, taggingYJK_Define_Name = 0 , text_hight = 300 )

if __name__ == '__main__':
    main()
    print(__name__)











#
