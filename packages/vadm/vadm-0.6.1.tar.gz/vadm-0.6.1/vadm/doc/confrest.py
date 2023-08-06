import py

try:
    from py.__.rest.resthtml import Project as BaseProject
except ImportError:
    from py.__.misc.rest import Project as BaseProject

class Project(BaseProject): # used for confrest.py files 
    def process(self, path):
        BaseProject.process(self, path) 
        p = self.get_htmloutputpath(path)
        out = p.read()
        out = out.replace("</body>", googlefragment + "</body>")
        p.write(out)

    def get_htmloutputpath(self, path):
        return path.new(ext='html')


googlefragment = """
<script type="text/javascript">
var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
try {
var pageTracker = _gat._getTracker("UA-7597274-6");
pageTracker._trackPageview();
} catch(err) {}</script>
"""
