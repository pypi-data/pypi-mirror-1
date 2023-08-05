var displayShelfImages;
var displayShelfInited = false;

function insertDisplayShelf(width, height)
{
    document.write("<object id='flexApp' classid='clsid:D27CDB6E-AE6D-11cf-96B8-444553540000' codebase='http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=9,0,0,0' height='"+height+"' width='"+width+"'>");
    document.write("<param name='flashvars' value='bridgeName=displayshelf'/>");
    document.write("<param name='src' value='/tg_widgets/displayshelf/tg_displayshelf.swf'/>");
    document.write("<embed name='flexApp' pluginspage='http://www.macromedia.com/go/getflashplayer' src='/tg_widgets/displayshelf/tg_displayshelf.swf' height='"+height+"' width='"+width+"' flashvars='bridgeName=displayshelf'/>");
    document.write("</object>");
    FABridge.addInitializationCallback("displayshelf",init);
}

function showPhotos(a)
{
  displayShelfImages = a;
  if (displayShelfInited)
  {
    init();
  }
}

function init()
{
  displayShelfInited = true;
  var flexApp = FABridge.displayshelf.root();
  flexApp.setDataSet(displayShelfImages);
}
