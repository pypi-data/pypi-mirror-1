// Copyright(c) gert.cuykens@gmail.com
import java.io.*;
import java.sql.*;
import javax.naming.*;
import javax.servlet.*;
import javax.servlet.http.*;
import javax.xml.parsers.*;
import org.xml.sax.SAXException;
import org.xml.sax.InputSource;
import org.w3c.dom.*;

public class Query extends HttpServlet 
{
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException
    {
        response.setContentType("text/xml;charset=UTF-8");
        BufferedReader in = request.getReader();
        PrintWriter out = response.getWriter();
        try
        {
            out.println("<?xml version='1.0' encoding='UTF-8'?>\n");
            out.println("<root>\n");
            DocumentBuilder parser = DocumentBuilderFactory.newInstance().newDocumentBuilder();
            Document doc = parser.parse(new InputSource(in));
            String usr = this.getTag(doc,"user");
            String pwd = this.getTag(doc,"password");
            String db  = this.getTag(doc,"database");
            String sql = this.getTag(doc,"sql");
            out.println(" <sql>"+this.escapeXml(sql)+"</sql>\n");
            Class.forName("com.mysql.jdbc.Driver");
            Connection cn = DriverManager.getConnection("jdbc:mysql://localhost/"+db+"?user="+usr+"&password="+pwd);
            try
            {
                //cn.setAutoCommit(flase);
                Statement st = cn.createStatement();
                st.execute(sql);
                ResultSet rs=st.getResultSet();
                int count = rs.getMetaData().getColumnCount();
                while (rs.next())
                {
                    out.println(" <record index='"+(rs.getRow()-1)+"'>\n");
                    for (int c=1;c<=count;c++)
                    {
                        out.println("  <"+rs.getMetaData().getColumnName(c)+
                                    ">"+this.escapeXml(rs.getString(c))+
                                    "</"+rs.getMetaData().getColumnName(c)+
                                    ">\n");
                    }
                    out.println(" </record>\n");
                }
                //connection.commit();
                //ResultSet rk = statement.getGeneratedKeys();
                //out.println(" <key>"+resultKey.getString(1)+"</key>");
                //rk.close();
                rs.close();
                st.close();
            }
            finally {cn.close();}
        }
        catch (ParserConfigurationException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (SQLException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (IOError ex)     {out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (SAXException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (ClassNotFoundException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        finally
        {
            out.println("</root>");
            out.close();
        }
    }
    
    protected String getTag(Document doc, String tag)
    {
        String v = "";
        NodeList nl1=doc.getElementsByTagName(tag);
        int tCount=doc.getElementsByTagName(tag).getLength();
        for(int t=0;t<tCount;t++)
        {
            NodeList nl2=nl1.item(t).getChildNodes();
            int cCount=nl2.getLength();
            for(int c=0;c<cCount;c++)
            {
                Node n=nl2.item(c);
                v=v+ n.getNodeValue();
            }
        }
        return v;
    }
    
    protected String escapeXml(String v)
    {
        //v=v.replace("\"","&quot;");
        //v=v.replace("'","&apos;");
        //v=v.replace("&","&amp;");
        v=v.replace("<","&lt;");
        v=v.replace(">","&gt;");
        return v;
    }
 
}
