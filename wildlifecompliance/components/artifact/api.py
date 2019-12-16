import json
import re
import operator
import traceback
import os
import base64
import geojson
from django.db.models import Q, Min, Max
from django.db import transaction
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.conf import settings
from wildlifecompliance import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views, filters
import rest_framework.exceptions as rest_exceptions
from rest_framework.decorators import (
    detail_route,
    list_route,
    renderer_classes,
    parser_classes,
    api_view
)
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from django.core.cache import cache
from ledger.accounts.models import EmailUser, Address
from ledger.address.models import Country
from ledger.checkout.utils import calculate_excl_gst
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from wildlifecompliance.components.main.api import save_location
from wildlifecompliance.components.main.models import TemporaryDocumentCollection
from wildlifecompliance.components.main.process_document import (
        process_generic_document, 
        save_comms_log_document_obj
        )
from wildlifecompliance.components.main.email import prepare_mail
from wildlifecompliance.components.users.serializers import (
    UserAddressSerializer,
    ComplianceUserDetailsSerializer,
)
from wildlifecompliance.helpers import is_customer, is_internal
from wildlifecompliance.components.artifact.models import (
        Artifact,
        DocumentArtifact,
        PhysicalArtifact,
        DocumentArtifactType,
        PhysicalArtifactType,
        PhysicalArtifactDisposalMethod,
        ArtifactUserAction,
        )
from wildlifecompliance.components.artifact.serializers import (
        ArtifactSerializer,
        DocumentArtifactSerializer,
        SaveDocumentArtifactSerializer,
        PhysicalArtifactSerializer,
        DocumentArtifactTypeSerializer,
        PhysicalArtifactTypeSerializer,
        PhysicalArtifactDisposalMethodSerializer,
        ArtifactUserActionSerializer,
        ArtifactCommsLogEntrySerializer,
        )
from wildlifecompliance.components.users.models import (
    CompliancePermissionGroup,    
)
from django.contrib.auth.models import Permission, ContentType
#from utils import SchemaParser

from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from rest_framework_datatables.filters import DatatablesFilterBackend
from rest_framework_datatables.renderers import DatatablesRenderer

from wildlifecompliance.components.legal_case.email import (
    send_mail)
from reversion.models import Version
#import unicodedata


#class LegalCaseFilterBackend(DatatablesFilterBackend):
#
#    def filter_queryset(self, request, queryset, view):
#        #import ipdb; ipdb.set_trace()
#        # Get built-in DRF datatables queryset first to join with search text, then apply additional filters
#        # super_queryset = super(CallEmailFilterBackend, self).filter_queryset(request, queryset, view).distinct()
#
#        total_count = queryset.count()
#        status_filter = request.GET.get('status_description')
#        date_from = request.GET.get('date_from')
#        date_to = request.GET.get('date_to')
#        search_text = request.GET.get('search[value]')
#
#        if search_text:
#            search_text = search_text.lower()
#            search_text_legal_case_ids = []
#            for legal_case in queryset:
#                #lodged_on_str = time.strftime('%d/%m/%Y', call_email.lodged_on)
#                case_created_date_str = legal_case.case_created_date.strftime('%d/%m/%Y') if legal_case.case_created_date else ''
#                if (search_text in (legal_case.number.lower() if legal_case.number else '')
#                    or search_text in (legal_case.status.lower() if legal_case.status else '')
#                    or search_text in (case_created_date_str.lower() if case_created_date_str else '')
#                    or search_text in (legal_case.title.lower() if legal_case.title else '')
#                    or search_text in (
#                        legal_case.assigned_to.first_name.lower() + ' ' + legal_case.assigned_to.last_name.lower()
#                        if legal_case.assigned_to else ''
#                        )
#                    ):
#                    search_text_legal_case_ids.append(legal_case.id)
#
#            # use pipe to join both custom and built-in DRF datatables querysets (returned by super call above)
#            # (otherwise they will filter on top of each other)
#            #_queryset = queryset.filter(id__in=search_text_callemail_ids).distinct() | super_queryset
#            # BB 20190704 - is super_queryset necessary?
#            queryset = queryset.filter(id__in=search_text_legal_case_ids)
#
#        status_filter = status_filter.lower() if status_filter else 'all'
#        if status_filter != 'all':
#            status_filter_legal_case_ids = []
#            for legal_case in queryset:
#                if status_filter == legal_case.get_status_display().lower():
#                    status_filter_legal_case_ids.append(legal_case.id)
#            queryset = queryset.filter(id__in=status_filter_legal_case_ids)
#
#        if date_from:
#            queryset = queryset.filter(case_created_date__gte=date_from)
#        if date_to:
#            date_to = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
#            queryset = queryset.filter(case_created_date__lte=date_to)
#
#        # override queryset ordering, required because the ordering is usually handled
#        # in the super call, but is then clobbered by the custom queryset joining above
#        # also needed to disable ordering for all fields for which data is not an
#        # CallEmail model field, as property functions will not work with order_by
#        
#        getter = request.query_params.get
#        fields = self.get_fields(getter)
#        ordering = self.get_ordering(getter, fields)
#        if len(ordering):
#            for num, item in enumerate(ordering):
#                #if item == 'planned_for':
#                #    # ordering.pop(num)
#                #    # ordering.insert(num, 'planned_for_date')
#                #    ordering[num] = 'planned_for_date'
#                #elif item == '-planned_for':
#                #    # ordering.pop(num)
#                #    # ordering.insert(num, '-planned_for_date')
#                #    ordering[num] = '-planned_for_date'
#                if item == 'status__name':
#                    # ordering.pop(num)
#                    # ordering.insert(num, 'status')
#                    ordering[num] = 'status'
#                elif item == '-status__name':
#                    # ordering.pop(num)
#                    # ordering.insert(num, '-status')
#                    ordering[num] = '-status'
#
#            queryset = queryset.order_by(*ordering)
#
#        setattr(view, '_datatables_total_count', total_count)
#        return queryset
#
#
#class LegalCaseRenderer(DatatablesRenderer):
#    def render(self, data, accepted_media_type=None, renderer_context=None):
#        if 'view' in renderer_context and hasattr(renderer_context['view'], '_datatables_total_count'):
#            data['recordsTotal'] = renderer_context['view']._datatables_total_count
#        return super(LegalCaseRenderer, self).render(data, accepted_media_type, renderer_context)
#
#
#class LegalCasePaginatedViewSet(viewsets.ModelViewSet):
#    filter_backends = (LegalCaseFilterBackend,)
#    pagination_class = DatatablesPageNumberPagination
#    renderer_classes = (LegalCaseRenderer,)
#    queryset = LegalCase.objects.none()
#    serializer_class = LegalCaseDatatableSerializer
#    page_size = 10
#    
#    def get_queryset(self):
#        # import ipdb; ipdb.set_trace()
#        user = self.request.user
#        if is_internal(self.request):
#            return LegalCase.objects.all()
#        return LegalCase.objects.none()
#
#    @list_route(methods=['GET', ])
#    def get_paginated_datatable(self, request, *args, **kwargs):
#        print(request.GET)
#        queryset = self.get_queryset()
#
#        queryset = self.filter_queryset(queryset)
#        self.paginator.page_size = queryset.count()
#        result_page = self.paginator.paginate_queryset(queryset, request)
#        serializer = LegalCaseDatatableSerializer(
#            result_page, many=True, context={'request': request})
#        return self.paginator.get_paginated_response(serializer.data)


class DocumentArtifactViewSet(viewsets.ModelViewSet):
    queryset = DocumentArtifact.objects.all()
    serializer_class = DocumentArtifactSerializer

    def get_queryset(self):
        # import ipdb; ipdb.set_trace()
        user = self.request.user
        if is_internal(self.request):
            return DocumentArtifact.objects.all()
        return DocumentArtifact.objects.none()

    @renderer_classes((JSONRenderer,))
    #def inspection_save(self, request, workflow=False, *args, **kwargs):
    def update(self, request, workflow=False, *args, **kwargs):
        print(request.data)
        try:
            with transaction.atomic():
                instance = self.get_object()
                #if request.data.get('renderer_data'):
                 #   self.form_data(request)

                serializer = SaveDocumentArtifactSerializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()
                    instance.log_user_action(
                            ArtifactUserAction.ACTION_SAVE_ARTIFACT.format(
                            instance.number), request)
                    headers = self.get_success_headers(serializer.data)
                    return_serializer = DocumentArtifactSerializer(instance, context={'request': request})
                    return Response(
                            return_serializer.data,
                            status=status.HTTP_201_CREATED,
                            headers=headers
                            )
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class PhysicalArtifactViewSet(viewsets.ModelViewSet):
    queryset = PhysicalArtifact.objects.all()
    serializer_class = PhysicalArtifactSerializer

    def get_queryset(self):
        # import ipdb; ipdb.set_trace()
        user = self.request.user
        if is_internal(self.request):
            return PhysicalArtifact.objects.all()
        return PhysicalArtifact.objects.none()


class ArtifactViewSet(viewsets.ModelViewSet):
    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer

    def get_queryset(self):
        # import ipdb; ipdb.set_trace()
        user = self.request.user
        if is_internal(self.request):
            return Artifact.objects.all()
        return Artifact.objects.none()

    @detail_route(methods=['GET', ])
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ArtifactUserActionSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['GET', ])
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ArtifactCommsLogEntrySerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(methods=['POST', ])
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, instance=None, workflow=False, *args, **kwargs):
        try:
            with transaction.atomic():
                # create Inspection instance if not passed to this method
                if not instance:
                    instance = self.get_object()
                # add Inspection attribute to request_data
                request_data = request.data.copy()
                request_data['artifact'] = u'{}'.format(instance.id)
                if request_data.get('comms_log_id'):
                    comms = ArtifactCommsLogEntry.objects.get(
                        id=request_data.get('comms_log_id')
                        )
                    serializer = ArtifactCommsLogEntrySerializer(
                        instance=comms, 
                        data=request.data)
                else:
                    serializer = ArtifactCommsLogEntrySerializer(
                        data=request_data
                        )
                serializer.is_valid(raise_exception=True)
                # overwrite comms with updated instance
                comms = serializer.save()
                
                if workflow:
                    return comms
                else:
                    return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


#class LegalCasePriorityViewSet(viewsets.ModelViewSet):
#   queryset = LegalCasePriority.objects.all()
#   serializer_class = LegalCasePrioritySerializer
#
#   def get_queryset(self):
#       # user = self.request.user
#       if is_internal(self.request):
#           return LegalCasePriority.objects.all()
#       return LegalCasePriority.objects.none()

   #@detail_route(methods=['GET',])
   #@renderer_classes((JSONRenderer,))
   #def get_schema(self, request, *args, **kwargs):
   #    instance = self.get_object()
   #    try:
   #        serializer = InspectionTypeSchemaSerializer(instance)
   #        return Response(
   #            serializer.data,
   #            status=status.HTTP_201_CREATED,
   #            )
   #    except serializers.ValidationError:
   #        print(traceback.print_exc())
   #        raise
   #    except ValidationError as e:
   #        print(traceback.print_exc())
   #        raise serializers.ValidationError(repr(e.error_dict))
   #    except Exception as e:
   #        print(traceback.print_exc())
   #        raise serializers.ValidationError(str(e))

class DocumentArtifactTypeViewSet(viewsets.ModelViewSet):
   queryset = DocumentArtifactType.objects.all()
   serializer_class = DocumentArtifactTypeSerializer

   def get_queryset(self):
       # user = self.request.user
       if is_internal(self.request):
           return DocumentArtifactType.objects.all()
       return DocumentArtifactType.objects.none()

   #@detail_route(methods=['GET',])
   #@renderer_classes((JSONRenderer,))
   #def get_schema(self, request, *args, **kwargs):
   #    instance = self.get_object()
   #    try:
   #        serializer = InspectionTypeSchemaSerializer(instance)
   #        return Response(
   #            serializer.data,
   #            status=status.HTTP_201_CREATED,
   #            )
   #    except serializers.ValidationError:
   #        print(traceback.print_exc())
   #        raise
   #    except ValidationError as e:
   #        print(traceback.print_exc())
   #        raise serializers.ValidationError(repr(e.error_dict))
   #    except Exception as e:
   #        print(traceback.print_exc())
   #        raise serializers.ValidationError(str(e))

class PhysicalArtifactTypeViewSet(viewsets.ModelViewSet):
   queryset = PhysicalArtifactType.objects.all()
   serializer_class = PhysicalArtifactTypeSerializer

   def get_queryset(self):
       # user = self.request.user
       if is_internal(self.request):
           return PhysicalArtifactType.objects.all()
       return PhysicalArtifactType.objects.none()

