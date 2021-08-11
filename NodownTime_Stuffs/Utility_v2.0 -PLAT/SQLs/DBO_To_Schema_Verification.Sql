SET NOCOUNT ON ;
GO
SET XACT_ABORT ON;
GO 

/*
AUTHOR : Ankit k
Description : Returns Schema mismatch result
*/


DROP TABLE IF EXISTS #TEMP_BadProc
CREATE TABLE #TEMP_BadProc( ProcName VARCHAR(200))

INSERT INTO #TEMP_BadProc
SELECT 'DisplayARecapinTxnDF_DF' UNION ALL
SELECT 'DisplayARecapinTxnDF_DF' UNION ALL
SELECT 'GenerateACHreturnfileSummary' UNION ALL
SELECT 'GenerateACHreturnfileSummary' UNION ALL
SELECT 'GenerateACHreturnfileSummary' UNION ALL
SELECT 'GenerateACHreturnfileSummary' UNION ALL
SELECT 'Generateachreturnfilesummaryfordate' UNION ALL
SELECT 'Generateachreturnfilesummaryfordate' UNION ALL
SELECT 'Generateachreturnfilesummaryfordate' UNION ALL
SELECT 'Generateachreturnfilesummaryfordate' UNION ALL
SELECT 'Generateachreturnfilesummaryfordate' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateDailyControlReportDataNonMatch' UNION ALL
SELECT 'GenerateOFACBlockedTransactionsReportData' UNION ALL
SELECT 'GenerateTransactionDetailReportData' UNION ALL
SELECT 'pr_UpdateUserOnRoleChanges' UNION ALL
SELECT 'pr_UpdateUserOnRoleChanges' UNION ALL
SELECT 'UDF_AccessibleAgents' UNION ALL
SELECT 'UDF_AccessibleProgramManagers' UNION ALL
SELECT 'UDF_AccessibleProgramManagers' UNION ALL
SELECT 'USP_GeneratePayoptDailyReportingFile_2' UNION ALL
SELECT 'USP_GetChargeOffDetails' UNION ALL
SELECT 'USP_GetMCCGroup' UNION ALL
SELECT 'USP_InventoryDispatchReceiptUpdate' UNION ALL
SELECT 'USP_SendAlert_CPS_APIs' UNION ALL
SELECT 'VW_Tcivrrequest' UNION ALL
SELECT 'TestAccounts_BC'  UNION ALL
SELECT 'SP_MDSCcardMatching' UNION ALL
SELECT 'AddNewTrancode'  UNION ALL
SELECT 'SP_MDSCcardMatching'  UNION ALL
SELECT 'sp_MerchantPLAccounts_sec_a_insupd'  UNION ALL
SELECT 'SP_PPARecapNewTranCode'  UNION ALL
SELECT 'USP_DoNonMonetaryLog'   

Drop Table IF Exists #MissingOne
Create Table #MissingOne 
(RowID INT Identity(1,1) ,
Type Char(5) ,
ObejctType VARCHAR(200),
ObjectName VARCHAR(200) )

Drop Table IF Exists #Tmp_ShemaMismatchData
Create Table #Tmp_ShemaMismatchData 
(RowID INT NULL  ,ObjectID INT NULL ,
ObjectName VARCHAR(200) ,
Schema_ID INT,
schema_name Char(20),
Type Char(5) ,
ErrorMsg Varchar(100)
)

Declare @P_SchemaID INT 
Declare @S_SchemaID INT 

SELECT @P_SchemaID = Schema_ID from sys.schemas Where Name ='DBO'
SELECT @S_SchemaID = Schema_ID from sys.schemas Where Name ='Schema_1'


DROP TABLE IF EXISTS #TempResult
  
--FIND MISSING SCHEMA OBJECTS
-------------------------------------------------------------------------------------------------------------------------
INSERT INTO #MissingOne (Type,ObejctType ,ObjectName)
SELECT SO.Type,SO.type_desc,SO.Name
FROM Sys.objects SO  WITH(NOLOCK)   JOIN  Sys.schemas SS WITH(NOLOCK) ON SO.schema_id =SS.schema_id
  WHERE SS.Name IN ('dbo' ) AND SO.type IN('FN',
'P',
'TF',
'IF',
'V'  )  
AND SO.Name NOT LIKE 'GENERATE%' AND SO.Name NOT LIKE 'SYNC_%' AND SO.Name NOT LIKE 'syncobj_%' AND SO.Name NOT LIKE 'Temp%'
AND SO.Name NOT IN (SELECT * FROM #TEMP_BadProc)

EXCEPT

SELECT  SO.Type,SO.type_desc,SO.Name 
FROM Sys.objects SO  WITH(NOLOCK)   JOIN  Sys.schemas SS WITH(NOLOCK) ON SO.schema_id =SS.schema_id
  WHERE SS.Name IN ('Schema_1' ) AND SO.type IN('FN',
'P',
'TF',
'IF',
'V'  )  
AND SO.Name NOT LIKE 'GENERATE%' AND SO.Name NOT LIKE 'SYNC_%' AND SO.Name NOT LIKE 'syncobj_%' AND SO.Name NOT LIKE 'Temp%'
AND SO.Name NOT IN (SELECT * FROM #TEMP_BadProc)
--------------------------------------------------------------------------------------------------------------------------------------------
INSERT INTO #Tmp_ShemaMismatchData (RowID    ,ObjectName  ,Schema_ID ,schema_name ,Type  ,ErrorMsg )
Select ROW_NUMBER() OVER (PARTITION BY Type ORDER BY ObjectName) ,Ltrim(Rtrim(ObjectName)) , @P_SchemaID ,'DBO' ,Type ,'Missing in Schema_1' from #MissingOne

UPDATE T SET T.ObjectID = SO.Object_ID FROM #Tmp_ShemaMismatchData T JOIN Sys.objects SO WITH(NOLOCK)
ON T.ObjectName = LTRIM(RTRIM(So.name)) AND SO.schema_id =@P_SchemaID

-- SELECT * FROM #Tmp_ShemaMismatchData

;With  CTE_SchemaMismatchData
As
(
SELECT  S1.Object_ID,S1.Name ,S1.Schema_ID ,S1.Type   FROM Sys.objects S1 
JOIN Sys.objects S2 ON Ltrim(Rtrim(S1.Name)) = Ltrim(Rtrim(S2.Name )) AND S1.Schema_id =@P_SchemaID AND S2.Schema_id =@S_SchemaID
AND S1.modify_date  > S2.modify_date  AND S1.type IN('FN',
'P',
'TF',
'IF',
'V'  )  
AND  S1.Name NOT LIKE 'GENERATE%' AND S1.Name NOT LIKE 'SYNC_%' AND S1.Name NOT LIKE 'syncobj_%' AND S1.Name NOT LIKE 'Temp%'
)

INSERT INTO #Tmp_ShemaMismatchData (RowID    ,ObjectID,ObjectName  ,Schema_ID ,schema_name ,Type  ,ErrorMsg  )
SELECT ROW_NUMBER() OVER (PARTITION BY CT.Type ORDER BY CT.Name) ,CT.Object_ID,CT.Name,CT.Schema_ID ,S.Name ,CT.Type ,'Schema_1 Not Updated' 
FROM CTE_SchemaMismatchData CT JOIN Sys.Schemas S With(Nolock) ON CT.Schema_ID = S.Schema_ID

SELECT  Count(1) FROM #Tmp_ShemaMismatchData  
-- 
--  SELECT * FROM #Tmp_ShemaMismatchData 

--SELECT  T.RowID	,T.ObjectID	,T.ObjectName	,T.Type,T.ErrorMsg, Cast (SPP.modify_date As DATE) as 'DBO_Mdate',Cast(SP.modify_date As DATE)  'Schema1_MDate' ,DateDiff(Day ,SP.modify_date ,SPP.modify_date) 'Days_Diff'
--iNTO #TempResult FROM #Tmp_ShemaMismatchData T JOIN SYS.procedures SP ON T.ObjectID = SP.Object_ID And Sp.Schema_id =@S_SchemaID
----And T.ObjectName NOT LIKE 'P_%'
--LEFT JOIN SYS.procedures SPP ON T.ObjectName =SPP.Name And SPP.Schema_iD  =@P_SchemaID
--ORDER By T.Type


--Select * from sys.procedures where name in (
--Select ObjectName From #TempResult )


SELECT  T.RowID	,T.ObjectID	,T.ObjectName	,T.Type,T.ErrorMsg, SP.modify_date as 'DBO_Mdate',SPP.modify_date  'Schema1_MDate' ,DateDiff(Day ,SPP.modify_date ,SP.modify_date) 'Days_Diff'
iNTO #TempResult FROM #Tmp_ShemaMismatchData T JOIN SYS.procedures SP ON T.ObjectName = SP.Name  AND SP.Schema_iD  =@P_SchemaID
LEFT JOIN SYS.procedures SPP ON T.ObjectName =SPP.Name  AND SPP.Schema_id =@S_SchemaID   
ORDER By T.Type


SELECT * FROM #TempResult WHERE type <>'V'
--and cast(DBO_Mdate   as Date )='2020-09-21' And cast(Schema1_Mdate   as Date )='2020-09-21'
and days_diff > 0

