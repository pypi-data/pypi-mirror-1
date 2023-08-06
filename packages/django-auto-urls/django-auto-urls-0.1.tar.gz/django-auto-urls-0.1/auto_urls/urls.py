from django.conf.urls.defaults import *

urlpatterns = patterns('auto_urls.views', 
                        url(
                            regex = r'^(?P<template_name>[\w\.\d]+)$', 
                            view = 'direct_to_disk_template', 
                            name = 'direct_to_disk_template' 
                        ),
                      )
