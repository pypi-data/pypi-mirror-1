# -*- coding: utf-8 -*-
"""
    pocoo.exceptions
    ~~~~~~~~~~~~~~~~

    Pocoo base exceptions.

    :copyright: 2006 by Georg Brandl, Armin Ronacher.
    :license: GNU GPL, see LICENSE for more details.
"""

class PocooException(Exception):
    """
    Base class for exceptions caused by
     - wrong set-up
     - misconfiguration
     - bad user actions (such as wrong login credentials)
    """


class ConfigurationError(PocooException):
    """
    Base for errors with the configuration file.
    """


class InvalidConfigFile(ConfigurationError):
    """
    If the config file cannot be parsed.
    """
    def __init__(self, fname, lno, msg):
        ConfigurationError.__init__(self)
        self.args = fname, lno, msg

    def __str__(self):
        return "%s in file %s, line %s" % (self.args[2], self.args[0], self.args[1])


class MissingConfigValue(ConfigurationError):
    """
    If a mandatory config value is missing.
    """


class PocooRuntimeError(Exception):
    """
    Base class for exceptions caused by bugs in Pocoo
    and plugins code.
    """


class PackageImportError(PocooException):
    """
    If a package mentioned in the config cannot be imported.
    """


class PackageNotFound(PackageImportError):
    """
    If a package cannot be found.
    """


class MissingResource(PocooException):
    """
    If a resource (template, cobalt file, etc.) cannot be found.
    """


class MissingLanguagePack(MissingResource):
    """
    If a language pack is missing.
    """


class EmailSMTPError(PocooException):
    """
    If the Email SMTP server fails working.
    """


class PasswordIncorrect(PocooException):
    """
    If the user provides a wrong password.
    """
