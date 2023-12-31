from django.conf.urls import url

from .api_views import APICheckedoutDocumentListView, APICheckedoutDocumentView, APIDocumentCheckoutView
from .views import (
    DocumentCheckInView, DocumentCheckOutDetailView, DocumentCheckOutListView,summery,Ocr,
    DocumentCheckOutView
)

urlpatterns = [
    url(
        regex=r'^documents/$', name='check_out_list',
        view=DocumentCheckOutListView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/check/in/$',
        name='check_in_document', view=DocumentCheckInView.as_view()
    ),
    url(
        regex=r'^documents/multiple/check/in/$',
        name='check_in_document_multiple', view=DocumentCheckInView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/check/out/$',
        name='check_out_document', view=DocumentCheckOutView.as_view()
    ),
    url(
        regex=r'^documents/multiple/check/out/$',
        name='check_out_document_multiple',
        view=DocumentCheckOutView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/checkout/info/$',
        name='check_out_info', view=DocumentCheckOutDetailView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/summery/$',
        name='summery_doc', view=summery.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>\d+)/ocr/$',
        name='ocr', view=Ocr.as_view()
    )
]

api_urls = [
    url(
        regex=r'^checkouts/$', name='checkout-document-list',
        view=APICheckedoutDocumentListView.as_view()
    ),
    url(
        regex=r'^checkouts/(?P<checkout_id>[0-9]+)/checkout_info/$',
        name='checkedout-document-view',
        view=APICheckedoutDocumentView.as_view()
    ),
    url(
        regex=r'^documents/(?P<document_id>[0-9]+)/checkout/$',
        name='document-checkout-view',
        view=APIDocumentCheckoutView.as_view()
    )
]
