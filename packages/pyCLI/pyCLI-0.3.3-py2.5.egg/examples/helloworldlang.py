def helloworldlang(app, *args, **kwargs):
    """[-l language]

    Print 'hello world' in the requested language.
    """
    msg = 'hello world'
    if kwargs['language'] == 'esperanto':
        msg = 'Saluton mondo'

    print('%s!' % msg)

if __name__ == '__main__':
    from cli import App
    app = App(helloworldlang)
    app.add_option("language",
        default='english',
        help="print message in Esperanto",
        action="store")
    app.run()

