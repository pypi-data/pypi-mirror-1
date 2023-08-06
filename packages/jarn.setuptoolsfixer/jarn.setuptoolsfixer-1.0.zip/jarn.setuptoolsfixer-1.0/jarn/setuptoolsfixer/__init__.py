import httplib
from setuptools.package_index import PackageIndex

def extension(buildout=None):
    _old_open_url = getattr(PackageIndex, '_jarn_old_open_url', None)
    if _old_open_url is not None:
        return
    _old_open_url = PackageIndex.open_url
    def open_url(self, url, warning=None):
        try:
            return _old_open_url(self, url, warning=warning)
        except httplib.HTTPException, v:
            if warning: self.warn(warning, v)
            else:
                raise DistutilsError("Download error for %s: %s"
                                     % (url, v))
    PackageIndex._jarn_old_open_url = _old_open_url
    PackageIndex.open_url = open_url
