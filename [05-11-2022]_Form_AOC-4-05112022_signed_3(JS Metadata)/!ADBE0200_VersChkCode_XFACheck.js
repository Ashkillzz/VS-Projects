if (typeof(xfa_installed) == "undefined" || typeof(xfa_version) == "undefined" || xfa_version < 2.1)
{
   if (app.viewerType == "Reader")
   {
      if (ADBE.Reader_Value_Asked != true)
      {
         if (app.viewerVersion < 6.0)
         {
            if (app.alert(ADBE.Viewer_Form_string_Reader_5x, 1, 1) == 1)
               this.getURL(ADBE.Reader_Value_New_Version_URL + ADBE.SYSINFO, false);
            ADBE.Reader_Value_Asked = true;
         }
         else if (app.viewerVersion < 7.0)
         {
            if (app.alert(ADBE.Viewer_Form_string_Reader_601, 1, 1) == 1)
               app.findComponent({cType:"App", cName:"Reader7", cDesc: ADBE.Viewer_string_Update_Reader_Desc});
            ADBE.Reader_Value_Asked = true;
         }
         else
         {
            if (app.alert(ADBE.Viewer_Form_string_Reader_6_7x, 1, 1) == 1)
               app.findComponent({cType:"Plugin", cName:"XFA", cDesc: ADBE.Viewer_string_Update_Reader_Desc});
            ADBE.Reader_Value_Asked = true;
         }
      }
   }
   else
   {
      if (ADBE.Viewer_Value_Asked != true)
      {
         if (app.viewerVersion < 7.0)
            app.response({cQuestion: ADBE.Viewer_Form_string_Viewer_Older, cDefault: ADBE.Viewer_Value_New_Version_URL + ADBE.SYSINFO, cTitle: ADBE.Viewer_string_Title});
         else if (app.alert(ADBE.Viewer_Form_string_Viewer, 1, 1) == 1)
            app.findComponent({cType:"Plugin", cName:"XFA", cDesc: ADBE.Viewer_string_Update_Desc});
         ADBE.Viewer_Value_Asked = true;
      }
   }
}
