// Copyright(c) gert.cuykens@gmail.com
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class File extends HttpServlet
{
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException
    {
        //try 
        //{
            HttpSession session = request.getSession(true);
            Double  r = (Double) session.getAttribute("random");
            Integer g = (Integer) session.getAttribute("gid");
            String type = request.getQueryString();
            if(type.equals("png"))
            {
                //Class.forName("Png");
                Png.create(response);
            }
            else if(type.equals("upload"))
            {
                //Class.forName("Upload");
                Upload.save(response);
            }
            else 
            {
                PrintWriter out = response.getWriter();
                out.println("<?xml version='1.0' encoding='UTF-8'?>\n");
                out.println("<error>file not found</error>");
                response.setContentType("text/xml;charset=UTF-8");
            }
        //}
        //catch (ClassNotFoundException ex){}
    }
}
