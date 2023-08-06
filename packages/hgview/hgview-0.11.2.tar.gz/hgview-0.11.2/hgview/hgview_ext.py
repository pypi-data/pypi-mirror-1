from mercurial import hg, commands, ui
import os, sys
import os.path as pos


def start_hgview(ui, repo, **opts):
    ## try to run hgview
    try:
        import hgview
        from hgview.gtk import hgview_gtk
        hgview_gtk.main()
    except ImportError:
        import stat
        exec_path = pos.abspath(__file__)
        # Resolve symbolic links
        statinfo = os.lstat(exec_path)
        if stat.S_ISLNK(statinfo.st_mode):
            exec_path = pos.abspath(pos.join(pos.dirname(exec_path),
                                             os.readlink(exec_path)))
        py_path = pos.abspath(pos.join(pos.dirname(exec_path), ".."))
        sys.path.append(py_path)
    
    
cmdtable = {
    "hgview": (start_hgview,
                       [],
                       "hg hgview [opts]"),
}

