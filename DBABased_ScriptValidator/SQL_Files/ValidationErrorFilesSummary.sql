USE Ankit_ValidatorDB
GO
--============

DROP TABLE IF EXISTS DBO.ValidationErrorFilesSummary
GO
CREATE TABLE DBO.ValidationErrorFilesSummary (
PackageID VARCHAR(50) NOT NULL ,
FileID VARCHAR(200) NOT NULL ,
ErrorCode VARCHAR(50) ,
ErrorMessage VARCHAR(max) ,
ErrCount INT ,
MarkDeleted INT
)


DROP TABLE IF EXISTS DBO.ValidatorMailDetail
GO
CREATE TABLE DBO.ValidatorMailDetail (
PackageID VARCHAR(50) NOT NULL ,
FileID VARCHAR(200) NOT NULL ,
AuthorsName VARCHAR(500) ,
MailID VARCHAR(500) ,
)

--DROP TABLE IF EXISTS DBO.DifferentAUTHOR
--GO
--CREATE TABLE DBO.DifferentAUTHOR (
--OrgAuthorsName VARCHAR(500) ,
--ChangedAuthorName VARCHAR(500)
--)

--INSERT INTO DBO.DifferentAUTHOR (OrgAuthorsName ,ChangedAuthorName)
--SELECT 'sunilr','sunil.rathor' UNION ALL 
--SELECT 'asaxena','ashish.saxena' UNION ALL 
--SELECT 'vrathor','virendra.rathore'
