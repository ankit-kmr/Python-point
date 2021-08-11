SET NOCOUNT ON ;
GO
SET XACT_ABORT ON;
GO 

/*
AUTHOR : Ankit k
Description : Returns Schema mismatch result

--------------------------------------
EXEC USP_PDF_GetProcToImport 20
--------------------------------------

RUN ON ALL DB Need to import Schema

*/

CREATE OR ALTER PROCEDURE [DBO].USP_PDF_GetProcToImport 
@ImprtDuration VARCHAR(20) = -1

As
BEGIN

DECLARE @vrFromDate DATETIME =NULL

IF @ImprtDuration IS NOT NULL AND @ImprtDuration != -1
BEGIN
SET @vrFromDate =  DATEADD(DAY,-1*@ImprtDuration,GETDATE() )
END

PRINT @vrFromDate


IF (  OBJECT_ID(N'TempImportData') >0)    
BEGIN  
	DROP TABLE TempImportData    
END 
CREATE TABLE TempImportData (
RowID INT IDENTITY(1,1)   ,
ObjectID INT NULL ,
ObjectName VARCHAR(200) ,
Type Char(5)  ,
Processed INT  Default 0 ,
Status CHAR(5) Default 'New' ,
ErrorMsg NVARCHAR(MAX) NULL 
)

Drop Table IF Exists #MissingOne
Create Table #MissingOne 
(RowID INT Identity(1,1) ,
Type Char(5) ,
ObejctType VARCHAR(200),
ObjectName VARCHAR(200) )

Drop Table IF Exists #Tmp_ShemaMismatchData
Create Table #Tmp_ShemaMismatchData 
(RowID INT NULL  ,
ObjectID INT NULL ,
ObjectName VARCHAR(200) ,
Schema_ID INT,
Type Char(5) ,
)

Declare @P_SchemaID INT 
Declare @S_SchemaID INT 

SELECT @P_SchemaID = Schema_ID from sys.schemas Where Name ='DBO'
SELECT @S_SchemaID = Schema_ID from sys.schemas Where Name ='Schema_1'


IF @vrFromDate IS NULL AND  @ImprtDuration = -1
BEGIN
	Print '____Fetching for All____'
		;With  CTE_SchemaMismatchData
		As
		(
		SELECT  S1.Object_ID,S1.Name ,S1.Schema_ID ,S1.Type  FROM Sys.objects S1 
		WHERE S1.Schema_id =@P_SchemaID AND S1.type IN('FN',
		'P',
		'TF',
		'IF',
		'V'  )  
		AND S1.Name NOT LIKE 'SYNC_%' AND S1.Name NOT LIKE 'syncobj_%' AND S1.Name NOT LIKE 'Temp%'
		and S1.is_ms_shipped=0
		)

	INSERT INTO #Tmp_ShemaMismatchData (RowID    ,ObjectID,ObjectName  ,Schema_ID  ,Type  )
	SELECT ROW_NUMBER() OVER(ORDER BY object_id) ,Object_ID,Name,Schema_ID  ,Type 
	FROM CTE_SchemaMismatchData  --JOIN Sys.Schemas S With(Nolock) ON CT.Schema_ID = S.Schema_ID

END
ELSE
BEGIN
Print '_____Fetching for specific date_____'


	INSERT INTO #Tmp_ShemaMismatchData (RowID    ,ObjectID,ObjectName  ,Schema_ID  ,Type  )
	SELECT ROW_NUMBER() OVER(ORDER BY object_id),object_id,name,schema_id ,TYPE FROM   sys.objects WHERE  TYPE IN ( 'P',  'V', 'TF',
	'IF', 'FN' ) and is_ms_shipped=0 and schema_id=@P_SchemaID AND
	(create_date  > @vrFromDate OR modify_date  > @vrFromDate )
	AND Name NOT LIKE 'SYNC_%' AND Name NOT LIKE 'syncobj_%' AND Name NOT LIKE 'Temp%'

END

INSERT INTO TempImportData (ObjectID ,ObjectName ,Type)
SELECT DISTINCT ObjectID ,ObjectName,Type  FROM #Tmp_ShemaMismatchData  
--WHERE ObjectName like '%SP_SelectMCC%'

END
GO



/*


SELECT * from TempImportData WHERE Processed = 2 ORDER BY TYPE

SELECT TOP 20 RowID ,ObjectID ,ObjectName,Type FROM TempImportData With(NOLOCK) WHERE Processed = 0 ORDER BY TYPE



*/

