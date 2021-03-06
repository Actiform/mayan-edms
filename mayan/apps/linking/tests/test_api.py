from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import override_settings

from rest_framework.test import APITestCase

from documents.models import DocumentType
from documents.tests.literals import (
    TEST_DOCUMENT_TYPE, TEST_SMALL_DOCUMENT_PATH
)
from user_management.tests.literals import (
    TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
)

from ..models import SmartLink, SmartLinkCondition

from .literals import (
    TEST_SMART_LINK_CONDITION_FOREIGN_DOCUMENT_DATA,
    TEST_SMART_LINK_CONDITION_EXPRESSION,
    TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED,
    TEST_SMART_LINK_CONDITION_OPERATOR, TEST_SMART_LINK_DYNAMIC_LABEL,
    TEST_SMART_LINK_LABEL_EDITED, TEST_SMART_LINK_LABEL
)


@override_settings(OCR_AUTO_OCR=False)
class SmartLinkAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

    def tearDown(self):
        if hasattr(self, 'document_type'):
            self.document_type.delete()

    def _create_document_type(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE
        )

    def _create_document(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def _create_smart_link(self):
        return SmartLink.objects.create(
            label=TEST_SMART_LINK_LABEL,
            dynamic_label=TEST_SMART_LINK_DYNAMIC_LABEL
        )

    def test_smart_link_create_view(self):
        response = self.client.post(
            reverse('rest_api:smartlink-list'), {
                'label': TEST_SMART_LINK_LABEL
            }
        )

        smart_link = SmartLink.objects.first()
        self.assertEqual(response.data['id'], smart_link.pk)
        self.assertEqual(response.data['label'], TEST_SMART_LINK_LABEL)

        self.assertEqual(SmartLink.objects.count(), 1)
        self.assertEqual(smart_link.label, TEST_SMART_LINK_LABEL)

    def test_smart_link_delete_view(self):
        smart_link = self._create_smart_link()

        self.client.delete(
            reverse('rest_api:smartlink-detail', args=(smart_link.pk,))
        )

        self.assertEqual(SmartLink.objects.count(), 0)

    def test_smart_link_detail_view(self):
        smart_link = self._create_smart_link()

        response = self.client.get(
            reverse('rest_api:smartlink-detail', args=(smart_link.pk,))
        )

        self.assertEqual(
            response.data['label'], TEST_SMART_LINK_LABEL
        )

    def test_smart_link_patch_view(self):
        smart_link = self._create_smart_link()

        self.client.patch(
            reverse('rest_api:smartlink-detail', args=(smart_link.pk,)),
            data={
                'label': TEST_SMART_LINK_LABEL_EDITED,
            }
        )

        smart_link.refresh_from_db()

        self.assertEqual(smart_link.label, TEST_SMART_LINK_LABEL_EDITED)

    def test_smart_link_put_view(self):
        smart_link = self._create_smart_link()

        self.client.put(
            reverse('rest_api:smartlink-detail', args=(smart_link.pk,)),
            data={
                'label': TEST_SMART_LINK_LABEL_EDITED,
            }
        )

        smart_link.refresh_from_db()

        self.assertEqual(smart_link.label, TEST_SMART_LINK_LABEL_EDITED)


@override_settings(OCR_AUTO_OCR=False)
class SmartLinkConditionAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username=TEST_ADMIN_USERNAME, email=TEST_ADMIN_EMAIL,
            password=TEST_ADMIN_PASSWORD
        )

        self.client.login(
            username=TEST_ADMIN_USERNAME, password=TEST_ADMIN_PASSWORD
        )

    def tearDown(self):
        if hasattr(self, 'document_type'):
            self.document_type.delete()

    def _create_document_type(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE
        )

    def _create_document(self):
        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def _create_smart_link(self):
        self.smart_link = SmartLink.objects.create(
            label=TEST_SMART_LINK_LABEL,
            dynamic_label=TEST_SMART_LINK_DYNAMIC_LABEL
        )
        self.smart_link.document_types.add(self.document_type)

    def _create_smart_link_condition(self):
        self.smart_link_condition = SmartLinkCondition.objects.create(
            smart_link=self.smart_link,
            foreign_document_data=TEST_SMART_LINK_CONDITION_FOREIGN_DOCUMENT_DATA,
            expression=TEST_SMART_LINK_CONDITION_EXPRESSION,
            operator=TEST_SMART_LINK_CONDITION_OPERATOR
        )

    def test_resolved_smart_link_detail_view(self):
        self._create_document_type()
        self._create_smart_link()
        self._create_smart_link_condition()
        self._create_document()

        response = self.client.get(
            reverse(
                'rest_api:resolvedsmartlink-detail',
                args=(self.document.pk, self.smart_link.pk)
            )
        )

        self.assertEqual(
            response.data['label'], TEST_SMART_LINK_LABEL
        )

    def test_resolved_smart_link_list_view(self):
        self._create_document_type()
        self._create_smart_link()
        self._create_smart_link_condition()
        self._create_document()

        response = self.client.get(
            reverse(
                'rest_api:resolvedsmartlink-list', args=(self.document.pk,)
            )
        )

        self.assertEqual(
            response.data['results'][0]['label'], TEST_SMART_LINK_LABEL
        )

    def test_resolved_smart_link_document_list_view(self):
        self._create_document_type()
        self._create_smart_link()
        self._create_smart_link_condition()
        self._create_document()

        response = self.client.get(
            reverse(
                'rest_api:resolvedsmartlinkdocument-list',
                args=(self.document.pk, self.smart_link.pk)
            )
        )

        self.assertEqual(
            response.data['results'][0]['label'], self.document.label
        )

    def test_smart_link_condition_create_view(self):
        self._create_document_type()
        self._create_smart_link()

        response = self.client.post(
            reverse(
                'rest_api:smartlinkcondition-list', args=(self.smart_link.pk,)
            ), {
                'foreign_document_data': TEST_SMART_LINK_CONDITION_FOREIGN_DOCUMENT_DATA,
                'expression': TEST_SMART_LINK_CONDITION_EXPRESSION,
                'operator': TEST_SMART_LINK_CONDITION_OPERATOR
            }
        )

        smart_link_condition = SmartLinkCondition.objects.first()
        self.assertEqual(response.data['id'], smart_link_condition.pk)
        self.assertEqual(
            response.data['operator'], TEST_SMART_LINK_CONDITION_OPERATOR
        )

        self.assertEqual(SmartLinkCondition.objects.count(), 1)
        self.assertEqual(
            smart_link_condition.operator, TEST_SMART_LINK_CONDITION_OPERATOR
        )

    def test_smart_link_condition_delete_view(self):
        self._create_document_type()
        self._create_smart_link()
        self._create_smart_link_condition()

        self.client.delete(
            reverse(
                'rest_api:smartlinkcondition-detail',
                args=(self.smart_link.pk, self.smart_link_condition.pk)
            )
        )

        self.assertEqual(SmartLinkCondition.objects.count(), 0)

    def test_smart_link_condition_detail_view(self):
        self._create_document_type()
        self._create_smart_link()
        self._create_smart_link_condition()

        response = self.client.get(
            reverse(
                'rest_api:smartlinkcondition-detail',
                args=(self.smart_link.pk, self.smart_link_condition.pk)
            )
        )

        self.assertEqual(
            response.data['operator'], TEST_SMART_LINK_CONDITION_OPERATOR
        )

    def test_smart_link_condition_patch_view(self):
        self._create_document_type()
        self._create_smart_link()
        self._create_smart_link_condition()

        self.client.patch(
            reverse(
                'rest_api:smartlinkcondition-detail',
                args=(self.smart_link.pk, self.smart_link_condition.pk)
            ),
            data={
                'expression': TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED,
            }
        )

        self.smart_link_condition.refresh_from_db()

        self.assertEqual(
            self.smart_link_condition.expression,
            TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED
        )

    def test_smart_link_condition_put_view(self):
        self._create_document_type()
        self._create_smart_link()
        self._create_smart_link_condition()

        self.client.put(
            reverse(
                'rest_api:smartlinkcondition-detail',
                args=(self.smart_link.pk, self.smart_link_condition.pk)
            ),
            data={
                'expression': TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED,
                'foreign_document_data': TEST_SMART_LINK_CONDITION_FOREIGN_DOCUMENT_DATA,
                'operator': TEST_SMART_LINK_CONDITION_OPERATOR,
            }
        )

        self.smart_link_condition.refresh_from_db()

        self.assertEqual(
            self.smart_link_condition.expression,
            TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED
        )
