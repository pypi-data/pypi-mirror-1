from turbogears import widgets
import feedparser

class RSSWidget(widgets.Widget):
    template = '''
    <table xmlns:py="http://purl.org/kid/ns#"
      class="rsswidget"
      border="0">
      <tr>
        <b>
        <th py:content="value.feed.lastbuilddate"/>
        </b>
      </tr>
      <tr>
         <th py:content="value.feed.title" style="color:red"/>
      </tr>
      <?python idx=0 ?> 
      <tr py:for="entry in value.entries">
         <?python idx=idx+1?>
         <td py:if="idx &lt;4">
         <table xmlns:py="http://purl.org/kid/ns#">
           <tr><td py:content="entry.title" style="color:#2b9fe8; font-style:italic"/></tr>
           <tr><td py:content="entry.description" style="padding:5px"/></tr>
           <tr><td><a href="${entry.link}"><img src="../static/images/r6.jpg" alt="" border="0" height="28" width="192"/></a></td></tr>
         </table>  
         </td>
      </tr>
    </table>
    '''

    def display(self, feed):
        try:
            return self.__class__.__bases__[0].display(self,feed)
        except:
            return "Feed is unavailable"
