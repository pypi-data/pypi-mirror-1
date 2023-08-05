// Copyright(c) gert.cuykens@gmail.com
import java.io.*;
import javax.servlet.http.*;

public class Upload
{
    public static void save(HttpServletResponse response)
    throws IOException
    {
        PrintWriter out = response.getWriter();
        out.println("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        out.println("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">");
        out.println("<!-- Copyright(c) gert.cuykens@gmail.com -->");
        out.println("<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\">");
        out.println(" <head>");
        out.println("  <title>upload</title>");
        out.println(" </head>");
        out.println(" <body onload=\"opener.getElementById('').src='../file/file?png'\">");
        out.println("  <p>upload succesfull</p>");
        out.println(" </body>");
        out.println("</html>");
        response.setContentType("text/xml;charset=UTF-8");
    }
}