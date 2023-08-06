#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import string

#
# a simple utility function to pretty-print an index tuple into a [x,y] form string.
#

def indexToString(index):

   # if the input type is a string or an int, then this isn't a tuple!
   if isinstance(index, str) or isinstance(index, int):
      return "["+str(index)+"]"

   result = "["
   for i in range(0,len(index)):
      result += str(index[i])
      if i != len(index) - 1:
         result += ","
   result += "]"
   return result

#
# a simple utility to determine if a variable name contains an index specification.
# in other words, is the reference to a complete variable (e.g., "foo") - which may
# or may not be indexed - or a specific index or set of indices (e.g., "foo[1]" or
# or "foo[1,*]".
#

def isVariableNameIndexed(variable_name):

   left_bracket_count = variable_name.count('[')
   right_bracket_count = variable_name.count(']')

   if (left_bracket_count == 1) and (right_bracket_count == 1):
      return True
   elif (left_bracket_count == 1) or (right_bracket_count == 1):
      raise ValueError, "Illegally formed variable name="+variable_name+"; if indexed, variable names must contain matching left and right brackets"
   else:
      return False

#
# takes a string indexed of the form "('foo', 'bar')" and returns a proper tuple ('foo','bar')
#

def tupleizeIndexString(index_string):

   index_string=index_string.lstrip('(')
   index_string=index_string.rstrip(')')
   pieces = index_string.split(',')
   return_index = ()
   for piece in pieces:
      piece = string.strip(piece)
      piece = piece.lstrip('\'')
      piece = piece.rstrip('\'')
      transformed_component = None
      try:
         transformed_component = int(piece)
      except ValueError:
         transformed_component = piece
      return_index = return_index + (transformed_component,)

   # IMPT: if the tuple is a singleton, return the element itself.
   if len(return_index) == 1:
      return return_index[0]
   else:
      return return_index      

#
# related to above, extract the index from the variable name.
# will throw an exception if the variable name isn't indexed.
# the returned variable name is a string, while the returned
# index is a tuple. integer values are converted to integers
# if the conversion works!
#

def extractVariableNameAndIndex(variable_name):

   if isVariableNameIndexed(variable_name) is False:
      raise ValueError, "Non-indexed variable name passed to function extractVariableNameAndIndex()"

   pieces = variable_name.split('[')
   name = string.strip(pieces[0])
   full_index = pieces[1].rstrip(']')

   # even nested tuples in pyomo are "flattened" into
   # one-dimensional tuples. to accomplish flattening
   # replace all parens in the string with commas and
   # proceed with the split.
   full_index=string.translate(full_index, None, "()")
   indices = full_index.split(',')

   return_index = ()
   
   for index in indices:

      # unlikely, but strip white-space from the string.
      index=string.strip(index)

      # if the tuple contains nested tuples, then the nested
      # tuples have single quotes - "'" characters - around
      # strings. remove these, as otherwise you have an
      # illegal index.
      index=string.translate(index, None, "\'")

      # if the index is an integer, make it one!
      transformed_index = None
      try:
         transformed_index = int(index)
      except ValueError:
         transformed_index = index                  
      return_index = return_index + (transformed_index,)

   # IMPT: if the tuple is a singleton, return the element itself.
   if len(return_index) == 1:
      return name, return_index[0]
   else:
      return name, return_index

#
# determine if the input index is an instance of the template,
# which may or may not contain wildcards.
#

def indexMatchesTemplate(index, index_template):

   # if the input index is not a tuple, make it one.
   # ditto with the index template. one-dimensional
   # indices in pyomo are not tuples, but anything
   # else is. 

   if type(index) != tuple:
      index = (index,)
   if type(index_template) != tuple:
      index_template = (index_template,)

   if len(index) != len(index_template):
      return False

   for i in range(0,len(index_template)):
      if index_template[i] == '*':
         # anything matches
         pass
      else:
         if index_template[i] != index[i]:
            return False

   return True

#
# given a variable (the real object, not the name) and an index,
# "shotgun" the index and see which variable indices match the
# input index. the cardinality could be > 1 if slices are
# specified, e.g., [*,1].
#

def extractVariableIndices(variable, index_template):

   result = []

   for index in variable._index:

      if indexMatchesTemplate(index, index_template) is True:
         result.append(index)

   return result
