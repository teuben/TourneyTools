' based on: http://www.oooforum.org/forum/viewtopic.phtml?t=15402
' install this in your OpenOffice macro repository
Private cFileIN As String
Private cFileOut As String
Private cDstType As String
Private cDstURL As String
Private cExportFilter As String
Private cSrcName As String
Private cSrcFolder As String
Private cDstFolder as String

Private oExportOptions As Object


Sub CSV2XLS(Optional dirName As String)

' Setup for export to MS xls native file
   oExportOptions = Array()
   cFileIn = ""
   cFileOut = ""
   cExportFilter = ""   
   cSrcFolder = "/tmp/csv/"
   cDstFolder = "/tmp/csv/"
   cDstType = "xls"
   cSrcFolder = dirName + "/"
   cDstFolder = cSrcFolder
   
' Start the Loop to get all CSV files.  NOTE!!  This will momentarily
' display each sheet opened on the screen, so if you have many files,
' make use of the "hidden" argument in the MakePropertyValue function
' documented elsewhere in this forum.

   cFileIn = Dir$(cSrcFolder + "/*.csv")
   Do While cFileIn <> ""
      cSrcName = cSrcFolder + cFileIn
   ' Open the CSV file and import
      oDoc = StarDesktop.loadComponentFromURL(_
               ConvertToURL( cSrcName ),_
               "_blank", 0,_
               Array( _
                  MakePropertyValue( "FilterName", "Text - txt - csv (StarCalc)"),_
                  MakePropertyValue( "FilterOptions", _
                  CStr(Asc(","))+","+CStr(Asc(""""))+",0,1,1/1" ) ) )

   ' Build the name of the new document and store.   
   
      cDstName = Left( cFileIn, Len( cFileIn ) - 4 )
      cDstName = cDstName + "." + LCase(cDstType)
      
   ' Build the URL of the new document. 
      
      cDstURL = ConvertToUrl( cDstFolder + cDstName )
      oExportOptions = Array( MakePropertyValue( "FilterName", cExportFilter ) )
      oDoc.storeToUrl( cDstURL, oExportOptions )
      oDoc.dispose()

      cFileIn = Dir$
      Loop
      
End Sub

Function MakePropertyValue( Optional cName As String, Optional uValue ) As com.sun.star.beans.PropertyValue
   oPropertyValue = createUnoStruct( "com.sun.star.beans.PropertyValue" )
   If Not IsMissing( cName ) Then
      oPropertyValue.Name = cName
   EndIf
   If Not IsMissing( uValue ) Then
      oPropertyValue.Value = uValue
   EndIf
   MakePropertyValue() = oPropertyValue
End Function 

