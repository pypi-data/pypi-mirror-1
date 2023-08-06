// Copyright(c) gert.cuykens@gmail.com
import java.io.*;
import java.sql.*;
import javax.sql.DataSource;
import javax.naming.*;
import javax.servlet.*;
import javax.servlet.http.*;
import javax.xml.parsers.*;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.w3c.dom.*;

public class Register extends HttpServlet
{
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
            HttpSession session = request.getSession(true);
            session.setAttribute("random",Math.random());
            DocumentBuilder parser = DocumentBuilderFactory.newInstance().newDocumentBuilder();
            Document doc = parser.parse(new InputSource(in));
            String cmd = this.getTag(doc,"cmd");
            String email = this.getTag(doc,"email");
            String pwd = this.getTag(doc,"pwd");
            String pwn = this.getTag(doc,"pwn");
            String name = this.getTag(doc,"name");
            String adress = this.getTag(doc,"adress");
            String city = this.getTag(doc,"city");
            String country = this.getTag(doc,"country");
            String phone = this.getTag(doc,"phone");
            out.println(this.reg(cmd,email,pwd,pwn,name,adress,city,country,phone,session));
        }
        catch (NamingException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (ParserConfigurationException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (SQLException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (IOError ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
        catch (SAXException ex){out.println(" <error>"+this.escapeXml(ex.getMessage())+"</error>\n");}
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
    
    protected String reg(String cmd,String email,String pwd,String pwn,String name,String adress,String city,String country,String phone,HttpSession session)
    throws NamingException,SQLException
    {
        String xml="";
        if(cmd.equals("logout"))
        {
             session.invalidate();
             xml=" <text>logout succesfull</text>\n";
        }
        else 
        {
            Context initContext = new InitialContext();
            Context webContext = (Context) initContext.lookup("java:/comp/env");
            DataSource ds = (DataSource) webContext.lookup("jdbc/pool");
            Connection cn = ds.getConnection();
            try
            {
                Statement st = cn.createStatement();
                if(cmd.equals("delete"))
                {
                    session.invalidate();
                    st.execute("DELETE FROM `register` WHERE `email`='"+email+"' AND pwd='"+pwd+"'");
                    xml=" <alert>succesfull removed</alert>";
                } 
                else if (cmd.equals("update"))
                {
                    st.execute("UPDATE `register` SET `pwd`='"+pwn+"', `name`='"+name+"', `adress`='"+adress+"', `city`='"+city+"', `country`='"+country+"', `phone`='"+phone+"' WHERE `email`='"+email+"' AND `pwd`='"+pwd+"'");
                    xml=" <alert>succesfull updated</alert>";
                } 
                else if (cmd.equals("select"))
                {
                    try{st.execute("INSERT INTO `register` VALUES ('"+email+"','"+pwd+"','"+name+"','"+adress+"','"+city+"','"+country+"','"+phone+"',0,0)");}
                    catch(SQLException ex){/*duplicates*/}
                    xml=  " <sql>SELECT email,name,adress,city,country,phone,id,gid FROM register WHERE `email`='"+email+"' AND `pwd`='"+pwd+"'</sql>";
                    st.execute("SELECT email,name,adress,city,country,phone,id,gid FROM register WHERE `email`='"+email+"' AND `pwd`='"+pwd+"'");
                    ResultSet rs=st.getResultSet();
                    int columns = rs.getMetaData().getColumnCount();
                    while (rs.next())
                    {
                        xml+=" <record index='"+(rs.getRow()-1)+"'>\n";
                        for (int c=1;c<=columns;c++)
                        {
                            xml+="  <"+rs.getMetaData().getColumnName(c)+
                                 ">"+this.escapeXml(rs.getString(c))+
                                 "</"+rs.getMetaData().getColumnName(c)+
                                 ">\n";
                            if(c==8)session.setAttribute("gid",rs.getInt(8));
                        }
                        xml+=" </record>\n";
                    }
                    if (!rs.first())xml=" <error>wrong password</error>\n";
                    rs.close();
                }
                st.close();
            }
            finally {cn.close();}
        }
        return xml;
    }
}
