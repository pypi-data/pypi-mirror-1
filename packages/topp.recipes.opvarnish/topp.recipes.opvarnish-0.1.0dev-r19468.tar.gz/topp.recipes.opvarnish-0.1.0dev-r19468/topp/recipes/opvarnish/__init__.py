# -*- coding: utf-8 -*-
"""Recipe opvarnish"""

import logging
import os
import string
import sys
import zc.buildout

class Recipe:
    not_config = ('recipe', 'backends', 'generate_config',
                  'config', 'bind-host', 'bind-port')
    not_config = dict.fromkeys(not_config)
    
    def __init__(self, buildout, name, options):
        self.name=name
        self.options=options
        self.buildout=buildout
        self.logger=logging.getLogger(self.name)

        self.options["location"] = os.path.join(
                buildout["buildout"]["parts-directory"], self.name)

        # Set some default options
        self.options["bind"]=self.options.get("bind", "127.0.0.1:8000")
        self.options["cache-size"]=self.options.get("cache-size", "1G")
        self.options["daemon"]=self.options.get("daemon", 
                os.path.join(buildout["buildout"]["bin-directory"], "varnishd"))

        if self.options.has_key("config"):
            if self.options.has_key("backends") or \
                    self.options.has_key("zope2_vhm_map"):
                self.logger.error("If you specify the config= option you can "
                                  "not use backends or zope2_vhm_map.")
                raise zc.buildout.UserError("Can not use both config and "
                                           "backends or zope2_vhm_map options.")
            self.options["generate_config"]="false"
        else:
            self.options["generate_config"]="true"
            self.options["backends"]=self.options.get("backends", "127.0.0.1:8080")
            self.options["config"]=os.path.join(self.options["location"],
                        "varnish.vcl")

        # Convenience settings
        (host,port)=self.options["bind"].split(":")
        self.options["bind-host"]=host
        self.options["bind-port"]=port

    def install(self):
        location=self.options["location"]

        if not os.path.exists(location):
            os.mkdir(location)
        self.options.created(location)

        self.addVarnishRunner()
        if self.options["generate_config"]=="true":
            self.createVarnishConfig()

        return self.options.created()


    def update(self):
        pass


    def addVarnishRunner(self):
        options = self.options.copy()
        target=os.path.join(self.buildout["buildout"]["bin-directory"],
                                self.name)
        f=open(target, "wt")
        print >>f, "#!/bin/sh"
        print >>f, "exec %s \\" % options.pop("daemon")
        print >>f, '    -f "%s" \\' % self.options["config"]
        location = options.pop("location")
        print >>f, '    -P "%s" \\' % \
                os.path.join(location, "varnish.pid")
        print >>f, '    -a %s \\' % options.pop("bind")
        if options.get("telnet", None):
            print >>f, '    -T %s \\' % options.pop("telnet")
        print >>f, '    -s file,"%s",%s \\' % (
                os.path.join(location, "storage"),
                options.pop("cache-size"))
        if options.pop("mode", "daemon") == "foreground":
            print >>f, '    -F \\'
        # we've popped all of the options, whatever's left should be
        # considered a "-p" argument
        for key in options:
            if key not in self.not_config:
                print >>f, '    -p %s=%s \\' % (key, options[key])
        print >>f, '    "$@"'
        f.close()
        os.chmod(target, 0755)
        self.options.created(target)


    def createVarnishConfig(self):
        module = ''
        for x in self.options["recipe"]:
            if x in (':', '>', '<', '='):
                break
            module += x
        whereami=sys.modules[module].__path__[0]
        template=open(os.path.join(whereami, "template.vcl")).read()
        template=string.Template(template)
        config={}

        zope2_vhm_map=self.options.get("zope2_vhm_map", "").split()
        zope2_vhm_map=dict([x.split(":") for x in zope2_vhm_map])

        backends=self.options["backends"].strip().split()
        backends=[x.split(":") for x in backends]
        if len(backends)>1:
            lengths=set([len(x) for x in backends])
            if lengths!=set([3]):
                self.logger.error("When using multiple backends a hostname "
                                  "must be given for each client")
                raise zc.buildout.UserError("Multiple backends without hostnames")


        output=""
        vhosting=""
        for i in range(len(backends)):
            parts=backends[i]
            output+='backend backend_%d {\n' % i
            if len(parts)==2:
                output+='    .host = "%s";\n' % parts[0]
                output+='    .port = "%s";\n' % parts[1]
            elif len(parts)==3:
                output+='    .host = "%s";\n' % parts[1]
                output+='    .port = "%s";\n' % parts[2]
                vhosting+=' elsif (req.http.host ~ "^%s(:[0-9]+)?$") {\n' % parts[0]
                vhosting+='    req.backend = backend_%d;\n' % i
                if parts[0] in zope2_vhm_map:
                    location=zope2_vhm_map[parts[0]]
                    if location.startswith("/"):
                        location=location[1:]
                    vhosting+='    set req.url = regsub(req.url, "(.*)", "/VirtualHostBase/http/%s:%s/%s/VirtualHostRoot/$1");\n' % \
                                (parts[0], self.options["bind-port"], location)
                vhosting+='}'
            else:
                self.logger.error("Invalid syntax for backend: %s" % 
                                        ":".join(parts))
                raise zc.buildout.UserError("Invalid syntax for backends")
            output+="}\n\n"


        vhosting=vhosting[4:]
        if len(backends)==0 and len(backends[0])==2:
            vhosting='set req.backend = backend_0;'
        elif len(backends[0])==3:
            vhosting+=' else {\n'
            vhosting+='    error 404 "Unknown virtual host";\n'
            vhosting+='}\n'

        config["backends"]=output
        config["virtual_hosting"]=vhosting

        f=open(self.options["config"], "wt")
        f.write(template.safe_substitute(config))
        f.close()
        self.options.created(self.options["config"])
