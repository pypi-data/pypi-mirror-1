""" FSDump product intialization

$Id: __init__.py 97104 2009-02-22 16:36:11Z tseaver $
"""
import Dumper

def initialize( context ):

    context.registerClass( Dumper.Dumper
                         , constructors= ( ( 'addDumperForm'
                                           , Dumper.addDumperForm
                                           )
                                         , Dumper.addDumper
                                         )
                         , permission= 'Add Dumper'
                         , icon='www/dumper.gif'
                         )

    context.registerHelpTitle( 'FSDump Help' )
    context.registerHelp( directory='help' )
