
/*

Author: Ankit k

EXEC USP_PDF_DBOToSchemaImport 
@vPrint = 1,
@IsdropON = 1 ,
@VrObjectType = 'FN',
@VrObjectID =185949376  ,
@VrObjectName= 'FCT_GetBillingPeriod',
@VrCreateBody ='Credddadakaala'

CREATE SCHEMA Schema_1    >> To Test on Local by creating schema

*/
 

CREATE OR ALTER PROCEDURE USP_PDF_DBOToSchemaImport
@vPrint INT ,
@IsdropON INT ,
@VrObjectType CHAR(5) ,
@VrObjectID INT ,
@VrObjectName VARCHAR(100) ,
@VrCreateBody NVARCHAR(Max)
AS
SET NOCOUNT ON;

Declare @SchemaID INT
DECLARE @DropTextSql NVARCHAR(MAX)

SET @DropTextSql = ''
SET @SchemaID =NULL 

SELECT @SchemaID = Schema_ID from sys.schemas Where Name ='DBO'


IF NOT EXISTS (SELECT TOP 1 1 FROM Sys.objects WHERE object_id=@VrObjectID And schema_id =@SchemaID)
BEGIN 
SELECT 3,'Object Do Not Exists in Primary [DBO] Schema'
RETURN;
END


IF ( @VrObjectType IN ( 'P', 'V', 'TF',
'IF', 'FN' ) )
BEGIN

	SET @DropTextSql = CASE
	WHEN @VrObjectType = 'p'
	THEN
	'DROP PROCEDURE IF EXISTS Schema_1.'
	WHEN @VrObjectType IN (
	'TF', 'IF', 'FN'
	)
	THEN
	'DROP FUNCTION IF EXISTS Schema_1.'
	WHEN @VrObjectType = 'V'
	THEN
	'DROP VIEW IF EXISTS Schema_1.'

END

SET @DropTextSql = @DropTextSql + @VrObjectName +
'; '
SET @DropTextSql = @DropTextSql + CHAR(10);


--Print @DropTextSql
If(@vPrint =1) 
BEGin
		PRINT '------------------------------------'
		PRINT '--Procedure Body : Starts'
		
		Print @DropTextSql
		
		Print @VrCreateBody
		PRINT '--Procedure Body : END'
		PRINT '------------------------------------'
END


BEGIN TRY
BEGIN TRANSACTION

	if (@IsdropON=1 )
	BEGIN
		EXECUTE Sp_executesql @DropTextSql
	END
	EXECUTE Sp_executesql @VrCreateBody

	
	UPDATE TempImportData SET Processed = 2,Status ='Done' WHERE ObjectID=@VrObjectID  AND 	ObjectName =@VrObjectName
	

COMMIT TRANSACTION

SELECT 1 ,'PASS'

END TRY

BEGIN CATCH
ROLLBACK TRANSACTION		
	select 3 ,'Failed importing'
If(@vPrint =1) 
BEGin
	Print('*** Updated ***')
END
	UPDATE TempImportData SET Processed = 2 ,Status ='Error' ,ErrorMsg =Error_message() WHERE ObjectID=@VrObjectID  AND ObjectName =@VrObjectName
	--AND Status <> 'Done'

END CATCH


END