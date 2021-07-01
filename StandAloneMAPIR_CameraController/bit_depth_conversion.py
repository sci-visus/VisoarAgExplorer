def normalize(layer, max_pixel, min_pixel):
    return (layer - min_pixel) / (max_pixel - min_pixel)

def normalize_rgb(red, green, blue, max_pixel, min_pixel):
    red = normalize(red, max_pixel, min_pixel)
    green = normalize(green, max_pixel, min_pixel)
    blue = normalize(blue, max_pixel, min_pixel)
    return red, green, blue
