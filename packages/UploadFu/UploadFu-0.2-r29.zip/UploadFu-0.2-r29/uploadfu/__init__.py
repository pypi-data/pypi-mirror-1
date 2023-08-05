from __future__ import with_statement

__version__ = "UploadFu/0.2"

import mechanize
import sys
import os
import glob
import subprocess
import re
import traceback
import urllib2
from configobj import ConfigObj

def get_work_dir():
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
            print "Saving cookies not supported on:", t.type
        


def upload(conf_file, dirs_to_upload, WORK_DIR):
    print conf_file, dirs_to_upload
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
            print "Loggin in..."
            resp = br.open(config['login_url']).read()
            for form in br.forms():
                if config['login_action'] in form.action:
                    form[config['username_field']] = config['username_value']
                    form[config['password_field']] = config['password_value']
                    br.form = form
                    print "Submitting loggin..."
                    print form
                    resp = br.submit().read()
                    
                    break
        if config['login_check_string'] in resp:
            print "Login successfull !"
        else:
            print resp
            raise Exception("Login UNsuccessfull !")
        failed = []
        for dir_to_upload in dirs_to_upload:
            if os.path.exists(dir_to_upload):
                while 1:
                    try:
                        br.form = None
                        base_name = os.path.basename(dir_to_upload)
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
                        print 'Making:', target
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
                                print 'Alert ! Multiple nfos:', nfo
                            nfo= nfo[0]
                            br.form['descr'] = file(nfo).read()
                            br.form.find_control('nfo').add_file(file(nfo), 'text/plain', os.path.basename(nfo))
                        else:
                            print 'Alert ! No nfo !'
                        br.form['name'] = os.path.splitext(os.path.basename(target))[0]
                        upload_conf = config['upload']
                        for i in upload_conf:
                            print 'Setting upload param %s: %s' % (i, upload_conf[i])
                            br.form[i] = upload_conf[i]
                        print "Uploading .torrent file."
                        resp = br.submit()
                        resp.read()
                        
                        resp = br.follow_link(url_regex=re.compile(config['download_url_regex']))
                        new_target = os.path.join(WORK_DIR, os.path.basename(target))
                        file(new_target, 'wb').write(resp.read())
                        command = config['torrent_handler'] % {'dl_dir': dir_to_upload, 'torrent_file':new_target}
                        print 'Running command:', command
                        subprocess.Popen(command)
                    except urllib2.URLError, e:
                        print 'We have a urlib error:', e
                        print "RETRYING ..."
                    except:
                        traceback.print_exc()
                        print "FORM: ", br.form
                        failed.append(dir_to_upload)
                        break
                    break
        if failed:
            print "We have %s FAILED torrents:" % len(failed)
            for i in failed:
                print i
