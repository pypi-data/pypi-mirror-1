def has_fatsyndication_support():
    try:
        import Products.fatsyndication
    except ImportError, e:
        return False
    return True

def has_atvideo_support():
    try:
        import Products.ATVideo
        return True
    except:
        return False

def has_blobfile_support():
    try:
        import Products.BlobFile
    except ImportError, e:
        return False
    return True
