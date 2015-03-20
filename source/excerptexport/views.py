import os

from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.template import RequestContext, loader

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.utils.encoding import smart_str

from excerptexport.models import Excerpt
from excerptexport.models import OutputFile
from excerptexport.models import BoundingGeometry
from excerptexport import settings


def index(request):
    return HttpResponse(loader.get_template('excerptexport/templates/index.html').render(RequestContext(request, {})))


class NewExcerptExportViewModel:
    def __init__(self, user):
        self.user = user
        self.personal_excerpts = Excerpt.objects.filter(is_active=True, is_public=False, owner=user) #.order_by('name')
        self.public_excerpts = Excerpt.objects.filter(is_active=True, is_public=True) #.order_by('name')

        self.administrative_areas = settings.ADMINISTRATIVE_AREAS
        self.export_options = settings.EXPORT_OPTIONS

    def get_context(self):
        return self.__dict__


@login_required(login_url='/admin/')
def new_excerpt_export(request):
    view_model = NewExcerptExportViewModel(request.user)
    return render(request, 'excerptexport/templates/new_excerpt_export.html', view_model.get_context())


@login_required(login_url='/admin/')
def create_excerpt_export(request):
    viewContext = {}
    if request.POST['form-mode'] == 'existing_excerpt':
        existingExcerptID = request.POST['existing_excerpt.id']
        viewContext = { 'use_existing': True, 'excerpt': existingExcerptID }

    if request.POST['form-mode'] == 'create_new_excerpt':
        excerpt = Excerpt(
            name = request.POST['new_excerpt.name'],
            is_active = True,
            is_public = request.POST['new_excerpt.is_public'] if ('new_excerpt.is_public' in request.POST) else False
        )
        excerpt.owner = request.user
        excerpt.save()

        bounding_geometry = BoundingGeometry.create_from_bounding_box_coordinates(
            request.POST['new_excerpt.boundingBox.north'],
            request.POST['new_excerpt.boundingBox.east'],
            request.POST['new_excerpt.boundingBox.south'],
            request.POST['new_excerpt.boundingBox.west']
        )
        bounding_geometry.excerpt = excerpt
        bounding_geometry.save()

        viewContext = { 'use_existing': False, 'excerpt': excerpt, 'bounding_geometry': bounding_geometry }

    viewContext['options'] = get_export_options(request.POST, settings.EXPORT_OPTIONS)
    return render(request, 'excerptexport/templates/create_excerpt_export.html', viewContext)


@login_required(login_url='/admin/')
def show_downloads(request):
    view_context = {}

    files = OutputFile.objects.filter(extraction_order__orderer=request.user)
    view_context['files'] = files
    return render(request, 'excerptexport/templates/show_downloads.html', view_context)


def download_file(request):

    file_id = int(request.GET['file'])
    output_file = get_object_or_404(OutputFile, pk=file_id)

    directory_path, file_name = os.path.split(output_file.path
    download_file_name = settings.APPLICATION_SETTINGS['download_file_name'] % { 'id': output_file.id, 'name': file_name }
    absolute_file_path = os.path.abspath(settings.APPLICATION_SETTINGS['data_directory'] + '/' + output_file.path)

    # stream file in chunks
    response = StreamingHttpResponse(
        FileWrapper(open(absolute_file_path), settings.APPLICATION_SETTINGS['dowload_chunk_size']),
        content_type=output_file.mime_type
    )
    response['Content-Length'] = os.path.getsize(absolute_file_path)
    response['Content-Disposition'] = 'attachment; filename=%s' % download_file_name
    return response


def get_export_options(requestPostValues, optionConfig):
    # post values naming schema:
    # formats: "export_options.{{ export_option_key }}.formats"
    # options: "'export_options.{{ export_option_key }}.options.{{ export_option_config_key }}"
    export_options = {}
    for export_option_key, export_option in optionConfig.items():
        export_options[export_option_key] = {}
        export_options[export_option_key]['formats'] = requestPostValues.getlist('export_options.'+export_option_key+'.formats')

        for export_option_config_key, export_option_config in export_option['options'].items():
            export_options[export_option_key][export_option_config_key] = requestPostValues.getlist('export_options.'+export_option_key+'.options.'+export_option_config_key)

    return export_options
