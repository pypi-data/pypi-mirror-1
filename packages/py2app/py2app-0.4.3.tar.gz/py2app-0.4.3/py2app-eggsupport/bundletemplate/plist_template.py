import sys
import py2app
from distutils import sysconfig

__all__ = ['infoPlistDict']

def infoPlistDict(CFBundleExecutable, plist={}):
    frameworkName = sysconfig.get_config_var('PYTHONFRAMEWORK', 'Python')
    CFBundleExecutable = unicode(CFBundleExecutable)
    NSPrincipalClass = u''.join(CFBundleExecutable.split())
    version = sys.version[:3]
    pdict = dict(
        CFBundleDevelopmentRegion=u'English',
        CFBundleDisplayName=plist.get('CFBundleName', CFBundleExecutable),
        CFBundleExecutable=CFBundleExecutable,
        CFBundleIconFile=CFBundleExecutable,
        CFBundleIdentifier=u'org.pythonmac.unspecified.%s' % (NSPrincipalClass,),
        CFBundleInfoDictionaryVersion=u'6.0',
        CFBundleName=CFBundleExecutable,
        CFBundlePackageType=u'BNDL',
        CFBundleShortVersionString=plist.get('CFBundleVersion', u'0.0'),
        CFBundleSignature=u'????',
        CFBundleVersion=u'0.0',
        LSHasLocalizedDisplayName=False,
        NSAppleScriptEnabled=False,
        NSHumanReadableCopyright=u'Copyright not specified',
        NSMainNibFile=u'MainMenu',
        NSPrincipalClass=NSPrincipalClass,
        PyMainFileNames=[u'__boot__'],
        PyResourcePackages=[ (s % version) for s in [
            u'lib/python%s',
            u'lib/python%s/lib-dynload',
            u'lib/python%s/site-packages.zip',
        ]],
        PyRuntimeLocations=[(s % dict(framework=frameworkName, version=version)) for s in [
            u'@executable_path/../Frameworks/%(framework)s.framework/Versions/%(version)s/%(framework)s',
            u'~/Library/Frameworks/%(framework)s.framework/Versions/%(version)s/%(framework)s',
            u'/Library/Frameworks/%(framework)s.framework/Versions/%(version)s/%(framework)s',
            u'/Network/Library/Frameworks/%(framework)s.framework/Versions/%(version)s/%(framework)s',
            u'/System/Library/Frameworks/%(framework)s.framework/Versions/%(version)s/%(framework)s',
        ]],
    )
    pdict.update(plist)
    pythonInfo = pdict.setdefault(u'PythonInfoDict', {})
    pythonInfo.update(dict(
        PythonLongVersion=unicode(sys.version),
        PythonShortVersion=unicode(sys.version[:3]),
        PythonExecutable=unicode(sys.executable),
    ))
    py2appInfo = pythonInfo.setdefault(u'py2app', {}).update(dict(
        version=unicode(py2app.__version__),
        template=u'bundle',
    ))
    return pdict
