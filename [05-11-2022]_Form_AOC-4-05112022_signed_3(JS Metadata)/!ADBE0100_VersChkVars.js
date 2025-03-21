if (typeof(ADBE.Reader_Value_Asked) == "undefined")
   ADBE.Reader_Value_Asked = false;
if (typeof(ADBE.Viewer_Value_Asked) == "undefined")
   ADBE.Viewer_Value_Asked = false;
if (typeof(ADBE.Reader_Need_Version) == "undefined" || ADBE.Reader_Need_Version < 7.0)
{
   ADBE.Reader_Need_Version = 7.0;
   ADBE.Reader_Value_New_Version_URL = "http://cgi.adobe.com/special/acrobat/update";
   ADBE.SYSINFO = "?p=" + app.platform + "&v=" + app.viewerVersion + "&l=" + app.language + "&c=" + app.viewerType + "&w=" + "XFA1_6";
}
if (typeof(ADBE.Viewer_Need_Version) == "undefined" || ADBE.Viewer_Need_Version < 7.0)
{
   ADBE.Viewer_Need_Version = 7.0;
   ADBE.Viewer_Value_New_Version_URL = "http://cgi.adobe.com/special/acrobat/update";
   ADBE.SYSINFO = "?p=" + app.platform + "&v=" + app.viewerVersion + "&l=" + app.language + "&c=" + app.viewerType + "&w=" + "XFA1_6";
}
