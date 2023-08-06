# -*- coding: utf-8 -*-
from tests import msg
from uamobile import detect, Willcom

def test_useragent():
    def inner(useragent, name, vendor, model, model_version, browser_version, cache_size):
        ua = detect({'HTTP_USER_AGENT': useragent})

        assert ua.is_willcom()
        assert isinstance(ua, Willcom)
        assert ua.name == name
        assert ua.carrier == 'WILLCOM'
        assert ua.short_carrier == 'W'
        assert ua.vendor == vendor
        assert ua.model == model, ua.model
        assert ua.model_version == model_version, ua.model_version
        assert ua.browser_version == browser_version
        if cache_size is not None:
            assert ua.cache_size == cache_size
        else:
            assert ua.cache_size is None
        assert ua.display is not None
        assert ua.serialnumber is None
        assert ua.supports_cookie() == True

    for args in DATA:
        yield ([inner] + list(args))

#########################
# Test data
#########################

# ua, name, vendor, model, model_version, browser_version, cache_size
DATA = (('Mozilla/3.0(DDIPOCKET;JRC/AH-J3001V,AH-J3002V/1.0/0100/c50)CNF/2.0', 'WILLCOM', 'JRC', 'AH-J3001V,AH-J3002V', '1.0', '0100', 50),
        ('Mozilla/3.0(DDIPOCKET;KYOCERA/AH-K3001V/1.7.2.70.000000/0.1/C100) Opera 7.0', 'WILLCOM', 'KYOCERA', 'AH-K3001V', '1.7.2.70.000000', '0.1', 100),
        ('Mozilla/3.0(DDIPOCKET;JRC/AH-J3003S/1.0/0100/c50)CNF/2.0', 'WILLCOM', 'JRC', 'AH-J3003S', '1.0', '0100', 50),
        ('Mozilla/3.0(WILLCOM;SANYO/WX310SA/2;1/1/C128) NetFront/3.3,61.198.142.127', 'WILLCOM', 'SANYO', 'WX310SA', '2;1', '1', 128),

        # IE on W-zero3
        ('Mozilla/4.0 (compatible; MSIE 4.01; Windows CE; SHARP/WS007SH; PPC; 480x640)', 'WILLCOM', 'SHARP', 'WS007SH', '', '', None),

        # Opera on W-zero3
        ('Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; SHARP/WS007SH; PPC; 480x640) Opera 8.60 [ja]', 'WILLCOM', 'SHARP', 'WS007SH', '', '', None),
)
