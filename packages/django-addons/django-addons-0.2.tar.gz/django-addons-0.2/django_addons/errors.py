# -*- coding: utf-8 -*-

class AddonIncompatible(BaseException):
    """
    This should be thrown when addon wants to import
    something from the base Django project but can't find it.

    This usually should indicate that addon has been installed onto
    wrong Django project
    """
    pass

class AddonError(StandardError):
    """
    Base class for all addon errors.
    """
    pass
