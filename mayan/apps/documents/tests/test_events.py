# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from actstream.models import Action

from common.tests import skip_file_descriptor_check
from user_management.tests.literals import (
    TEST_USER_PASSWORD, TEST_USER_USERNAME
)

from ..events import event_document_download, event_document_view
from ..permissions import (
    permission_document_download, permission_document_view
)


from .test_views import GenericDocumentViewTestCase


TEST_DOCUMENT_TYPE_EDITED_LABEL = 'test document type edited label'
TEST_DOCUMENT_TYPE_2_LABEL = 'test document type 2 label'
TEST_TRANSFORMATION_NAME = 'rotate'
TEST_TRANSFORMATION_ARGUMENT = 'degrees: 180'


class DocumentEventsTestCase(GenericDocumentViewTestCase):
    def test_document_download_event_no_permissions(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        Action.objects.all().delete()

        response = self.post(
            'documents:document_download', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(list(Action.objects.any(obj=self.document)), [])

    @skip_file_descriptor_check
    def test_document_download_event_with_permissions(self):
        # TODO: Skip this test's file descriptor check until it gets migrate
        # SingleObjectDownloadView CBV
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        Action.objects.all().delete()

        self.role.permissions.add(
            permission_document_download.stored_permission
        )

        self.expected_content_type = 'image/png'

        self.post(
            'documents:document_download', args=(self.document.pk,),
        )

        event = Action.objects.any(obj=self.document).first()

        self.assertEqual(event.verb, event_document_download.name)
        self.assertEqual(event.target, self.document)
        self.assertEqual(event.actor, self.user)

    def test_document_view_event_no_permissions(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        Action.objects.all().delete()

        response = self.get(
            'documents:document_preview', args=(self.document.pk,)
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(list(Action.objects.any(obj=self.document)), [])

    def test_document_view_event_with_permissions(self):
        self.login(
            username=TEST_USER_USERNAME, password=TEST_USER_PASSWORD
        )

        Action.objects.all().delete()

        self.role.permissions.add(
            permission_document_view.stored_permission
        )
        self.get(
            'documents:document_preview', args=(self.document.pk,),
        )

        event = Action.objects.any(obj=self.document).first()

        self.assertEqual(event.verb, event_document_view.name)
        self.assertEqual(event.target, self.document)
        self.assertEqual(event.actor, self.user)
