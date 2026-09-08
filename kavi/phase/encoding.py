"""Lossless input framing. These supplied codecs do not learn representations."""


def text_events(text):
    """Stream Unicode code points, preserving case, whitespace and punctuation."""
    if not isinstance(text, str):
        raise TypeError('Text input must be a string')
    yield 'text:begin'
    for character in text:
        yield 'text:U+%06X' % ord(character)
    yield 'text:end'


def gray_events(width, height, pixels):
    """Frame row-major grayscale pixels without conflating text and image ports.

    Consuming this iterator can fail on malformed input; callers must abort the
    invocation on that failure. Framing is not image recognition or visualization.
    """
    if type(width) is not int or type(height) is not int or not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise ValueError('Invalid grayscale dimensions')
    yield 'gray:begin'
    yield f'gray:width:{width}'
    yield f'gray:height:{height}'
    iterator = iter(pixels)
    for _ in range(height):
        yield 'gray:row'
        for _ in range(width):
            value = next(iterator, None)
            if type(value) is not int or not 0 <= value <= 255:
                raise ValueError('Missing or invalid grayscale pixel')
            yield f'gray:value:{value}'
    sentinel = object()
    if next(iterator, sentinel) is not sentinel:
        raise ValueError('Extra grayscale pixels')
    yield 'gray:end'
