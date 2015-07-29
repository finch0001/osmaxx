import abc
import stored_messages

from celery import shared_task

from django.contrib import messages
from django.core.mail import send_mail
from django_enumfield import enum
from django.utils.translation import ugettext_lazy as _


class ExcerptConverterState(enum.Enum):
    QUEUED = 0
    RUNNING = 1
    FINISHED = 2
    ABORTED = 3


class BaseExcerptConverter(metaclass=abc.ABCMeta):
    available_converters = []
    name = 'base'
    export_formats = {}
    export_options = {}
    steps_total = 0

    @classmethod
    def converter_configuration(cls):
        return {
            'name': cls.name,
            'formats': cls.export_formats,
            'options': cls.export_options
        }

    @staticmethod
    @abc.abstractmethod
    @shared_task
    def execute_task(extraction_order_id, supported_export_formats, execution_configuration):
        return None

    @staticmethod
    def inform_user(user, message_type, message_text, email=True):
        stored_messages.api.add_message_for(
            users=[user],
            level=message_type,
            message_text=message_text
        )

        if email:
            if hasattr(user, 'email'):
                send_mail(
                    '[OSMAXX] '+message_text,
                    message_text,
                    'no-reply@osmaxx.hsr.ch',
                    [user.email]
                )
            else:
                stored_messages.api.add_message_for(
                    users=[user],
                    level=messages.WARNING,
                    message_text=_("There is no email address assigned to your account. "
                                   "You won't be notified by email on process finish!")
                )

    @classmethod
    def execute(cls, extraction_order, execution_configuration, run_as_celery_tasks):
        """
        Execute excerpt conversion task

        :param execution_configuration example:
            {
                'formats': ['txt', 'file_gdb'],
                'options': {
                    'coordinate_reference_system': 'wgs72',
                    'detail_level': 'verbatim'
                }
            }

        :param export_formats example:
            {
                'txt': {
                    'name': 'Text',
                    'file_extension': 'txt',
                    'mime_type': 'text/plain'
                },
                'markdown': {
                    'name': 'Markdown',
                    'file_extension': 'md',
                    'mime_type': 'text/markdown'
                }
            }
        """
        # queue celery task
        # run_as_celery_tasks=False allows to run as normal functions for testing
        if run_as_celery_tasks:
            cls.execute_task.delay(extraction_order.id, cls.export_formats, execution_configuration)
        else:
            cls.execute_task(extraction_order.id, cls.export_formats, execution_configuration)
