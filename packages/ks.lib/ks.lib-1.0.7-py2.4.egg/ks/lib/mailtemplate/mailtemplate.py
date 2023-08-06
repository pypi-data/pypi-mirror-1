### -*- coding: utf-8 -*- #############################################
# Разработано компанией Ключевые Решения (http://keysolutions.ru/)
# Все права защищены, 2006-2007
#
# Developed by Key Solutions (http://keysolutions.ru/)
# All right reserved, 2006-2007
#######################################################################
"""template function for mailtemplate package

$Id: mailtemplate.py 35349 2008-10-24 09:01:22Z anatoly $
"""
__author__  = ""
__license__ = "ZPL"
__version__ = "$Revision: 35349 $"
__date__ = "$Date: 2008-10-24 12:01:22 +0300 (Fri, 24 Oct 2008) $"

from email import Message, Header, MIMEMultipart, MIMEText, Utils, Encoders
import email
import re
from email.MIMEBase import MIMEBase

from formatter import AbstractFormatter, DumbWriter
import htmllib
from StringIO import StringIO


class HTMLParser(htmllib.HTMLParser):

    def start_style(self, *args):
        self.save_bgn()

    def end_style(self, *args):
        self.save_end()
        
    def anchor_end(self):
        """This method is called at the end of an anchor region.

        The default implementation adds a textual footnote marker using an
        index into the list of hyperlinks created by the anchor_bgn()method.

        """
        if self.anchor:
            #self.handle_data("[%d]" % len(self.anchorlist))
            self.anchor = None


def template(use_container=False,
             use_alternative=False,
             charset=None,
             mime='text/plain',
             filename='body',
             mail_header='',
             mail_footer='',
             attaches = (),
             text_headers={},
             address_headers={},
             data={},
             mail_body=''):
    
    """ Return email based on template """
    
    if use_container:
        ma = MIMEMultipart.MIMEMultipart()
        
        mal = []
        
        if mail_header:
            mai = Message.Message()
            mai.set_type(mime)
            mai.set_payload(mail_header % data)
            mai.set_charset(charset)
            mai.set_param("format", "flowed")
            mai.add_header("Content-Disposition", "inline")
            mal.append(mai)

        mai = Message.Message()
        mai.set_type(mime)
        
        if mime == 'text/plain':
            f = StringIO()
            HTMLParser(AbstractFormatter(DumbWriter(f))).feed(mail_body)
            mail_body = f.getvalue()
            
        mai.set_payload(mail_body)
        mai.add_header("Content-Disposition", "inline", filename=filename)
        mal.append(mai)
        
        if mail_footer:
            mai = Message.Message()
            mai.set_type(mime)
            mai.set_payload(mail_footer % data)
            mai.set_charset(charset)
            mai.set_param("format", "flowed")
            mai.add_header("Content-Disposition", "inline")
            mal.append(mai)
        
        #attaches allowed only for multipart emails
        for a in attaches:
            mime = a['mime'].split('/')
            part = MIMEBase(mime[0], mime[1])
            part.set_payload(a['filedata'])
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % a['filename'])
            mal.append(part)
            ma.set_payload(mal)

    else:
        ma = Message.Message()
        ma.set_type(mime)

        try:
            html_charset = re.compile(".*;\s*charset=(.*)(;|\s*$)").match(mime).group(1)
        except (KeyError, IndexError, AttributeError):
            #XXX что-нибудь придумаю
            #warning(_("Body can't be converted because charset is unknown"),2)
            pass
        else:
            try:
                mail_body = mail_body.decode(html_charset).encode(charset, "ignore")
            except Exception,msg:
                #XXX и здесь
                #warning(_("Body can't be converted because of \"%s\""),2,msg)
                pass

        body = ''.join((mail_header % data, mail_body, mail_footer % data))
        ma.set_payload(body)
        ma.set_charset(charset)

        if use_alternative and ma.get_content_subtype() == 'html':
            f = StringIO()
            HTMLParser(AbstractFormatter(DumbWriter(f))).feed(body)
            mt = MIMEText.MIMEText(f.getvalue(), _charset=charset)

            m = MIMEMultipart.MIMEMultipart(_subtype='alternative')
            m.set_payload([ma, mt])
            ma = m


    # 'Subject'
    for header, hs in text_headers.iteritems():
        ma.add_header(header, Header.Header(hs % data, charset=charset).encode())

    # 'From','To','Reply-To'
    for header, hs in address_headers.iteritems():
        name, addr = Utils.parseaddr(hs % data)
        ma.add_header(header, Utils.formataddr((Header.Header(name, charset=charset).encode(), addr)))

    return ma


def set_text_header(msg, header, value, charset=None):
    del msg[header]
    msg.add_header(header, Header.Header(value, charset=charset).encode())


def set_address_header(msg, header, value, charset=None):
    del msg[header]
    name, addr = Utils.parseaddr(value)
    msg.add_header(header, Utils.formataddr((Header.Header(name, charset=charset).encode(), addr)))


if __name__ == '__main__':
    import sys, os

    def hack(prefix, d, name, value):
        if name.startswith(prefix):
            d[name[len(prefix):]] = value
            return True
        return False

    bool_args = ('use_container', 'use_alternative')
    kw = {}
    text_headers = {}
    address_headers = {}
    data = {}
    options = {}
    for arg in sys.argv[1:]:
        name, value = tuple(arg.split('=', 1))
        if name in bool_args:
            kw[name] = eval(value)
        elif hack('text_', text_headers, name, value) or \
             hack('address_', address_headers, name, value) or \
             hack('data_', data, name, value) or \
             hack('-', options, name, value):
             continue
        kw[name] = value
    kw['text_headers'] = text_headers
    kw['address_headers'] = address_headers
    kw['data'] = data
    body = template(**kw).as_string(unixfrom=False)
    if 'sendmail' in options:
        p=os.popen(options['sendmail'] % data, 'w')
        try:
            p.write(body)
        finally:
            p.close()
    else:
        print body
