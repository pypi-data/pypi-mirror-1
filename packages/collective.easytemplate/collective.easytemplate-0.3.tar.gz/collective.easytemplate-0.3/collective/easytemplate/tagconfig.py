"""

    Maintain list of custom template tags.
    
    Just import & add new tags to this dictionary.
    
"""

from collective.easytemplate.tags.listfolder import list_folder

tags = {
        "list_folder" : list_folder
}