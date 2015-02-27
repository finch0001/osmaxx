from django.contrib import admin
from excerptExport.models import BoundingGeometry, Excerpt, ExtractionOrder, OutputFile


admin.site.register(BoundingGeometry)
admin.site.register(Excerpt)
admin.site.register(ExtractionOrder)
admin.site.register(OutputFile)