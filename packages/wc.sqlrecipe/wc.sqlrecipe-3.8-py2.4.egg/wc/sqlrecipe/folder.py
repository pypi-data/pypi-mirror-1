from zope.interface import implements
from z3c.zalchemy.container import SQLAlchemyContainer
from worldcookery.interfaces import IRecipeContainer

class RecipeFolder(SQLAlchemyContainer):
    implements(IRecipeContainer)

    def __init__(self):
        self.className = 'wc.sqlrecipe.recipe.Recipe'
