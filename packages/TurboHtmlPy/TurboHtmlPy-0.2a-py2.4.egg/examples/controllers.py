class Root(controllers.Root):
    @turbogears.expose(template = 'htmlpy:project.templates.index')
    def index(self):
        return dict(
            title = 'My Page',
            content = 'home.htmlpy',
            menu = ['home', 'about'],
            render_text = self.render_text
        )

    def render_text(self, context, data):
        return context.tag(style = 'color: red') [ 'This text is dynamic' ]
