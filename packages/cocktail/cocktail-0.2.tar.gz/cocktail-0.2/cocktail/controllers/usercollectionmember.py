#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from cocktail.schema import Member
from cocktail.controllers.usercollection import UserCollection


class UserCollectionMember(Member):

    type = UserCollection
    root_type = None
    edit_control = "cocktail.html.CollectionView"

    allow_type_selection = True
    allow_member_selection = True
    allow_language_selection = True
    allow_filters = True
    allow_sorting = True
    allow_grouping = True
    allow_paging = True

    def read_request_value(self, reader):
        
        user_collection = self.type(self.root_type)
        user_collection.params.prefix = self.name
        user_collection.params.source = reader.source
        
        user_collection.allow_type_selection = self.allow_type_selection
        user_collection.allow_member_selection = self.allow_member_selection
        user_collection.allow_language_selection = self.allow_language_selection
        user_collection.allow_filters = self.allow_filters
        user_collection.allow_sorting = self.allow_sorting
        user_collection.allow_grouping = self.allow_grouping
        user_collection.allow_paging = self.allow_paging

        return user_collection

