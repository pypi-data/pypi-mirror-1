'''
A drop-in replacement for optparse ( "import optparse_gui as optparse" )
Provides an identical interface to optparse(.OptionParser),
But displays an automatically generated wx dialog in order to enter the 
options/args, instead of parsing command line arguments
'''

import sys
import re
import optparse

import wx

__version__ = 0.1
__revision__ = '$Id: __init__.py 4 2008-03-08 12:13:06Z slider.fry $'

class OptparseDialog( wx.Dialog ):
    '''The dialog presented to the user with dynamically generated controls,
    to fill in the required options.
    Based on the wx.Dialog sample from wx Docs & Demos'''
    def __init__(
            self,
            option_parser, #The OptionParser object
            parent = None, 
            ID = 0, 
            title = 'Optparse Dialog', 
            pos=wx.DefaultPosition, 
            size=wx.DefaultSize, 
            style=wx.DEFAULT_DIALOG_STYLE,
            name = 'OptparseDialog',
        ):
        
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)
        
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.option_controls = {}
        
        top_label_text = '%s %s' % ( option_parser.get_prog_name(), 
                                     option_parser.get_version() )
        label = wx.StaticText(self, -1, top_label_text)
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        # Add controls for all the options
        for option in option_parser.option_list:
            if option.dest is None:
                continue
            
            if option.help is None:
                option.help = u''

            box = wx.BoxSizer(wx.HORIZONTAL)
            if 'store' == option.action:
                label = wx.StaticText(self, -1, option.dest )
                label.SetHelpText( option.help )
                box.Add( label, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
                
                if 'choice' == option.type:
                    if optparse.NO_DEFAULT == option.default:
                        option.default = option.choices[0]
                    ctrl = wx.ComboBox( 
                        self, -1, choices = option.choices,
                        value = option.default,
                        style = wx.CB_DROPDOWN | wx.CB_READONLY | wx.CB_SORT 
                    )
                else:
                    ctrl = wx.TextCtrl( self, -1, "", size=(300,-1) )
                    if option.default != optparse.NO_DEFAULT:
                        ctrl.Value = str( option.default )
                        
                box.Add( ctrl, 1, wx.ALIGN_CENTRE|wx.ALL, 5 )
            elif option.action in ( 'store_true', 'store_false' ):
                ctrl = wx.CheckBox( self, -1, option.dest, size = ( 300, -1 ) )
                box.Add( ctrl, 0, wx.ALIGN_CENTRE|wx.ALL, 5 )
                
            ctrl.SetHelpText( option.help )
            sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)      
            
            self.option_controls[ option ] = ctrl

        # Add a text control for entering args
        box = wx.BoxSizer( wx.HORIZONTAL )
        label = wx.StaticText(self, -1, 'args' )
        label.SetHelpText( 'This is the place to enter the args' )
        
        self.args_ctrl = wx.TextCtrl( self, -1, '', size = ( -1, 100 ), 
                            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER )
        self.args_ctrl.SetHelpText( 
'''Args can either be separated by a space or a newline
Args the contain spaces must be entered like so: "arg with sapce" 
'''
        )
        box.Add( label, 0, wx.ALIGN_CENTRE | wx.ALL, 5 )
        box.Add( self.args_ctrl, 1, wx.ALIGN_CENTRE | wx.ALL, 5 )
        
        sizer.Add( box , 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def _getOptions( self ):
        option_values = {}
        for option, ctrl in self.option_controls.iteritems():
            option_values[option] = ctrl.Value
        
        return option_values

    def _getArgs( self ):
        args_buff = self.args_ctrl.Value
        args = re.findall( r'(?:((?:(?:\w|\d)+)|".*?"))\s*', args_buff )
        return args

    def getOptionsAndArgs( self ):
        '''Returns the tuple ( options, args )
        options -  a dictionary of option names and values
        args - a sequence of args'''
        
        option_values = self._getOptions()
        args = self._getArgs()
        return option_values, args

class UserCancelledError( Exception ):
    pass

class OptionParser( optparse.OptionParser ):
    SUPER = optparse.OptionParser
    
    def __init__( self, *args, **kwargs ):
        if wx.GetApp() is None:
            self.app = wx.App( False )
            
        self.SUPER.__init__( self, *args, **kwargs )
    
    def parse_args( self, args = None, values = None ):
        '''
        This is the heart of it all - overrides optparse.OptionParser.parse_args
        @param arg is irrelevant and thus ignored, 
               it's here only for interface compatibility
        '''
        
        dlg = OptparseDialog( option_parser = self )
        dlg_result = dlg.ShowModal()
        if wx.ID_OK != dlg_result:
            raise UserCancelledError( 'User has canceled' )
        
        if values is None:
            values = self.get_default_values()
            
        option_values, args = dlg.getOptionsAndArgs()
         
        for option, value in option_values.iteritems():
            if ( 'store_true' == option.action ) and ( value is False ):
                setattr( values, option.dest, False )
                continue
            if ( 'store_false' == option.action ) and ( value is True ):
                setattr( values, option.dest, False )
                continue
            
            if option.takes_value() is False:
                value = None

            option.process( option, value, values, self )
        
        return values, args

    def error( self, msg ):
        wx.MessageDialog( 0, msg, 'Error!', wx.ICON_ERROR )
        return self.SUPER.error( self, msg )
    
################################################################################

def sample_parse_args():
    usage = "usage: %prog [options] args"
    if 1 == len( sys.argv ):
        option_parser_class = OptionParser
    else:
        option_parser_class = optparse.OptionParser
        
    parser = option_parser_class( usage = usage, version='0.1' )
    parser.add_option("-f", "--file", dest="filename", default = r'c:\1.txt',
                      help="read data from FILENAME")
    parser.add_option("-a", "--action", dest="action",
                      choices = ['delete', 'copy', 'move'],
                      help="Which action do you wish to take?!")
    parser.add_option("-n", "--number", dest="number", default = 23,
                      type = 'int',
                      help="Just a number")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose")
    
    (options, args) = parser.parse_args()
    return options, args

def main():
    options, args = sample_parse_args()
    print 'args: %s' % repr( args )
    print 'options: %s' % repr( options )
    
if '__main__' == __name__:
    main()
