--USE ControlTeam_Prod_DB
--GO

USE Ankit_ValidatorDB
GO
-----------------

CREATE OR ALTER PROCEDURE USP_PDF_GetValidatorAuthorDetails 
@arg_PackgeID VARCHAR(max) ,
@arg_FileLoc VARCHAR(max) 

As

Declare @v_AuthorsName varchar(500)
Declare @v_AuthorsMail varchar(2000)
Declare @vr_FID VARCHAR(50)

SELECT @vr_FID = ltrim(Rtrim(File_Id)) FROM [dbo].[SVN_Files] With(NOLOCk) WHERE Shared_Path =Ltrim(Rtrim(@arg_FileLoc)) 
and Package_ID = @arg_PackgeID

IF (@vr_FID IS NOT NULL )
BEGIN
 
	SELECT @v_AuthorsName =COALESCE(RTRIM(@v_AuthorsName) + ',','') + AuthorsName , @v_AuthorsMail =COALESCE(RTRIM(@v_AuthorsMail) + ',','') + MailID 
			FROM DBO.ValidatorMailDetail WITH(NOLOCK)
			WHERE PackageID=Ltrim(Rtrim(@arg_PackgeID)) AND FileID=Ltrim(Rtrim(@vr_FID)) AND AuthorsName NOT IN (		
			SELECT SVNAuthorName  FROM SVNAuthor_EmailLookup WHERE IsConfig = 1)


END

IF @v_AuthorsName IS NOT NULL And @v_AuthorsMail IS NOT NULL
BEGIN	
	Select @v_AuthorsName as 'AuthorName' ,@v_AuthorsMail as 'MailIDs'
END
ELSE
	Select 0