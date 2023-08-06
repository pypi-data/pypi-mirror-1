// Amir Salihefendic's RND templater, as at:
//   http://amix.dk/blog/viewEntry/?id=163p

function RND(tmpl, ns, scope) {
    scope = scope || window;
    var fn = function(w, g) {
        g = g.split("|");
        var cnt = ns[g[0]];
        for(var i=1; i < g.length; i++)
            cnt = scope[g[i]](cnt);
        if(cnt == 0 || cnt == -1)
            cnt += '';
        return cnt || w;
    };
    return tmpl.replace(/%\(([A-Za-z0-9_|.]*)\)/g, fn);
}
