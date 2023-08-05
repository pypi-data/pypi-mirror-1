from zope.interface import implements
from worldcookery.interfaces import IRecipe
from rwproperty import getproperty, setproperty

class Recipe(object):
    implements(IRecipe)

    __name__ = __parent__ = None

    name = u''
    time_to_cook = 0
    description = u''

    @getproperty
    def ingredients(self):
        return [item.name for item in self._ingredients]

    @setproperty
    def ingredients(self, new):
        # rebuild the list of Ingredient objects by reusing existing objects
        # if possible and only creating new ones if they don't exist yet.
        existing = dict((item.name, item) for item in self._ingredients)
        self._ingredients = [existing.get(name, Ingredient(name))
                             for name in new]

    @getproperty
    def tools(self):
        return [item.name for item in self._tools]

    @setproperty
    def tools(self, new):
        # rebuild the list of KitchenTool objects by reusing existing objects
        # if possible and only creating new ones if they don't exist yet.
        existing = dict((item.name, item) for item in self._tools)
        self._tools = [existing.get(name, KitchenTool(name)) for name in new]

class Ingredient(object):

    def __init__(self, name):
        self.name = name

class KitchenTool(object):

    def __init__(self, name):
        self.name = name

from zope.component.factory import Factory

recipeFactory = Factory(
    Recipe,
    title=u"Create a new recipe",
    description = u"This factory instantiates new recipes."
    )

import sqlalchemy
import z3c.zalchemy

recipe_table = sqlalchemy.Table(
    'recipes',
    z3c.zalchemy.metadata('WorldCookery'),
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.Unicode),
    sqlalchemy.Column('time_to_cook', sqlalchemy.Integer),
    sqlalchemy.Column('description', sqlalchemy.Unicode)
    )

ingredient_table = sqlalchemy.Table(
    'ingredients',
    z3c.zalchemy.metadata('WorldCookery'), 
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('recipe_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('recipes.id')),
    sqlalchemy.Column('name', sqlalchemy.Unicode),
    )

tool_table = sqlalchemy.Table(
    'tools',
    z3c.zalchemy.metadata('WorldCookery'), 
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('recipe_id', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('recipes.id')),
    sqlalchemy.Column('name', sqlalchemy.Unicode),
    )

z3c.zalchemy.createTable('recipes', 'WorldCookery')
z3c.zalchemy.createTable('ingredients', 'WorldCookery')
z3c.zalchemy.createTable('tools', 'WorldCookery')
sqlalchemy.mapper(Ingredient, ingredient_table)
sqlalchemy.mapper(KitchenTool, tool_table)
sqlalchemy.mapper(Recipe, recipe_table,
                  properties={
    '_ingredients': sqlalchemy.relation(Ingredient,
                                        cascade="all, delete-orphan"),
    '_tools': sqlalchemy.relation(KitchenTool, cascade="all, delete-orphan"),
    })
