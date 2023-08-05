<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="'master.kid'">
<?python

import feed
import turbogears


feeds = { "Top Stories":"http://rss.cbc.ca/lineup/topstories.xml",
	  "Technology and Science":"http://rss.cbc.ca/lineup/technology.xml",
	  "Health":"http://rss.cbc.ca/lineup/health.xml",
	  "Football":"http://rss.cbc.ca/lineup/sports-soccer.xml",
        }

parsedfeeds=feed.getFeeds(feeds)

?>

<head>
      <title>${page.pagename}</title>
      
      <meta http-equiv="Content-Type" content="text/html; charset=windows-1251"/>
 <style type="text/css">
<!--
  .header {font-family:Tahoma, sans-serif; font-size: 12px; COLOR:#2FFFFF; padding-left:10; padding-right:5; font-weight:900 }
  .text {font-family:Verdana,sans-serif; font-size: 11px; color:#000000; padding-left:20; padding-right:10 }
  .text2 {font-family:Tahoma,sans-serif; font-size: 11px; color:#000000; padding-left:20; padding-right:10; font-weight:100; }
  .news {font-family:Arial, sans-serif; font-size: 9px; color:#ffffff; padding-left:10; padding-right:5; font-weight:900; }
  table { border-collapse: collapse; border:0px;}
  th { padding: 0px; text-align: center;}
  tr { border-top: 0px; border-bottom: 0px; border:0px}
  td { border-bottom: 0px; padding: 0px;}
  a:link{text-decoration: none; color:#ffffff}
  a:visited{text-decoration: none; color: #ffffff}
  a:hover{text-decoration: none; color: #ffffff}
  a:active{text-decoration: none; color: #ffffff}
--></style>
</head>

<body leftmargin="0" topmargin="0" bgcolor="#283150" marginheight="0" marginwidth="0">
<!-- ImageReady Slices (co-casher-33.psd) -->
<table align="center" border="0" cellpadding="0" cellspacing="0" height="100%" width="780"  >
	<tbody>
         <tr>  
 	  <td valign="top" width="192">
	     <div  py:for="feed in parsedfeeds" class="text" style="font-size: 11px; color: rgb(255, 255, 255); padding-left:0;">
 	       ${rss_widget.display(feed)}
	     </div>
         </p>
        </td>
	</tr>
       </tbody>
       </table>
<!-- End ImageReady Slices -->
</body></html>
