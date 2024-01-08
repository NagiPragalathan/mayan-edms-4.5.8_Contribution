import uuid

from django.db import models, transaction
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.common.signals import signal_mayan_pre_save
from mayan.apps.events.decorators import method_event
from mayan.apps.events.event_managers import EventManagerSave

from ..events import (
    event_document_created, event_document_edited,
    event_document_trashed, event_trashed_document_deleted
)
from ..literals import DEFAULT_LANGUAGE
from ..managers import (
    DocumentManager, TrashCanManager, ValidDocumentManager,
    ValidRecentlyCreatedDocumentManager
)
from ..settings import setting_language

from .document_model_mixins import DocumentBusinessLogicMixin
from .document_type_models import DocumentType
from .model_mixins import HooksModelMixin

from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.document import Document as doc
import re
from langchain.text_splitter import TextSplitter

def get_text_chunks_langchain(text):
    print("chunks text : ",text)
    text_splitter = CharacterTextSplitter(chunk_size = 1024, chunk_overlap = 128)
    docs = [doc(page_content=x) for x in text_splitter.split_text(text)]
    return docs

from PIL import Image
import pytesseract
import PyPDF2

__all__ = ('Document', 'DocumentSearchResult',)


from django.db import models

class Summary(models.Model): # table name
    id = models.IntegerField(primary_key=True) # id of the table
    doc_id = models.IntegerField()
    name = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.summary

count=0
class Document(
    DocumentBusinessLogicMixin, ExtraDataModelMixin, HooksModelMixin,
    models.Model
):
    """
    Defines a single document with it's fields and properties
    Fields:
    * uuid - UUID of a document, universally Unique ID. An unique identifier
    generated for each document. No two documents can ever have the same UUID.
    This ID is generated automatically.
    """
    _hooks_pre_create = []

    file_latest = models.OneToOneField(
        blank=True, null=True, on_delete=models.SET_NULL, to='DocumentFile',
        related_name='document_latest', verbose_name=_(
            'Latest document file'
        )
    )
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text=_(
            'UUID of a document, universally Unique ID. An unique '
            'identifier generated for each document.'
        ), verbose_name=_('UUID')
    )
    document_type = models.ForeignKey(
        help_text=_('The document type of the document.'),
        on_delete=models.CASCADE, related_name='documents', to=DocumentType,
        verbose_name=_('Document type')
    )
    label = models.CharField(
        blank=True, db_index=True, default='', max_length=255,
        help_text=_(
            'A short text identifying the document. By default, will be '
            'set to the filename of the first file uploaded to the document.'
        ),
        verbose_name=_('Label')
    )
    description = models.TextField(
        blank=True, default='', help_text=_(
            'An optional short text describing a document.'
        ), verbose_name=_('Description')
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text=_(
            'The date and time of the document creation.'
        ), verbose_name=_('Created')
    )
    language = models.CharField(
        blank=True, default=DEFAULT_LANGUAGE, help_text=_(
            'The primary language in the document.'
        ), max_length=8, verbose_name=_('Language')
    )
    in_trash = models.BooleanField(
        db_index=True, default=False, help_text=_(
            'Whether or not this document is in the trash.'
        ), editable=False, verbose_name=_('In trash?')
    )
    trashed_date_time = models.DateTimeField(
        blank=True, editable=True, help_text=_(
            'The server date and time when the document was moved to the '
            'trash.'
        ), null=True, verbose_name=_('Date and time trashed')
    )
    is_stub = models.BooleanField(
        db_index=True, default=True, editable=False, help_text=_(
            'A document stub is a document with an entry on the database '
            'but no file uploaded. This could be an interrupted upload or '
            'a deferred upload via the API.'
        ), verbose_name=_('Is stub?')
    )
    version_active = models.OneToOneField(
        blank=True, null=True, on_delete=models.SET_NULL,
        to='DocumentVersion', related_name='document_active', verbose_name=_(
            'Active document version'
        )
    )

    objects = DocumentManager()
    trash = TrashCanManager()
    valid = ValidDocumentManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        
    def summary(self, text):
        if text:
            prompt_template = """Write a concise summary of the following:
            "{text}"
            CONCISE SUMMARY:"""
            prompt = PromptTemplate.from_template(prompt_template)
            print("inner text:", text)
            # Define LLM chain
            llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-1106", api_key='')
            llm_chain = LLMChain(llm=llm, prompt=prompt)

            # Define StuffDocumentsChain
            stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")

            # docs = loader.load()
            return { 'summary': stuff_chain.run(get_text_chunks_langchain(text)) }
        else:
            return False

        
    def read_and_print_document_content(self):
        content = False
        if self.file_latest:
            document_file = self.file_latest
            print(self.language)
            print(document_file)
            try:
                # Check if the file is an image (assuming JPEG for simplicity)
                if str(document_file).lower().endswith(('.jpg', '.jpeg','.png')):
                    # Open the image file
                    with Image.open(document_file.file) as img:
                        # Use Tesseract to extract text from the image
                        text = pytesseract.image_to_string(img, lang=self.language, config='--psm 6')
                        # Print the extracted text
                        content=text
                elif str(document_file).lower().endswith('.pdf'):
                    # Open the PDF file using PyPDF2
                    temp_content = ""
                    with document_file.file.open('rb') as file_handle:
                        pdf_reader = PyPDF2.PdfReader(file_handle)

                        # Iterate through all pages of the PDF
                        for page_number in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_number]
                            # Extract text from the PDF page
                            text = page.extract_text()
                            temp_content = temp_content + text +"\n\n"
                    content = temp_content
                else:
                    # Open the file and read its content for non-image files
                    with document_file.file.open('r') as file_handle:
                        text = file_handle.read()
                    content = text  

            except Exception as e:
                print(f"Error reading document content: {e}")
        else:
            print("No document file attached to this document.")
        return content
            
    def __str__(self):
        return self.get_label()

    def delete(self, *args, **kwargs):
        to_trash = kwargs.pop('to_trash', True)
        user = self.__dict__.pop('_event_actor', None)
        print("document deleted..!")

        if not self.in_trash and to_trash:
            self.in_trash = True
            self.trashed_date_time = now()
            print(self.id,self.label)
            with transaction.atomic():
                self._event_ignore = True
                self.save(
                    update_fields=('in_trash', 'trashed_date_time')
                )

            event_document_trashed.commit(actor=user, target=self)
        else:
            with transaction.atomic():
                for document_file in self.files.all():
                    try:
                        del_obj = Summary.objects.get(doc_id=document_file.id)
                        del_obj.delete()
                    except Summary.DoesNotExist:
                        # Handle the case where the Summary object does not exist
                        print(f"Summary for doc_id {document_file.id} does not exist.")
                    document_file.delete()
                obj = Summary.objects.all()
                for i in obj:
                    print("in delete : ",i.id,(i.name),i.doc_id)

                super().delete(*args, **kwargs)

            event_trashed_document_deleted.commit(
                actor=user, target=self.document_type
            )

    def get_absolute_url(self):
        return reverse(
            viewname='documents:document_preview', kwargs={
                'document_id': self.pk
            }
        )

    def natural_key(self):
        return (self.uuid,)
    natural_key.dependencies = ['documents.DocumentType']

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_document_created,
            'action_object': 'document_type',
            'target': 'self'
        },
        edited={
            'event': event_document_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        user = self.__dict__.pop('_event_actor', None)
        new_document = not self.pk
        self.id = self.id
        self.description = self.description or ''
        self.label = self.label or ''
        self.language = self.language or setting_language.value
        print(self.id,self.description,self.label)

        signal_mayan_pre_save.send(
            instance=self, sender=Document, user=user
        )
        print("doc_saved..!")
        content = self.read_and_print_document_content()
        # print(content)
        # try:
        global count
        summery_content = self.summary(content)
        print(count%2 ==0 and not self.in_trash,count%2 , self.in_trash)
        if count%2 ==0 and not self.in_trash and self.id is not None and content != False:
            print("self.id;",self.id)
            new_summary = Summary(
                doc_id=self.id,
                name=self.label,
                content=content,
                summary=summery_content['summary'],
            )
            new_summary.save()
            print(summery_content['summary'])
        else:
            pass
        count = count + 1
        print("count : ", count)
        # except:
        #     print("doc can't find...!")

        obj = Summary.objects.all()
        # obj.delete()
        for i in obj:
            print(i.id,i.doc_id,(i.name))
        print("data stored..!", self.uuid, self.id)

        super().save(*args, **kwargs)

        if new_document:
            if user:
                self.add_as_recent_document_for_user(user=user)


class DocumentSearchResult(Document):
    class Meta:
        proxy = True


class RecentlyCreatedDocument(Document):
    objects = models.Manager()
    valid = ValidRecentlyCreatedDocumentManager()

    class Meta:
        proxy = True
