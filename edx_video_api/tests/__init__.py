"""Test suite init"""
import warnings
from django.utils.deprecation import RemovedInDjango20Warning
# Suppress DeprecationWarnings from certain external libraries
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r".*(isort|pylint|configparser).*"
)
# Suppress RemovedInDjango20Warning from the edxval library
warnings.filterwarnings(
    action='ignore',
    category=RemovedInDjango20Warning,
    module=r'.*edxval.*'
)
