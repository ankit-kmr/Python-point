import os,sys
import pandas as pd

def fn_CsvFilemaking (filenam):
    
    vr_csvR = pd.read_csv("C:\\Users\\ankit.kumar\\Desktop\\Input_outpu_CSV\\Input\\"+filenam, delimiter = ',' )

    clrclmn =["Quiz Name"]
    vr_csvR.sort_values("Email", inplace = True)
    vr_csvR[clrclmn] = vr_csvR[clrclmn].replace({' ':''}, regex=True)

    vr_csvR.columns =[column.replace(" ", "_") for column in vr_csvR.columns] 

    #print(vr_csvR)
    vrMailList = vr_csvR['Email']
    vrMailList = list(dict.fromkeys(vrMailList))

    print (vrMailList)
    for vrMailId in vrMailList :

        veremailID =[]
        vrFname =[]
        vrLstName =[]
        vrGrpname =[]
        vrPerc =[]
        vrstatus=[]
        vrScore1 =[]
        vrScore2 =[]
        vrScore3 =[]
        vrScore4 =[]
        vrScore5 =[]

        try:
            print('MaidID :: ' +vrMailId)
            dfmain = vr_csvR.loc[vr_csvR['Email'] == vrMailId]
            
            if (len (dfmain['Email']) == 5):
                print('===== 5 records found ======')  
                print (dfmain)
                print('hera A')
                veremailID = dfmain['Email'].tolist()
                print('hera B')
                Ls_mailid.append (veremailID[0])
                print('here c')
                vrFname = dfmain['First_Name'].tolist()
                print('here D')
                print(vrFname)
                Ls_fname.append (vrFname[0])
                #print(Ls_fname)
                vrLstName = dfmain['Last_Name'].tolist()
                Ls_lastname.append (vrLstName[0])
                vrGrpname = dfmain['Group_name'].tolist()
                ls_grpname.append (vrGrpname[0])
                print('here E')
                vrPerc = dfmain['Percentage'].tolist()
                ls_percentage.append (vrPerc[0])
                print('here F')
                vrstatus = dfmain['Status'].tolist()
                ls_status.append (vrstatus[0])

                
                dfChild1 = dfmain.loc[dfmain['Quiz_Name'] =="Kongu_ReasoningAndAnalytical_Sep_2020"]
                print('Child frame1')
                print(dfChild1)
                dfChild2 = dfmain.loc[dfmain['Quiz_Name'] =="Kongu_DigitalElectronicsNew_Sep_2020"]
                print('Child frame2')
                print(dfChild2)
                dfChild5 = dfmain.loc[dfmain['Quiz_Name'] =="Kongu_BasicElectronics_Sep_2020"]
                print('Child frame5')
                print(dfChild5)
                dfChild3 = dfmain.loc[dfmain['Quiz_Name'] =="Kongu_C&C++_Sep_2020"]
                print('Child frame3')
                print(dfChild3)
                dfChild4 = dfmain.loc[dfmain['Quiz_Name'] =="Kongu_VLSI_Sep_2020"]
                print('Child frame4')
                print(dfChild4)
                
                # dfChild1 = dfmain.query('Email =='+ vrMailId +' and Quiz_Name == "Kongu_Reasoning And Analytical_Sep_2020"',inplace = True)
                # print('Child frame1')
                # print(dfChild1)
                # dfChild2 = dfmain.query('Email =='+ vrMailId  +'and Quiz_Name == "Kongu_Basic Electronics_Sep_2020"',inplace = True)
                # print('Child frame2')
                # print(dfChild2)
                # dfChild5 = dfmain.query('Email =='+ vrMailId  +'and Quiz_Name == "Kongu_Digital Electronics New_Sep_2020"',inplace = True)
                # print('Child frame5')
                # print(dfChild5)
                # dfChild3 = dfmain.query('Email =='+ vrMailId  +'and Quiz_Name == "Kongu_C & C++_Sep_2020"',inplace = True)
                # print('Child frame3')
                # print(dfChild3)
                # dfChild4 = dfmain.query('Email =='+ vrMailId  +'and Quiz_Name == "Kongu_VLSI_Sep_2020"',inplace = True)
                # print('Child frame4')
                # print(dfChild4)

                # dfChild1 = dfmain.query[(dfmain['Email'] == vrMailId) & (dfmain['QuizName'] == 'Kongu_Reasoning And Analytical_Sep_2020') ]
                # print('Child frame1')
                # print(dfChild1)
                # dfChild2 = dfmain.loc[(dfmain['Email'] == vrMailId) & (dfmain['QuizName'] == 'Kongu_Basic Electronics_Sep_2020') ]
                # print('Child frame2')
                # print(dfChild2)
                # dfChild5 = dfmain.loc[(dfmain['Email'] == vrMailId) & (dfmain['QuizName'] == 'Kongu_Digital Electronics New_Sep_2020') ]
                # print('Child frame5')
                # print(dfChild5)
                # dfChild3 = dfmain.loc[(dfmain['Email'] == vrMailId) & (dfmain['QuizName'] == 'Kongu_C & C++_Sep_2020') ]
                # print('Child frame3')
                # print(dfChild3)
                # dfChild4 = dfmain.loc[(dfmain['Email'] == vrMailId) & (dfmain['QuizName'] == 'Kongu_VLSI_Sep_2020') ]
                # print('Child frame4')
                # print(dfChild4)

                print('here G')
                vrScore1 = dfChild1.Score.tolist()
                print(vrScore1)
                vrScore2 = dfChild2.Score.tolist()
                print('here H1')
                print(vrScore2)
                vrScore3 = dfChild3.Score.tolist()
                print('here H2')
                print(vrScore3)
                vrScore4 = dfChild4.Score.tolist()
                print('here H3')
                print(vrScore4)
                vrScore5 = dfChild5.Score.tolist()
                print('here H4')
                print(vrScore5)
               
                ls_score1.append ( vrScore1[0] )
                print('here I')
                print(ls_score1)
                ls_score2.append ( vrScore2[0] )
                print('here J')
                print(ls_score2)
                print(ls_score3)
                ls_score3.append ( vrScore3[0] )
                print('here k')
                print(ls_score3)
                ls_score4.append ( vrScore4[0] )
                print('here L')
                print(ls_score3)
                ls_score5.append ( vrScore5[0] )

                vrAvg = (vrScore1[0] +vrScore2[0] +vrScore3[0]+vrScore4[0]+vrScore5[0]) / 5
                print('here M')
                print(vrAvg)
                ls_avg.append(vrAvg)
                print(ls_avg)

        except Exception as e :
            print ("Exception >>>"+ str(e))

    # -------------------------- Changing to dataframe and making CSV ----------------------------------
    data_tuples = list(zip(Ls_mailid ,Ls_fname ,Ls_lastname ,ls_grpname ,ls_score1,ls_score2,ls_score3,ls_score4,ls_score5,ls_avg,ls_percentage,ls_status))
    print(data_tuples)
    df = pd.DataFrame(data_tuples, columns=header)
    print (df)
    df.to_csv(vr_Outfolder+'\marks_output.csv' ,index=False)
    
try :
    
    Ls_mailid = []
    Ls_fname = []
    Ls_lastname = [] 
    ls_grpname =[]
    ls_score1 =[]
    ls_score2 =[]
    ls_score3 =[]
    ls_score4 =[]
    ls_score5 =[]
    ls_avg =[]
    ls_percentage =[]
    ls_status =[]

    header=["Email" ,"First Name" ,"Last Name" ,"Group name" ,"Kongu_Reasoning And Analytical_Sep_2020" ,"Kongu_Basic Electronics_Sep_2020"  ,"Kongu_C & C++_Sep_2020" ,"Kongu_VLSI_Sep_2020" ,"Kongu_Digital Electronics New_Sep_2020" ,"AvgScore","Percentage" ,"Status" ]

    vr_Outfolder = "C:\\Users\\ankit.kumar\\Desktop\\Input_outpu_CSV\\Output"
    
    if os.path.exists (vr_Outfolder):
        print('************** Creating csv file **************')
        csvOpen = open(vr_Outfolder+'\marks_output.csv' ,'w+')
        csvOpen.close()

    # -------------------------------------------
    fn_CsvFilemaking ('marks_input.csv')
    # -------------------------------------------  

except Exception as e :
    print('FATAL >> '+ str(e))
    
        
        