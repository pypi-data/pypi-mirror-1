from interfaces import IOrderableFormFields
from zope.formlib.form import Fields
from zope.interface import implements

class OrderableFields(Fields):
    """Orderable collection of form fields."""
    implements(IOrderableFormFields)
    
    def moveField(self, name, direction=None, position=None, before=None,
                  after=None):
        """Moves a field called ``name`` to a new position based on the chosen
        parameter.
        
        """
        if name not in self.__FormFields_byname__:
            raise ValueError, "Field '%s' does not exist." % name
        
        if direction is not None:
            curpos = self.__FormFields_seq__.index(self.get(name))
            if direction.lower() == 'up':
                if curpos > 0 and curpos < len(self):
                    return self._moveToPosition(name, curpos-1)
                return
            elif direction.lower() == 'down':
                if curpos >= 0 and curpos < (len(self)-1):
                    return self._moveToPosition(name, curpos+1)
                return
            else:
                raise ValueError, "Direction must be either 'up' or 'down'."
        
        if position is not None:
            if str(position).lower() in ('top', 'first'):
                return self._moveToPosition(name, 0)
            elif str(position).lower() in ('bottom', 'last'):
                return self._moveToPosition(name, len(self)-1)
            else:
                position = int(position)
                if position >=0 and position < len(self):
                    return self._moveToPosition(name, position)
                else:
                    raise ValueError, "Invalid position: %d" % position
        
        if before is not None:
            if before not in self.__FormFields_byname__:
                raise ValueError, ("Can not move field '%s' before field '%s'. "
                                   "Field '%s' does not exist." % (name, before))
            if before == name:
                raise ValueError, "Can not move field '%s' before itself." % before
            before_pos = self.__FormFields_seq__.index(self.get(before))
            return self._moveToPosition(name, before_pos, compensate=True)
        
        if after is not None:
            if after not in self.__FormFields_byname__:
                raise ValueError, ("Can not move field '%s' after field '%s'. "
                                   "Field '%s' does not exist." % (name, after))
            if after == name:
                raise ValueError, "Can not move field '%s' after itself." % after
            after_pos = self.__FormFields_seq__.index(self.get(after))
            return self._moveToPosition(name, after_pos+1, compensate=True)

        raise TypeError, ("moveField() must to be given exactly one of the "
                          "following parameters: direction, position, before "
                          "or after.")

    def _moveToPosition(self, name, position, compensate=False):
        """Moves the field identified by ``name`` to a new position identified
        by ``position``. The ``position`` is relative to the current (yet to
        be modified) field order.
        """
        field = self.get(name)
        curpos = self.__FormFields_seq__.index(field)
        if curpos == position:
            return
        self.__FormFields_seq__.remove(field)
        if compensate and curpos < position:
            self.__FormFields_seq__.insert(position-1, field)
        else:
            self.__FormFields_seq__.insert(position, field)
