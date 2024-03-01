from enum import Enum, EnumMeta, unique

class ImgExtensionMeta(EnumMeta):  
    def __getitem__(self, name):
        try:
            name = super().__getitem__(name)
            return name.value
        except (TypeError, KeyError) as error:
            return
    
@unique
class ImgExtension(Enum, metaclass=ImgExtensionMeta):
    bmpbmp = 'bmpbmp'
    ecw = 'ecw'
    gif = 'gif'
    ico = 'ico'
    ilbm = 'ilbm'
    jpeg = 'jpeg'
    jpg = 'jpg'
    jpeg2000 = 'jpeg2000'
    mrsid = 'mrsid'
    pcx = 'pcx'
    png = 'png'
    psd = 'psd'
    tga = 'tga'
    tiff = 'tiff'
    jfif = 'jfif'
    hdphoto = 'hdphoto'
    webp = 'webp'
    xbm = 'xbm'
    xps = 'xps'
    rla = 'rla'
    rpf = 'rpf'
    pnm = 'pnm'
    
    
img_extension = ImgExtension