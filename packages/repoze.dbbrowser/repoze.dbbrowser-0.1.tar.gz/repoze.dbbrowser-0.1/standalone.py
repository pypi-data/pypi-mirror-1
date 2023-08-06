if __name__=='__main__':
    import sys
    from paste.httpserver import serve
    from repoze.dbbrowser.dbbrowser import make_dbbrowser_app
    db_string = 'sqlite:///demo.db'
    if len(sys.argv)>1:
        db_string = sys.argv[1]
    app = make_dbbrowser_app({},
                             db_string=db_string,
                             theme_switcher=True)
    serve(app, host="0.0.0.0")

