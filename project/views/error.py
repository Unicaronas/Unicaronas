from django.views import generic


class Handler500(generic.TemplateView):
    template_name = 'project/errors/500.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=500)


class Handler404(generic.TemplateView):
    template_name = 'project/errors/404.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=404)
