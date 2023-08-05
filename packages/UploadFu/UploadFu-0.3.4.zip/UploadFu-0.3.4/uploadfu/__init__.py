from __future__ import with_statement

__version__ = "UploadFu/0.3.3r-r%s" % "$Revision: 67 $".split(':')[1].strip(' $')

import mechanize
import sys
import os
import glob
import subprocess
import re
import traceback
import urllib2
import httplib
import webbrowser 
from configobj import ConfigObj
import logging
import logging.handlers

def set_logging(WORK_DIR):
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    uploadfu_log = logging.handlers.TimedRotatingFileHandler(os.path.join(WORK_DIR,'uploadfu.log'), 'midnight', backupCount=20)
    uploadfu_log.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s [%(name)-10s] %(message)s', '%a, %d %b %Y %H:%M:%S'))
    uploadfu_log.setLevel(logging.NOTSET)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)

    logger.addHandler(uploadfu_log)
    logger.addHandler(console_log)


def get_work_dir():
    if sys.platform == "win32":
        import _winreg
        hkey = None
        try:
            hkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Python\\PythonCore\\2.5\\InstallPath")
            if hkey is not None:
                v, t = _winreg.QueryValueEx(hkey, "")
                python_path = v
        except:
            pass
        finally:
            _winreg.CloseKey(hkey)
        return python_path, os.path.join(python_path,'Scripts')
    else:
        work_path = os.path.expanduser("~/.uploadfu")
        if not os.path.isdir(work_path):
            os.mkdir(work_path)
        return "", work_path
def match_stuff(defaults_dict, regex_dict, text):
    v = {}
    for i in defaults_dict:
        v[i] = defaults_dict[i]
    
    for exp in regex_dict:
        mlist = [re.compile(i, re.I) for i in regex_dict[exp]]
        for mg in mlist:
            m = mg.search(text)
            if m:
                v[exp] = m.groups()[0]
                break
    return v

class CookieContext:
    def __init__(t, config):
        t.type = config['login_cookies_type']
        t.path = config['login_cookies_path']
        if t.type == 'local':
            t.jar = mechanize.LWPCookieJar()
            t.path = os.path.join(os.path.dirname(sys.argv[0]), t.path)
        elif t.type == 'ie':
            t.jar = mechanize.MSIECookieJar(delayload=True)
        elif t.type == 'mozilla':
            t.jar = mechanize.MozillaCookieJar()

    def __enter__(t):
        try:
            if t.type == 'local':
                t.jar.load(t.path)
            elif t.type == 'ie':
                t.jar.load_from_registry()
            elif t.type == 'mozilla':
                t.jar.load(t.path)
        except IOError:
            pass
        return t.jar
    def __exit__(t, exc_type, exc_val, exc_tb):
        if t.type == 'local':
            t.jar.save(t.path, ignore_discard=True, ignore_expires=True)
        else:
            logging.getLogger("upload").warn("Saving cookies not supported on: %s" % t.type)
        


def upload(conf_file, dirs_to_upload, WORK_DIR):
    logger = logging.getLogger("upload")
    logger.info("Uploading with %s: %s" % (conf_file, dirs_to_upload))
    config = ConfigObj(conf_file, unrepr=True, interpolation="Template")

    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_debug_responses(True)
    br.set_debug_redirects(True)

    with CookieContext(config) as cj:
        br.set_cookiejar(cj)

        resp = br.open(config['base_url']).read()
        #~ print resp
        if config['login_check_string'] not in resp:
            # we need to login
            logger.info("Loggin in...")
            resp = br.open(config['login_url']).read()
            for form in br.forms():
                if config['login_action'] in form.action:
                    form[config['username_field']] = config['username_value']
                    form[config['password_field']] = config['password_value']
                    br.form = form
                    logger.warn("Submitting loggin...")
                    logger.info(form)
                    resp = br.submit().read()
                    
                    break
        if config['login_check_string'] in resp:
            logger.info("Login successfull !")
        else:
            logger.error(resp)
            logger.error('`login_check_string` missing from response !')
            raise Exception("Login UNsuccessfull !")
        failed = []
        for dir_to_upload in dirs_to_upload:
            if os.path.exists(dir_to_upload):
                while 1:
                    try:
                        br.form = None
                        base_name = os.path.basename(dir_to_upload)
                        logger = logging.getLogger("upload.%s" % base_name.replace('.','_'))
                        from BitTorrent.makemetafile import make_meta_files
                        target = os.path.join(WORK_DIR, '%s.torrent' % base_name)
                        args = [
                            config['announce_url'], 
                            dir_to_upload
                        ]
                        def dc(v):
                            print v

                        def prog(amount):
                            print '%.1f%% complete\r' % (amount * 100),
                        logger.info('Making: %s' % target)
                        make_meta_files(args[0], args[1:], piece_len_pow2=int(config['piece_size']), progressfunc=prog, filefunc=dc, comment=config.get('torrent_comment', None), target=target, filesystem_encoding='', created_by=__version__)


                        resp = br.open(config['upload_url'])
                        for i in br.forms():
                            if config['upload_action'] in i.action:
                                br.form = i
                                break
                        if not br.form:
                            raise Exception("No upload form matching upload_action found.")
                        
                        br.form.find_control('file').add_file(file(target, 'rb'), 'application/x-bittorrent', os.path.basename(target))
                        nfo = glob.glob(os.path.join(dir_to_upload, '*.nfo'))
                        if nfo:
                            if len(nfo) != 1:
                                logger.warn('Alert ! Multiple nfos: %s' % nfo)
                            nfo= nfo[0]
                            nfo_content = file(nfo).read()
                            br.form['descr'] = nfo_content
                            br.form.find_control('nfo').add_file(file(nfo), 'text/plain', os.path.basename(nfo))
                        else:
                            logger.warn('Alert ! No nfo !')
                            nfo_content = ''
                        br.form['name'] = os.path.splitext(os.path.basename(target))[0]
                        
                        v = match_stuff(
                            config.get('nfo_regex_defaults', {}), 
                            config.get('nfo_regex', {}), 
                            nfo_content
                        )
                        
                        upload_conf = config['upload']
                        
                        for key in upload_conf:
                            val = upload_conf[key]
                            if isinstance(val, list):
                                val = [i % v for i in val if isinstance(i, (str, unicode))]
                            else:
                                val = val % v
                            logger.info('Setting upload param %s: %s' % (key, val))
                            br.form[key] = val
                        logger.info("Uploading .torrent file.")
                        resp = br.submit()
                        prev_resp = resp.read()
                        logger.info("RESPONSE: "+ prev_resp)
                        
                        try:
                            resp = br.follow_link(url_regex=re.compile(config['download_url_regex']))
                            
                        except:
                            html_filter = config.get('html_filter', None)
                            if html_filter:
                                m = re.search(html_filter, prev_resp, re.MULTILINE|re.DOTALL)
                                if m:
                                    prev_resp = m.group() or prev_resp
                            raise
                        new_target = os.path.join(WORK_DIR, os.path.basename(target))
                        file(new_target, 'wb').write(resp.read())
                        command = config['torrent_handler'] % {'dl_dir': dir_to_upload, 'torrent_file':new_target}
                        logger.info('Running command: %s' % command)
                        subprocess.Popen(command)
                        
                                               
                        v = match_stuff(
                            config.get('page_regex_defaults', {}), 
                            config.get('page_regex', {}), 
                            prev_resp
                        )
                        upload_success_browse = config.get('upload_success_browse', None)
                        if upload_success_browse:
                            url = upload_success_browse % v
                            logger.info("Opening: %s" % url)
                            webbrowser.open(url) 
                        upload_success_run = config.get('upload_success_run', None)
                        if upload_success_run:
                            cmd = upload_success_run % v
                            logger.info("Running: %s" % cmd)
                            subprocess.Popen(cmd)
                        
                    except (httplib.HTTPException, urllib2.URLError), e:
                        logger.exception('We have a http error:')
                        logger.warn("RETRYING ...")
                    except:
                        logger.exception("Torrent %s failed" % dir_to_upload)
                        logger.info("FORM: %s" % br.form)
                        failed.append(dir_to_upload)
                        break
                    break
        
        if failed:
            logger = logging.getLogger("upload")
            logger.error("We have %s FAILED torrents: \n  %s" % (len(failed), "\n  ".join(failed)))
            