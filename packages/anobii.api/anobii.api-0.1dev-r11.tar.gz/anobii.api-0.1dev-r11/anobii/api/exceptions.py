'''Exceptions used by the AnobiiAPI module.'''

class IllegalArgumentException(ValueError):
    '''Raised when a method is passed an illegal argument.
    
    More specific details will be included in the exception message
    when thrown.
    '''

class AnobiiError(Exception):
    '''Raised when a Anobii method fails.
    
    More specific details will be included in the exception message
    when thrown.
    '''
