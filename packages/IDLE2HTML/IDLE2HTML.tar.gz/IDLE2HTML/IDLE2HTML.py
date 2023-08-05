# IDLE2HTML - IDLE extension
# saves the contents of the editwindow (file or shell)
# to a html file using css styles
#
# creator:        d2m <michael@d2m.at>
# 0.1/2006-07-22: initial revision
#
# todo:           check for valid css color values
#                 use elementtree for html generation

import Tkinter 
import tkFileDialog
import cgi

class IDLE2HTML:
    menudefs=[('options',[('Save to HTML', '<<idle2html>>')])]

    def __init__(self,editwin):
        self.editwin=editwin
        self.text=editwin.text
            
    def idle2html_event(self, event=None):
        filetypes = [
            ("All HTML files", "*.htm *.html", "TEXT"),
            ("All files", "*"),
            ]
        filename=tkFileDialog.SaveAs(master=self.text, filetypes=filetypes).show()
        f=open(filename,'w')
        f.write(self.idle2html())
        f.close()
        
    def idle2html(self):
        """format tags 2 html
        """
        out=['<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \
"http://www.w3.org/TR/2002/REC-xhtml1-20020801/DTD/xhtml1-transitional.dtd">\n']
        out.append('<html>\n<head>\n<title>IDLE2HTML</title>\n')
        out.append('<meta name="generator" content="IDLE2HTML - IDLE extension" />\n')
        out.append('<style type="text/css">\n')
        for tagname in self.text.tag_names():
            out.append('.%s {color: %s; background: %s;}\n' % (
                tagname,
                self.text.tag_cget(tagname,'foreground'),
                self.text.tag_cget(tagname,'background'),
                )
                       )
        out.append('</style>\n')
        out.append('</head>\n<body>\n<pre>')
        for tagname,content,dummy in self.text.dump('1.0',self.text.index('end')):
            if tagname=='tagon' and content != 'SYNC':
                out.append('<span class="'+content+'">')
            if tagname=='text':
                out.append(cgi.escape(content))
            if tagname=='tagoff' and content != 'SYNC':
                out.append('</span>')
        out.append('</pre>\n</body>\n</html>')
        return ''.join(out)

