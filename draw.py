import ReadYJK
import YJK_cad
import Tools

fileDir = r'J:\2020\北京副中心\地下模型（不含夹层及两侧下沉庭院）20210513\施工图\dtlmodel.ydb'
#fileDir = r'J:\2020\东升科技园\YJKceshi\施工图\dtlmodel.ydb'
#fileDir = r'C:\Users\2020055\Desktop\2022.2.11.ydb'

#floor:自然层号
YJKData = ReadYJK.YJKData(fileDir, floor = 9, Basefloor = 1)

YJK_cad.Draw_All_Colum( YJKData )
#YJK_cad.Draw_All_Beam( YJKData )
YJK_cad.Tagging_Colum( YJKData, Draw_Colum_Table = 1, taggingYJK_Define_Name = 0 , text_hight = 375 )
YJK_cad.Tagging_Beam( YJKData, Draw_Beam_Table = 1, taggingYJK_Define_Name = 0 , text_hight = 300 )




'''
for i in range( 4 , 15 ) :

    YJKData = ReadYJK.YJKData(fileDir, floor = i, Basefloor = 1)
    YJKData.CAD_Base_Coor = Tools.Add_List(YJKData.CAD_Base_Coor,[0,-100000*(i-4),0])

    YJK_cad.Draw_All_Colum( YJKData )
    YJK_cad.Draw_All_Beam( YJKData )
    YJK_cad.Tagging_Colum( YJKData, Draw_Colum_Table = 1, taggingYJK_Define_Name = 0 , text_hight = 375 )
    YJK_cad.Tagging_Beam( YJKData, Draw_Beam_Table = 1, taggingYJK_Define_Name = 0 , text_hight = 300 )
'''
