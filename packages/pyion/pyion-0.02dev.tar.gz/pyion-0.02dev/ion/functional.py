def tagfunc (f, **kwargs):
    """ allows a function to be called
        with defaults filled in by tags table,
	
	eg 
	gaussBlur (image, 'rle huge') 
	-> (gaussBlur (image, mode = rle, hradius = 100, vradius = 100))
	
	or 
	gaussBlur (image, 'rle huge', hradius = 50)
	-> (gaussBlur (image, mode = rle, hradius = 50, vradius = 100))

	or
	gaussBlur (image, hradius = 50, how = 'rle huge')
	-> (gaussBlur (image, mode = rle, hradius = 50, vradius = 100))
	
	"""
    def f (*args, **kwargs):
        pass
