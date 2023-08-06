from zope.interface import Interface


class IChecklist(Interface):
    
    def getId():
        """ """
        
    def setId():
        """ """
        
    def Title():
        """ """
        
    def Description():
        """ """
        
    def setDescription():
        """ """
            
    def getCheckedItems():
        """ """
    
    def setCheckedItems():
        """ """
    
    def getAllItems():
        """ """
    
    def setAllItems():
        """ """
    
    def getCheckedManagerItems():
        """ """
    
    def setCheckedManagerItems():
        """ """
    
    def getAllManagerItems():
        """ """
    
    def setAllManagerItems():
        """ """
    
