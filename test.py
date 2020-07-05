import wx
from pytube import YouTube


def toString(stream) -> str:
    parts = str(stream.mime_type) + "_"
    if stream.includes_video_track:
        parts += str(stream.resolution)+"_" +str(stream.fps)+"fps"
        if not stream.is_adaptive:
            parts +="_" + str(stream.video_codec) + "_" + str(stream.audio_codec)
        else:
            parts += "_" + str(stream.video_codec)
    else:
        parts += str(stream.audio_codec)
    return parts

class YoutubeRipper( wx.Frame):

    def __init__(self, *args, **kwargs):
        super(YoutubeRipper, self).__init__(*args, **kwargs, size=(600,140))
        self.initUI()

    def progress(self, stream=None, chunk=None, bytes_remaining=None):
        if( bytes_remaining != None):
            percent = 100.0*(self.fileSize - bytes_remaining)/self.fileSize;
            self.progressBar.SetValue( int(percent) )

    def initUI(self):
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileItem = fileMenu.Append(wx.ID_EXIT, "Quit", "quit YoutubeRipper");
        menuBar.Append(fileMenu,"&File")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.onQuit, fileItem)

        panel = wx.Panel(self)
        grid_bag = wx.GridBagSizer(3,5)

        #link line

        label_link = wx.StaticText(panel, label="Youtube Link")
        self.text_link = wx.TextCtrl(panel)
        self.text_link.Bind(wx.EVT_TEXT, self.onTextLink)
        self.button_link= wx.Button(panel,wx.ID_ANY,label="Load")
        self.button_link.Disable()
        self.button_link.Bind(wx.EVT_BUTTON, self.onLoad)

        grid_bag.Add(label_link,pos=(0,0), flag=wx.LEFT)
        grid_bag.Add(self.text_link,pos=(0,1), span=(1,3),flag=wx.EXPAND)
        grid_bag.Add(self.button_link,pos=(0,4),flag=wx.RIGHT)
        # streams line

        label_stream = wx.StaticText(panel,label="Stream")
        self.combo_stream = wx.ComboBox(panel,style=wx.CB_READONLY)
        self.combo_stream.Bind(wx.EVT_COMBOBOX, self.onSelection)
        self.button_stream = wx.Button(panel,label="Download")
        self.button_stream.Bind(wx.EVT_BUTTON, self.onDownload)
        self.combo_stream.Disable()
        self.button_stream.Disable()

        grid_bag.Add(label_stream,pos=(1,0), flag=wx.LEFT)
        grid_bag.Add(self.combo_stream,pos=(1,1),span=(1,3),flag=wx.EXPAND)
        grid_bag.Add(self.button_stream,pos=(1,4),flag=wx.RIGHT)

        self.progressBar = wx.Gauge(panel)
        grid_bag.Add(self.progressBar,pos=(2,0),span= (1,5),flag=wx.EXPAND)
        grid_bag.AddGrowableCol(1,1)
        panel.SetSizer( grid_bag)

    def onLoad(self, event):
        link = self.text_link.GetValue()
        print("load :",link)
        self.yt = YouTube(link)
        print( self.yt.title)
        self.streams = self.yt.streams
        for s in self.streams:
            self.combo_stream.Append(toString(s),s )
        self.combo_stream.Enable()
        self.combo_stream.SetSelection(0)
        print(self.yt.streams)

    def onDownload(self, event):
        print("download")
        pos = self.combo_stream.GetSelection()
        stream = self.combo_stream.GetClientData(pos)
        with wx.FileDialog(self, "Save file", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind
            self.fileSize= stream.filesize
            self.yt.register_on_progress_callback( self.progress)
            stream.download( fileDialog.GetDirectory(), filename=fileDialog.GetFilename()  )
        self.progressBar.SetValue(0)

    def onSelection(self,event):
        self.button_stream.Enable()

    def onQuit(self, e):
        self.Close()

    def onTextLink(self, event):
        link = event.GetString()
        if( len(link) > 0 ):
            self.button_link.Enable()
        else:
            self.button_link.Disable()

def main():
    app =wx.App()
    ripper = YoutubeRipper(None)
    ripper.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
