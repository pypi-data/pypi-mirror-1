from handlers.custom import marscategory
from handlers.custom import marscoordinates 
CUSTOMHANDLERS={"marsapp.categories.field.MarscatField": {'handler_class' : marscategory.CSVMarsCat(), 'file' : False},
                "marsapp.content.schemata.field.CoordinatesField": {'handler_class' : marscoordinates.CSVMarsCoordinates(), 'file' : False},
                }