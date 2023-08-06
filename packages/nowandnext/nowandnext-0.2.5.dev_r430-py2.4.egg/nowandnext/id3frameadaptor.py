"""
Given a set of key-val pairs provided by the textparser this class will transform it into a new 
mapping in which the keys are all ID3V2 frame names.
"""

class id3frameadaptor():
    
    @classmethod
    def adapt( cls, inputmapping ):
        return inputmapping