# $Id: rowaccess.py,v 1.1 2002/03/05 23:45:06 jribbens Exp $

import jon.wt as wt

class RowAccess(wt.TemplateCode):
  rowaccess_attrib = "row"

  def __getattr__(self, name):
    try:
      return getattr(self, self.rowaccess_attrib)[name]
    except KeyError:
      raise AttributeError, name
