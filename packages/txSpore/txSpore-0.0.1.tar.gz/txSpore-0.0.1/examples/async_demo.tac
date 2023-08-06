"""
To run this file, simply do the following from the top-level txSpore source
directory:

    $ twistd -noy examples/async_demo.tac

This will run the demo service in the foreground. Now open a web browser and
point it to the following:

    http://localhost:8080/
"""
from twisted.application import service, internet
from twisted.web import server, resource
from twisted.web.server import NOT_DONE_YET

from txspore import client


# configuration
PORT = 8080


# supporting resource code
class UserInfo(resource.Resource):

    isLeaf = True

    def render_GET(self, request):
        template = """
            <html><body>
            <h4>User Info</h4>
            User image:<img src="%s" /><br />
            Tagline: %s<br />
            User since: %s<br />
            <a href="/userassets/?user=%s">See the assets</a> for this user
            </body></html>"""

        def writeData(userModel):
            data = template % (
                userModel.image, userModel.tagline,
                userModel.creation.strftime("%Y.%m.%s %H:%M:%S"),
                userModel.input
                )
            request.write(data)
            request.finish()

        [user] = request.args.get("user")
        d = client.getProfileInfo(user)
        d.addCallback(writeData)
        return NOT_DONE_YET


class UserAssets(resource.Resource):

    isLeaf = True

    def render_GET(self, request):
        template = """
            <html><body>
            <h4>User Assets</h4>
            <p>Click on a thumbnail to see a larger image</p>
            %s
            </body></html>
            """

        def writeData(assets):
            data = ""
            for asset in assets:
                data += """<a href="%s" alt="%s"><img src="%s" /></a>&nbsp;""" % (
                    asset.image, asset.name, asset.thumb)
            request.write(template % data)
            request.finish()

        [user] = request.args.get("user")
        d = client.getAssetsForUser(user, 0, 100)
        d.addCallback(writeData)
        return NOT_DONE_YET


class UserForm(resource.Resource):

    isLeaf = True

    def render_GET(self, request):
        return ("""
            <html><body><form action="/userpage"><span>Enter your spore
            username:</span><input type="text" name="user"/>
            <input type="submit" /></body></html>""")


# application code
application = service.Application("Demo txSpore Application")
root = resource.Resource()
root.putChild("", UserForm())
root.putChild("userpage", UserInfo())
root.putChild("userassets", UserAssets())
sporeSite = server.Site(root)
service = internet.TCPServer(PORT, sporeSite)
service.setServiceParent(application)
