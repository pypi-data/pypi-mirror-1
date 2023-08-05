import logging

import cherrypy

import turbogears
import model

from turbogears import controllers, expose, validate, redirect
from turbogears import identity

from model import Page, hub
from docutils.core import publish_parts
from sqlobject import SQLObjectNotFound 
from turbogears import validators
from turbogears.toolbox.catwalk import CatWalk

from hlevca import json
from hlevca import rsswidget
from hlevca import weatherwidget

import re
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

log = logging.getLogger("hlevca.controllers")
rss_widget = rsswidget.RSSWidget()
weather_widget = weatherwidget.WeatherWidget()


class Members(controllers.Controller):
    @turbogears.expose(html="hlevca.templates.users")
    def index(self):
        users = model.Member.select()
        return dict(users=users)

    @turbogears.expose(html="hlevca.templates.user")
    def default(self, memberID):
        try:
            memberID = int(memberID)
            member = model.Member.get(memberID)
        except (ValueError, model.SQLObjectNotFound):
            raise cherrypy.NotFound
        else:
            return dict(member=member)

    @turbogears.expose()
    def add(self, email):
        # Remove extra spaces
        email = email.strip()
        # Remove null bytes (they can seriously screw up the database)
        email = email.replace('\x00', '')
        if email:
            try:
                member = model.Member.byEmail(email)
            except model.SQLObjectNotFound:
                member = model.Member(email=email)
                turbogears.flash("User %s added!" % email)
            else:
                turbogears.flash("User %s already exists!" % email)
        else:
            turbogears.flash("E-mail must be non-empty!")
        redirect('index')

    @turbogears.expose()
    def remove(self, email):
        try:
            member = model.Member.byEmail(email)
        except model.SQLObjectNotFound:
            turbogears.flash("The user %s does not exist. (Did someone else remove it?)" % email)
        else:
            for memberList in member.lists:
                for item in memberList.items:
                    item.destroySelf()
                memberList.destroySelf()
            member.destroySelf()
            turbogears.flash("User %s removed!" % email)
        redirect('index')


########################################
class Root(controllers.RootController):

    users = Members()
    catwalk = CatWalk(model)
    
    @expose(html="hlevca.templates.frontpage")
    def index(self, pagename="MainPage"):
        try:
            page = Page.byPagename(pagename)
            page.pagename=pagename
        except SQLObjectNotFound:
            raise cherrypy.HTTPRedirect(turbogears.url("/notfound", pagename= pagename))
        #top_content = publish_parts(page.top_data, writer_name="html")["html_body"]
        #bot_content = publish_parts(page.bot_data, writer_name="html")["html_body"]
        #right_content = publish_parts(page.right_data, writer_name="html")["html_body"]
        #p1_content = publish_parts(page.picture1, writer_name="html")["html_body"]
        #p2_content = publish_parts(page.picture2, writer_name="html")["html_body"]
        p3_content = publish_parts(page.picture3, writer_name="html")["html_body"]
        p4_content = publish_parts(page.picture4, writer_name="html")["html_body"]
        p5_content = publish_parts(page.picture5, writer_name="html")["html_body"]
        root = str(turbogears.url("/"))
        #content = wikiwords.sub(r'<a href="%s\1">\1</a>' % root, content)
        cherrypy.response.headerMap["Content-Type"] += ";charset=utf-8"
        #return dict(data=content, pagename=page.pagename, rss_widget=rss_widget, weather_widget = weather_widget)
        return dict(top_data=page.top_data, bot_data=page.bot_data, right_data= page.right_data,\
                    picture1=page.picture1, picture2=page.picture2, picture3=p3_content, picture4=p4_content, picture5=p5_content, \
                    page=page, rss_widget=rss_widget, weather_widget = weather_widget)
    
    @expose(html="hlevca.templates.frontpage")
    def travel(self, pagename="Travel"):
        try:
            page = Page.byPagename(pagename)
            page.pagename=pagename
        except SQLObjectNotFound:
            raise cherrypy.HTTPRedirect(turbogears.url("/notfound", pagename= pagename))
        top_content = publish_parts(page.top_data, writer_name="html")["html_body"]
        bot_content = publish_parts(page.bot_data, writer_name="html")["html_body"]
        p3_content = publish_parts(page.picture3, writer_name="html")["html_body"]
        p4_content = publish_parts(page.picture4, writer_name="html")["html_body"]
        p5_content = publish_parts(page.picture5, writer_name="html")["html_body"]
        root = str(turbogears.url("/"))
        cherrypy.response.headerMap["Content-Type"] += ";charset=utf-8"
        return dict(top_data=top_content, bot_data=bot_content, right_data= page.right_data,\
                    picture1=page.picture1, picture2=page.picture2, picture3=p3_content, picture4=p4_content, picture5=p5_content, \
                    page=page, rss_widget=rss_widget, weather_widget = weather_widget)

    @expose(html="hlevca.templates.edit")
    def edit(self, pagename):
        page = Page.byPagename(pagename)
        return dict(pagename=page.pagename, data=page.data, new=False)

    @turbogears.expose(html="hlevca.templates.edit") 
    def notfound(self, pagename): 
        return dict(pagename=pagename, data="", new=True) 

    @turbogears.expose(validators=dict(new=validators.StringBoolean()))
    def save(self, pagename, data, submit, new):
        hub.begin()
        if new:
            page = Page(pagename=pagename, data=data)
        else:
            page = Page.byPagename(pagename)
            page.data = data
        hub.commit()
        hub.end()
        turbogears.flash("Changes saved!")
        raise cherrypy.HTTPRedirect(turbogears.url("/%s" % pagename))

    @expose(html="hlevca.templates.page")
    def default(self, pagename):
        return self.index(pagename)

    @turbogears.expose(html="hlevca.templates.pagelist")
    @expose("json")
    def pagelist(self):
        pages = [page.pagename for page in Page.select(orderBy=Page.q.pagename)]
        return dict(pages=pages)
    
    
    @expose(template="hlevca.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):

        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= cherrypy.request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= cherrypy.request.headers.get("Referer", "/")
        cherrypy.response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=cherrypy.request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        #raise redirect("http://www.hlevca.com:8082/")
        raise redirect(turbogears.url(self.getURL()+"/"))


    @turbogears.expose(template="hlevca.templates.users")
    def addList(self, memberID, title):
        try:
            memberID = int(memberID)
            member = model.Member.get(memberID)
        except (ValueError, model.SQLObjectNotFound):
            raise cherrypy.NotFound
        else:
            # Remove extra spaces
            title = title.strip()
            # Remove null bytes (they can seriously screw up the database)
            title = title.replace('\x00', '')
            if title:
                l = model.List(title=title, member=member)
                turbogears.flash("List created!")
            else:
                turbogears.flash("Title must be non-empty!")
        raise cherrypy.HTTPRedirect(self.getURL()+'/users/%s' % memberID)

    @turbogears.expose(template="hlevca.templates.users")
    def removeList(self, memberID, listID):
        try:
            listID = int(listID)
            l = model.List.get(listID)
        except ValueError:
            turbogears.flash("Invalid list!")
        except model.SQLObjectNotFound:
            turbogears.flash("List not found! (Did someone else remove it?)")
        else:
            for item in l.items:
                item.destroySelf()
            l.destroySelf()
            turbogears.flash("List deleted!")
        raise cherrypy.HTTPRedirect(self.getURL()+'/users/%s' % memberID)

    @turbogears.expose(template="hlevca.templates.users")
    def addItem(self, memberID, listID, value):
        try:
            listID = int(listID)
            l = model.List.get(listID)
        except ValueError:
            turbogears.flash("Invalid list!")
        except model.SQLObjectNotFound:
            turbogears.flash("List not found! (Did someone else remove it?)")
        else:
            # Remove extra spaces
            value = value.strip()
            # Remove null bytes (they can seriously screw up the database)
            value = value.replace('\x00', '')
            if value:
                item = model.Item(listID=listID, value=value)
                turbogears.flash("Item added!")
            else:
                turbogears.flash("Item must be non-empty!")
        #raise cherrypy.HTTPRedirect('/users/%s' % memberID)
        raise redirect(self.getURL()+'/users/%s' % memberID)

    @turbogears.expose(template="hlevca.templates.users")
    def removeItem(self, memberID, itemID):
        try:
            itemID = int(itemID)
            item = model.Item.get(itemID)
        except ValueError:
            turbogears.flash("Invalid item!")
        except model.SQLObjectNotFound:
            turbogears.flash("No such item! (Did someone else remove it?)")
        else:
            item.destroySelf()
            turbogears.flash("Item removed!")
        raise cherrypy.HTTPRedirect(self.getURL()+'/users/%s' % memberID)

    @turbogears.expose(format="json")    
    def editItem(self, itemID, value):
        try:
            itemID = int(itemID)
            item = model.Item.get(itemID)
        except (ValueError, model.SQLObjectNotFound):
            raise CherryPy.NotFound
        else:
            # Remove extra spaces
            value = value.strip()
            # Remove null bytes (they can seriously screw up the database)
            value = value.replace('\x00', '')
            if value:
                item.value = value
            else:
                value = item.value
        return dict(value=value)

    @turbogears.expose()
    def about(self, author="Bogdan Hlevca"):
        return "This Site was written by %s." % author

    @turbogears.expose()
    def downloads(self, author="Bogdan Hlevca"):
        return '''
            <html>
            <body>
            <a href="./static/files/rsswidget.tar.bz2">Download rsswidget</a>
            <br/><br/>
             <a href="./static/files/Archive.zip">Download Botez</a> 
            </body>
            </html>
            '''

    def getURL(self):
        return "http://www.hlevca.com:8082"
