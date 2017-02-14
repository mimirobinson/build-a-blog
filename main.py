#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

#set up jinja
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Post(db.Model):
    #Post class with title and body
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        more = "N"
        page = self.request.get("page")

        #if page was not sent as a parameter, default the page to 1(main)
        if page == "":
            page = 1
        else:
            page = int(page)

        #return 5 posts per page; use the page number to determine the offset.
        #if page 1, then get posts 0 - 4, if page 2, get posts 5 - 9
        posts = get_posts(5, (page - 1) * 5)

        #check to see if there are posts for the next page. If so, set the
        #more tag to true.
        if(posts.count(limit = 5, offset=(page*5)) > 0):
            more = "Y"
        self.render("index.html", posts=posts, error="", more=more, page=page)

class NewPost(Handler):
    def get(self):
        #render basic add new post page
        self.render("add.html", title="", body="", error="")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
        #if both title and body are input, add post to database and redirect
        #to blog page
            newpost = Post(title=title, body=body)
            newpost.put()
            self.redirect("/blog/" + str(newpost.key().id()))
        else:
        #if either title or body are missing, redisplay new post page with
        #previously entered content and error message
            error = "Both a title and blog post are required."
            self.render("add.html", title=title, body=body, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        a = Post.get_by_id(long(id))
        self.render("post.html", post = a)

def get_posts(limit, offset):
    sql_string = ("SELECT * FROM Post ORDER BY created DESC LIMIT " + str(limit)
        + " OFFSET " + str(offset))
    posts = db.GqlQuery(sql_string)
    return posts

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
