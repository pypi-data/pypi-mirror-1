import Globals

def pdb(self):
    if Globals.DevelopmentMode:
        import pdb;pdb.set_trace()