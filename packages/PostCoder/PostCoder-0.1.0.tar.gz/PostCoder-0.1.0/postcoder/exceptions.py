# __init__.py
# Copyright (C) 2010 Sharoon Thomas sharoon.thomas@openlabs.co.in
#
# This module is part of postvoder module by Openlabs
# the MIT License: http://www.opensource.org/licenses/mit-license.php

"""PostCoder Exception"""

class PostCoderException(Exception):
    """General Class for all exceptions"""
    pass


class IPAddressException(PostCoderException):
    """The Server IP Address is not registered"""
    def __init__(self, message):
        """The IP Address of the requesting server is not registered \
        for use of the Service under your account. Call us on 01508 494488 \
        or email support@postcoder.com to ask for this IP Address to be \
        added to your account."""
        message += __doc__
        PostCoderException.__init__(self, message)
        
        
class CredentialsException(PostCoderException):
    """Invalid Username and/or Password"""
    def __init__(self, message):
        """The username password combination you have used is not valid. \
        Please check them and try again."""
        message += __doc__
        PostCoderException.__init__(self, message)
        
        
class SuspensionException(PostCoderException):
    """This account has been suspended."""
    def __init__(self, message):
        """The service is disabled when your account is suspended. \
        Please call 01508 494488 to re-activate your account."""
        message += __doc__
        PostCoderException.__init__(self, message)


class CreditsException(PostCoderException):
    """This account has too few credits to perform the search"""
    def __init__(self, message):
        """Your account is currently using credit packs and does not \
        have enough valid credits to perform the requested search. \
        Please add more credit packs to your account or change \
        your account to a pay monthly option."""
        message += __doc__
        PostCoderException.__init__(self, message)


class LicenseTException(PostCoderException):
    """Not licenced for a Thoroughfare level search."""
    def __init__(self, message):
        """You are not licenced to perform a Thoroughfare level search."""
        message += __doc__
        PostCoderException.__init__(self, message)


class LicensePException(PostCoderException):
    """Not licenced for a Premise level search."""
    def __init__(self, message):
        """You are not licenced to perform a Premise level search."""
        message += __doc__
        PostCoderException.__init__(self, message)
        

class LicensePGException(PostCoderException):
    """not licenced for a Postzon or Grids search."""
    def __init__(self, message):
        """You are not licenced to perform a Postzon or Grids search."""
        message += __doc__
        PostCoderException.__init__(self, message)
