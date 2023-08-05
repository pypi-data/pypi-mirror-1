UseDefaultValue = object()

class IntPrompter:
    """ Demo prompter

    Ask for an integer with a certain range of legal values.
    """
    
    def __init__(self,min=None,max=None):
        self.min = min
        self.max = max
    def prompt(self,varname):
        while 1:
            
            i = raw_input("give an int (min=%s, max=%s) for %s: " % (
                self.min,self.max,varname))
            try:
                val =  int(i)
            except ValueError:
                print "You should enter a legal integer!"
            if (self.min == None or val >=self.min) and (
                self.max == None or val <=self.max):
                
                return val
            print "The integer should be in specified range!"
            
    def __repr__(self):
        return '<int prompter>'

class ListPrompter:
    """ ask for a list of strings"""
    
    def prompt(self,varname):
        print "Entering an array '%s'; end by entering '.' on the line alone" % varname
        l = []
        i = 0 
        while 1:
            s = raw_input("%s[ %s ] := " % (varname,i))
            if not s:
                continue
            if s==".":
                return l
            l.append(s)
            i+=1
        return l
    def __repr__(self):
        return "<list prompter>"

class DefaultPrompter:
    def prompt(self,varname):
        choice = raw_input("%s: " % varname)
        if choice == '-':
            return UseDefaultValue
        return choice
        
    

# various 'qualifiers' to prevent warnings when using the qualifier in
# the place where prompter should be (immediately after the var
# list). It's a good practice to assign qualifiers to None, because
# it's Yet Another Object that has no 'prompt' attribute ->
# DefaultPrompter is selected.

once = None
