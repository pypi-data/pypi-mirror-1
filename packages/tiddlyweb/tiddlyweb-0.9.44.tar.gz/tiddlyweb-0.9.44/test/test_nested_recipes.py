"""
Test a recipe that includes a recipe in the recipe.
"""


from fixtures import _teststore

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe

def setup_module(module):
    module.store = _teststore()

def test_nested_recipe():
    bag_one = Bag('one')
    store.put(bag_one)
    bag_two = Bag('two')
    store.put(bag_two)
    recipe_one = Recipe('one')
    
