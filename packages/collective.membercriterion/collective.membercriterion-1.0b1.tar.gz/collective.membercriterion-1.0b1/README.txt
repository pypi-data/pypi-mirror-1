Introduction
============

This package adds a new criteria type for the Collection type (aka Topic). By
default, the crtieria is available for the 'Categories' (aka Subject) index,
but it could be enabled for most index types.

When added to a collection, the criteria is configured with a member property
that will be used to find content. The member property is based on the
properties of the current user, although it is unlikely that other users
will have different properties.

When the collection is viewed, this criteria will search for content where
the index matches the value of the member property for the current user.

The original use case for this functionality was to find content the user may
be interested in: the user specifies a list of "interesting" keywords in his
profile. The collection is used to show content matching his interests.