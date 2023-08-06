# This is a basic VCL configuration file for varnish.  See the vcl(7)
# man page for details on VCL syntax and semantics.
#
# Default backend definition.  Set this to point to your content server.

${backends}

acl purge {
    "localhost";
}

sub vcl_recv {
${virtual_hosting}

    if (req.request != "GET" && req.request != "HEAD") {
        # PURGE request if zope asks nicely
        if (req.request == "PURGE") {
            if (!client.ip ~ purge) {
                error 405 "Not allowed.";
            }
            lookup;
        }
	pipe;
    }

    if (req.http.Expect) {
        pipe;
    }

    /* Always cache images */
    if (req.url ~ "\.(jpg|jpeg|gif|png|tiff|tif|svg|swf|ico|css|js|vsd|doc|ppt|pps|xls|pdf|mp3|mp4|m4a|ogg|mov|avi|wmv|sxw|zip|gz|bz2|tgz|tar|rar|odc|odb|odf|odg|odi|odp|ods|odt|sxc|sxd|sxi|sxw|dmg|torrent|deb|msi|iso|rpm)$") {
        lookup;
    }
    /* Always cache CSS and javascript */
    if (req.url ~ "\.(css|js)$") {
        lookup;
    }

    /* Do not cache other authorized content */
    if (req.http.Authenticate || req.http.Authorization) {
        pass;
    }
    
    /* We only care about the "__ac.*" cookies, used for authentication */
    if (req.http.Cookie && (req.http.Cookie ~ "__ac(_(name|password|persistent))?=" || req.http.Cookie ~ "_ZopeId")) {
        pass;
    }

    lookup;
}

/* Deal with purge requests */
sub vcl_hit {
    if (req.request == "PURGE") {
            set obj.ttl = 0s;
            error 200 "Purged";
    }
}

sub vcl_miss {
    if (req.http.If-Modified-Since) {
        pass;
    }

    if (req.request == "PURGE") {
            error 404 "Not in cache";
    }
}

sub vcl_fetch {
    if (!obj.valid) {
        error;
    }
    if (!obj.cacheable) {
        pass;
    }
    if (obj.http.Set-Cookie) {
        pass;
    }

    if (req.url ~ "(rss_|search_rss)") {
        set obj.ttl = 1800s;
    }
}

sub vcl_hash {
    set req.hash += req.http.Accept-Encoding;
}
